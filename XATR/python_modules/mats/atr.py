# DISTRIBUTION STATEMENT D. Distribution authorized to the Department of
# Defense and U.S. DoD contractors only; Administrative or Operational Use; 1
# Jan 2017. Other U.S. requests shall be referred to Naval Surface Warfare
# Center Panama City Division, ATTN: Technical Director NSWC PCD, 110 Vernon
# Ave, Panama City, FL 32407.
"""
mats.atr
--------

This submodule provides functions for execution of an ATR configuration or parts
thereof. For these functions to execute correctly, the configure function must
be executed first, which does setup and initialization of modules utilized by
the other submodule functions.
"""
import os.path as osp
import math
import traceback

from mats import (ContactList, EcdataList)
import mats.pkg
import mats.core
import mats.sensor
import mats.log
import mats.filesystem
import mats.cfg
import mats.time
import mats.uuid
from timeit import default_timer as timer
from datetime import datetime
import sklearn.metrics


UNIT_TEST = False
atrcfg_ = None
detector_ = None
classifier_ = None
features_ = []
normalizer_ = None
sensor_ = None


def configure(cfg) -> None:
    """
    Configure ATR processing stream.

    :param cfg: Configuration for ATR.
    :type cfg: mats.AtrConfig
    """
    global atrcfg_, detector_, classifier_, features_, normalizer_, sensor_

    # - Get list of needed modules from atrconfig
    # - Create and configure each interface and module
    atrcfg_ = cfg
    mats.pkg.scan()

    # Sensor
    sensor_ = mats.sensor.mats_sensor(cfg.sensor)
    if not sensor_:
        raise RuntimeError('Sensor module assignment failed.')

    # Detector
    det_mod = cfg['detector_module']
    det_cfg = cfg['det_cfg']
    detector_ = mats.pkg.create(det_mod['name'])
    if not detector_:
        raise RuntimeError("Detector module assignment failed.")
    detector_.configure(det_cfg)

    # Normalizer
    norm_mod = cfg['normalizer_module']
    norm_cfg = cfg['norm_cfg']
    normalizer_ = mats.pkg.create(norm_mod['name'])
    if not normalizer_:
        raise RuntimeError("Normalizer module assignment failed.")
    normalizer_.configure(norm_cfg)

    # Features
    feat_mods = cfg['feat_modules']
    features_ = []
    for k in range(len(feat_mods)):
        feat_cfg = cfg.feature_config(k)
        feat = mats.pkg.create(feat_mods[k]['name'])
        if not feat:
            raise RuntimeError('Feature module creation failure.')
        feat.configure(feat_cfg)
        features_.append(feat)

    # Classifier
    cls_mod = cfg['classifier_module']
    cls_cfg = cfg['cls_cfg']
    classifier_ = mats.pkg.create(cls_mod['name'])
    if not classifier_:
        raise RuntimeError("Classifier module assignment failed.")
    classifier_.configure(cls_cfg)


def process(inp, gt=None):
    """
    Process sonar data through the entire Python processing stream.

    :param inp: Input object
    :type inp: mats.Input
    :param gt: Ground truth (optional)
    :type gt: [dict] or None
    :returns: Lists of contacts and ecdata
    :rtype: (mats.ContactList, mats.EcdataList)
    :raises RuntimeError: On processing failure
    """
    try:
        con = ContactList()
        ecd = EcdataList()
        print('Processing File: {}, Side: {}'.format(inp['filename'],
                                                     inp['side']))

        if not inp['data_names']:
            return con, ecd

        # Find bad regions -----------------------------------------------------
        bad_regions = mats.core.data_integ_verif_phase(inp)

        # Normalize good regions of the image ----------------------------------
        normalize_images_good_regions(inp, bad_regions)

        # Get detections for each chunk ----------------------------------------
        print("Chunking/Detection phase starting.")

        start_detector = timer()
        con, ecd = atr_chunking_wrapper_c(inp, bad_regions)
        end_detector = timer()
        print(f"Chunking/Detection phase complete. time: "
              f"{end_detector - start_detector}s")

        print("{} contacts generated".format(len(con)))
        if len(con) == 0:
            return con, ecd

        start_conecd = timer()
        # Fill in remaining contact/ecdata information
        for k in range(len(con)):
            # Info from input
            mats.core.detsub_contact_fill(inp, con[k], ecd[k])

            # Module names
            con[k]['normalizer'] = atrcfg_['normalizer']
            con[k]['detector'] = atrcfg_['detector']
            con[k]['classifier'] = atrcfg_['classifier']
            con[k]['contcorr'] = ''

        # Sort contacts --------------------------------------------------------
        mats.core.sort_contacts(con, ecd)

        # Label contacts -------------------------------------------------------
        for k in range(len(con)):
            # Add ID field to data structures
            con[k]['id'] = k + 1
            ecd[k]['id'] = k + 1

        end_conecd = timer()
        print(f'detsub fill time: {end_conecd - start_conecd}s')

        # Run feature modules --------------------------------------------------
        print("Feature phase starting.")
        start_feature = timer()
        feature(con, ecd)
        end_feature = timer()
        print(f"Feature phase complete. time: {end_feature - start_feature}")

        # Normalize features ---------------------------------------------------
        print("Feature normalization phase starting.")
        feat_norm = atrcfg_.feat_norm
        for k in range(len(con)):
            feat = con[k]['features']
            if not (len(feat) == atrcfg_['feat_len']+atrcfg_['det_feat_len']):
                print(f"Unexpected feature vector length. contact[{k}]: "
                      f"Feature length {feat.shape[0]} (expected "
                      f"{atrcfg_['feat_len']}).")
                return con, ecd
            con[k]['features'] = (feat - feat_norm[0, :]) / feat_norm[1, :]
        print("Feature normalization phase complete.")

        # Check if test classifier. If yes, run ground truther early -----------
        ran_gt_flag = False
        if hasattr(classifier_, 'TEST_MODULE'):
            if classifier_.TEST_MODULE is True:
                if gt is not None:
                    gt_contact_list(inp, gt, con)
                    ran_gt_flag = True

        # Run Classifier -------------------------------------------------------
        print("Classification phase starting.")
        start_class = timer()
        classify(con, ecd)
        end_class = timer()
        print(f"Classification phase complete. time: {end_class - start_class}")

        # Run Ground Truther ---------------------------------------------------
        if ran_gt_flag is False:
            if gt is not None:
                gt_contact_list(inp, gt, con)
            else:
                print('No GT specified, skipping step ...')

        return con, ecd
    except RuntimeError:
        msg = traceback.format_exc()
        mats.log.error('Python processing stream failed: '+msg)


def gt_contact_list(ins, gt, con):
    """
    Apply ground truth to a contact list.

    :param ins: Input object for a particular image
    :type ins: mats.Input
    :param gt: Ground truth information for this image
    :type gt: [dict]
    :param con: Contact list for this image
    :type con: mats.ContactList
    """
    start_gt = timer()
    mats.core.gt_contact_list(ins, gt, con)
    end_gt = timer()
    gt_time = end_gt - start_gt
    print(f'gt label time: {gt_time}s')


def normalize_images_good_regions(inp, bad_regions):
    """
    Normalize good regions of data.

    :param inp: Data to be processed.
    :type inp: mats.Input
    :param bad_regions: List of bad regions.  Each region is described by a
        dict with the following fields:

      - start: Starting along-track index of bad region.
      - end: Ending along-track index of bad region.
      - reason: String describing why the region is bad.
    :type bad_regions: [dict]
    """
    data_list = inp['data_names']
    if not data_list:
        raise RuntimeError("Input has no data.")

    # Determine desired anum (des_y) for each segment.
    refanum, refcnum = inp.data(inp['ref_name']).size()
    refares = inp.data(inp['ref_name']).ares
    refcres = inp.data(inp['ref_name']).cres
    des_y = min(math.floor(refcnum * refcres / refares), refanum)

    for band in data_list:
        anum, cnum = inp.data(band).size()
        y_mult = refanum / anum
        des_y = math.floor(des_y / y_mult) * y_mult

    # Split image into segments using des_y.
    segments = mats.core.calc_good_segments(bad_regions, refanum, des_y)
    for n in range(len(segments['y_starts'])):
        chunk = mats.core.input_chunk(inp, segments['y_starts'][n],
                                      segments['y_ends'][n])
        normalize(chunk)
        mats.core.input_chunk_apply(chunk, segments['y_starts'][n],
                                    segments['y_ends'][n], inp)
    return


def normalize(inp) -> None:
    """
    Executes configured normalizer module on data. Input data is modified.

    :param inp: Data to be processed.
    :type inp: mats.Input
    :raise RuntimeError: No normalizer module has been configured.
    """
    global normalizer_
    if not normalizer_:
        raise RuntimeError('No normalizer module loaded')
    return normalizer_.normalize(inp)


def detect(inp):
    """
    Detect regions of interest.

    :param inp: Data to be processed.
    :type inp: mats.Input
    :returns: Lists of contacts and ecdata
    :rtype: (mats.ContactList, mats.EcdataList)
    :raise RuntimeError: If no detector module has been configured.
    """
    global detector_
    if not detector_:
        raise RuntimeError('No detector module loaded')
    return detector_.detect(inp)


def feature(contacts, ecdata):
    """
    Compute features for regions of interest.

    :param contacts: List of contacts
    :type contacts: mats.ContactList
    :param ecdata: List of extra contact data
    :type ecdata: mats.EcdataList
    :raise RuntimeError: If no feature module has been configured.
    """
    global features_
    for feat in features_:
        if not feat:
            raise RuntimeError('No feature module loaded')
        feat.feature(contacts, ecdata)


def classify(contacts, ecdata):
    """
    Classify regions of interest.

    :param contacts: List of contacts
    :type contacts: mats.ContactList
    :param ecdata: List of extra contact data
    :type ecdata: mats.EcdataList
    :raise RuntimeError: If no classifier module has been configured.
    """
    global classifier_
    if not classifier_:
        raise RuntimeError('No classifier module loaded')
    return classifier_.classify(contacts, ecdata)


def atr_chunking_wrapper_c(inp, bad_regions):
    """
    Chunk sonar data and detect regions of interest.

    A large image is broken down into a set of smaller sub-images that
    overlap slightly in the track dimension.  Known bad regions are avoided.
    The resulting contacts from each sub-image is then consolidated into
    a single, combined list for the entire image as a whole.
    
    :param inp: Input object
    :type inp: mats.Input
    :param bad_regions: List of bad regions.  Each region is described by a
        dict with the following fields:

      - start: Starting along-track index of bad region.
      - end: Ending along-track index of bad region.
      - reason: String describing why the region is bad.
    :type bad_regions: [dict]
    :returns: Lists of contacts and ecdata
    :rtype: (mats.ContactList, mats.EcdataList)
    """
    contacts = ContactList()
    ecdata = EcdataList()
    chunk = mats.core.calc_image_partitions(inp, bad_regions)

    # Run chunking
    if len(chunk['y_starts']) == 0:
        return contacts, ecdata
    elif len(chunk['y_starts']) == 1:
        calc_sweetspot(inp)
        ss = inp['sweetspot']
        print('SweetSpot: [{}, {}]'.format(ss[0], ss[1]))

        # Not big enough for chunking; just use existing input
        contacts, ecdata = detect(inp)
    else:
        # Process each data chunk
        for c in range(len(chunk['y_starts'])):
            print('CHUNK {}'.format(c))
            # Detector on this chunk of data
            in_chunk = mats.core.input_chunk(inp, chunk['y_starts'][c],
                                             chunk['y_ends'][c])
            con, ecd = detect(in_chunk)

            # Shift contact coordinates back to original frame
            for q in range(len(con)):
                con[q]['x'] += chunk['x_starts'][c]
                con[q]['y'] += chunk['y_starts'][c]
                contacts.append(con[q])
                ecdata.append(ecd[q])

        # Group contacts, prune duplicate contacts, recenter.
        # In keeping with MATS atr_chunking_wrapper(), this is only done when
        # the input was chunked.
        # print("Grouping, pruning, and recentering contacts.")
        mats.core.group_contacts(inp, contacts, ecdata)
        mats.core.prune_duplicate_contacts(contacts, ecdata)

    for con in contacts:
        tempX = con['x']
        tempY = con['y']
        tempX, tempY = roi_recenter(inp, tempX, tempY)
        con['x'] = tempX
        con['y'] = tempY
    # print("Grouping, pruning, and recentering contacts complete.")

    return contacts, ecdata


def retrain(arc_list, atrcfg_info):
    try:
        mats.log.info('retrain start')
        # print('!! RETRAIN START')
        # mats.mats_error_report_level('MSG')

        con_list = ContactList()
        ecd_list = EcdataList()

        arc = mats.Archive()
        atrcfg = mats.AtrConfig()
        matscfg = mats.cfg.Cfg()

        atrcfgfile = matscfg.atrconfig_name(atrcfg_info['Uuid'])
        if atrcfg.load(atrcfgfile) == 1:
            raise RuntimeError('Failed to load ATR Config ({})'.
                               format(atrcfgfile))
        mats.log.info('Loaded AtrConfig ({})'.format(atrcfgfile))

        mats.log.info('Scanning for packages...')
        mats.pkg.scan()

        mats.log.info('Creating classifier module...')
        cls = mats.pkg.create('clsCh1Resnet')
        if cls is None:
            raise RuntimeError('Unable to find classifier module.')

        mats.log.info('Configuring classifier module...')
        try:
            cls.configure(atrcfg['cls_cfg'])
        except RuntimeError:
            raise RuntimeError('Failed to configure classifier module.')

        mats.log.info('Enabling classifier training...')
        if not cls.trainable(None):
            raise RuntimeError('Classifier module not trainable')

        mats.log.info('Load clinfo...')
        clinfo = atrcfg['clinfo']

        if 'train_arc' in clinfo:
            mats.log.info('Found training archive information.')
            for arcId in clinfo['train_arc']:
                try:
                    arc.load(arcId)
                except RuntimeError:
                    mats.log.warn(
                        'Failure loading archive file ({})'.format(arcId))
                    continue

                try:
                    con = arc.contact()
                    ecd = arc.ecdata()
                except RuntimeError:
                    mats.log.warn(
                        'Failure loading contacts from "{}"'.format(arcId))
                    continue

                try:
                    cls.addTrainData(con, ecd)
                except RuntimeError:
                    mats.log.warn(
                        'Failure adding training data for "{}"'.format(arcId))
                    continue

        if 'validation_arc' in clinfo:
            mats.log.info('Found validation archive information.')
            for arcId in clinfo['validation_arc']:
                try:
                    arc.load(arcId)
                except RuntimeError:
                    mats.log.warn(
                        'Failure loading archive file ({})'.format(arcId))
                    continue

                try:
                    con = arc.contact()
                    ecd = arc.ecdata()
                except RuntimeError:
                    mats.log.warn(
                        'Failure loading contacts from "{}"'.format(arcId))
                    continue

                if len(con) == 0:
                    mats.log.warn(
                        'No contacts in archive file ({})'.format(arcId))
                    continue

                try:
                    cls.addTrainData(con, ecd, True)
                except RuntimeError:
                    mats.log.warn(
                        'Failure adding validation data for "{}"'.format(arcId)
                    )
                    continue

                for c, e in zip(con, ecd):
                    con_list.append(c)
                    ecd_list.append(e)

        mats.log.info('Load training data...')
        for arcId in arc_list:
            try:
                arc.load(arcId)
            except RuntimeError:
                mats.log.warn(
                    'Failure loading archive file ({})'.format(arcId))
                continue

            try:
                con = arc.contact()
                ecd = arc.ecdata()
            except RuntimeError:
                mats.log.warn(
                    'Failure loading contact info from "{}"'.format(arcId))
                continue

            try:
                cls.addTrainData(con, ecd, True)
                cls.addTrainData(con, ecd)
            except RuntimeError:
                mats.log.warn(
                    'Failure adding training data for "{}"'.format(arcId))
                continue
            for c, e in zip(con, ecd):
                con_list.append(c)
                ecd_list.append(e)

        # Update clinfo information.
        for arclist_name in ['validation_arc']:
            if arclist_name in clinfo:
                cl_arc = clinfo[arclist_name]
                ix1 = len(cl_arc)
            else:
                cl_arc = mats.Cell()
                ix1 = 0
            cl_arc.resize(1, ix1+len(arc_list))
            for ix in range(len(arc_list)):
                cl_arc[ix1+ix] = arc_list[ix]
            clinfo[arclist_name] = cl_arc

        mats.log.info('Start training...')
        deps, ccfg = cls.train()

        # ROC Curve
        # First, re-configure the classifier.
        mats.log.info('Compute ROC curve...')
        try:
            cls.configure(ccfg)
        except RuntimeError:
            raise RuntimeError(
                'Failed to configure classifier module after retraining.')
        # Next, run classifier on contacts.
        try:
            cls.classify(con_list, ecd_list)
        except RuntimeError:
            raise RuntimeError('Failed to classify contacts after retraining.')
        gt = []
        conf = []
        num_pos = 0
        for con in con_list:
            gt.append(con['gt'])
            conf.append(con['classconf'])
            if con['gt']:
                num_pos += 1
        fad, pc, thresh = sklearn.metrics.roc_curve(gt, conf)
        roc = mats.cfg.create_atr_roc()
        roc['PdPc'] = pc
        roc['Fad'] = fad
        roc['Threshold'] = thresh
        roc['NumberOfPositives'] = num_pos

        mats.log.info('Make ATR_Configuration...')
        uuid = mats.uuid.uuid_generator()
        mats.log.warn('New configure UUID: {}'.format(uuid))
        date = datetime.today()
        cfg = mats.cfg.create_atr_configuration()
        cfg['Sensor'] = atrcfg['sensor']
        cfg['Uuid'] = uuid
        cfg['SourceConfigId'] = atrcfg_info['Uuid']
        cfg['Name'] = '{}+{} {}'.format(
            atrcfg['detector'], atrcfg['classifier'], date.strftime('%Y%m%d')
        )
        cfg['Date'] = mats.time.datenum({
            'year': date.year,
            'month': date.month,
            'day': date.day,
            'hour': date.hour,
            'minute': date.minute,
            'dsecond': 0.0
        })
        cfg['Description'] = 'Tuner Generated Configuration'
        cfg['Threshold'] = 0.5
        cfg['ThreadSafe'] = atrcfg_info['ThreadSafe']
        cfg['Location'] = atrcfg_info['Location']
        cfg['Dependency'] = deps
        cfg['RoCs'] = [roc]

        mats.log.info('Make atrcfg file...')
        atrcfg.set_classifier('clsCh1ResnetTrt', 'MATS_C', '1.2', ccfg)
        atrcfg['filename'] = osp.join(mats.mats_output_dir(), uuid+'.atrcfg')
        atrcfg.save()

        # Note: clinfo is not stored internally for an AtrConfig. So, if the
        # file does not exist then setting the clinfo will not save it.
        # Therefore, we must save our new AtrConfig before we add clinfo.
        atrcfg['clinfo'] = clinfo

        mats.log.info('Training Complete!')
    except RuntimeError:
        raise RuntimeError('Python exception occurred.')
    return cfg


def calc_sweetspot(inp):
    """
    Calculate range bounds for the portion of data suitable for ATR.

    :param inp: Input object
    :type inp: mats.Input
    """
    if sensor_ is None:
        mats.log.warn('Missing Sensor. Using default sweetspot')
        return mats.core.default_sweetspot(inp)
    return sensor_.sweetspot(inp)


def roi_recenter(inp, x, y):
    """
    Reposition contact snippet.

    :param inp: Input object
    :type inp: mats.Input
    :param x: x pixel coordinate of contact
    :type x: int
    :param y: y pixel coordinate of contact
    :type y: int
    :returns: New pixel coordinates (x, y)
    :rtype: (int, int)
    """
    if sensor_ is None:
        mats.log.warn('Missing Sensor. Recentering not available.')
        return x, y
    try:
        sensor_.roi_recenter(inp, x, y)
    except:
        mats.log.warn(f'ROI recenter failed on {inp.filename} at x,y = {x},{y}')
    return x, y
