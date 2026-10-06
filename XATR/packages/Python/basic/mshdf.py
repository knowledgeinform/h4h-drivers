import mats
import mats.geo
import mats.interp
import mats.time
import mats.log
import h5py
import numpy as np
import scipy.signal
import os.path as osp
import math
import warnings
import glob
import numpy


typeChan = np.dtype([
    ('Range', np.float32),
    ('RangeDelay', np.float32),
    ('Frequency', np.float64),
    ('AlongTrackResolution', np.float64),
    ('AcrossTrackResolution', np.float64),
    ('SlantRange', np.float64),
    ('ChannelType', np.uint32),
    ('MotionCorrected', np.uint8)
])


typeNav = np.dtype([
    ('Yaw', np.float64), ('Pitch', np.float64), ('Roll', np.float64),
    ('Depth', np.float64), ('Altitude', np.float64), ('SoundSpeed', np.float64),
    ('Latitude', np.float64), ('Longitude', np.float64)
])


typeTime = np.dtype([
    ('Year', np.uint32),
    ('Month', np.uint32),
    ('Day', np.uint32),
    ('Hour', np.uint32),
    ('Minute', np.uint32),
    ('DecimalSec', np.float32),
    ('DaylightSavings', np.uint8),
    ('LocalOffset', np.float32)
])


def read_stream_name(fid, dname):
    dset = fid[dname]
    sname = dset.attrs['DataStreamName']
    if type(sname) in [bytes, numpy.bytes_]:
        return sname.decode('utf-8')
    return sname

def read_sensor_name(fid, dname):
    dset = fid[dname]
    sname = dset.attrs['SensorName']
    if type(sname) in [bytes, numpy.bytes_]:
        return sname.decode('utf-8')
    return sname


def hdf5ReadTime(fid):
    if '/Platform/Time' in fid:
        dset = fid['/Platform/Time']
    else:
        raise RuntimeError('Missing /Platform/Time.')

    try:
        t = np.array(dset, dtype=typeTime)
    except:
        raise RuntimeError('Failure reading time data.')

    # To convert time data to UTC
    date = {
        'year': 0, 'month': 0, 'day': 0, 'hour': 0, 'minute': 0, 'dsecond': 0.0
    }
    utc = np.zeros((len(t)))
    for q in range(len(t)):
        date['year'] = int(t['Year'].flatten()[q])
        date['month'] = int(t['Month'].flatten()[q])
        date['day'] = int(t['Day'].flatten()[q])
        date['hour'] = int(t['Hour'].flatten()[q])
        date['minute'] = int(t['Minute'].flatten()[q])
        date['dsecond'] = float(t['DecimalSec'].flatten()[q])
        utc[q] = mats.time.datenum(date)
    return utc


def hdf5ReadNav(fid, inp):
    anum = inp['nav_size']

    # open data set
    if '/Sonar/Sensor1/Data1/Navigation' in fid:
        dset = fid['/Sonar/Sensor1/Data1/Navigation']
    elif '/Platform/Navigation' in fid:
        dset = fid['/Platform/Navigation']
    else:
        raise RuntimeError('Unable to open Navigation dataset.')

    # Read nav data
    nav = np.array(dset, dtype=typeNav)
    num = len(nav)

    # Read time data
    try:
        time = hdf5ReadTime(fid)
    except:
        raise RuntimeError('Failure reading time data.')
    if not anum == len(inp.get_time()):
        raise RuntimeError('Time length differs from data size.')

    # If necessary, interpolate nav data.
    if not num == anum:
        # Different size -> must interpolate existing data
        tempLat = np.zeros((num,))
        tempLon = np.zeros((num,))
        tempHeading = np.zeros((num,))
        tempTime = np.zeros((num,))
        tempHeight = np.zeros((num,))
        tempDepth = np.zeros((num,))
        for k in range(num):
            tempLat[k] = nav[k]['Latitude']
            tempLon[k] = nav[k]['Longitude']
            tempHeading[k] = nav[k]['Yaw']
            tempTime[k] = time[k]
            tempHeight[k] = nav[k]['Altitude']
            tempDepth[k] = nav[k]['Depth']

        rate = anum / num
        x = np.array([k*rate for k in range(num)])
        xx = np.array([k for k in range(anum)])

        mats.interp.interp1(x, tempLat, None, xx, inp.get_lat(), None, "linear")
        mats.interp.interp1(x, tempLon, None, xx, inp.get_lon(), None, "linear")
        mats.interp.interp1(x, tempHeading, None, xx, inp.get_heading(), None, "linear")
        mats.interp.interp1(x, tempTime, None, xx, inp.get_time(), None, "linear")
        mats.interp.interp1(x, tempHeight, None, xx, inp.get_height(), None, "linear")
        mats.interp.interp1(x, tempDepth, None, xx, inp.get_depth(), None, "linear")
    else:
        # Same size -> copy data to existing pointers to numpy 1D arrays
        pLat = inp.get_lat()
        pLon = inp.get_lon()
        pHeading = inp.get_heading()
        pTime = inp.get_time()
        pHeight = inp.get_height()
        pDepth = inp.get_depth()
        for k in range(num):
            pLat[k] = nav[k]['Latitude']
            pLon[k] = nav[k]['Longitude']
            pHeading[k] = nav[k]['Yaw']
            pTime[k] = time[k]
            pHeight[k] = nav[k]['Altitude']
            pDepth[k] = nav[k]['Depth']

    return


def hdf5ReadChannelInfo(fid, dname):
    dset = fid[dname]
    chan = np.array(dset, dtype=typeChan)
    return chan


def read_data(fid, info, data):
    complexData = False

    # This code assumes ChannelType is 1 or 2
    if not info['ChannelType'] in [1, 2]:
        mats.log.error('Unable to handle given ChannelType.')
        raise RuntimeError('Unable to handle given ChannelType.')

    # Check if complex component of data is present
    if '/Sonar/Sensor1/Data1/PingDataPhase' in fid:
        complexData = True

    did = fid['/Sonar/Sensor1/Data1/PingData']
    if complexData:
        did2 = fid['/Sonar/Sensor1/Data1/PingDataPhase']

    # Read data
    try:
        if did.ndim == 2:
            indata1 = did[:, :]
        # Check for singleton 3rd dimension, which will trigger the multi-image
        #   case below in error for starboard images
        elif did.ndim == 3 and did.shape[2] == 1:
            indata1 = did[:, :, 0]
        else:
            indata1 = did[:, :, info['ChannelType']-1]
        indata1 = indata1.astype('float64')
    except:
        mats.log.error('Failed H5D data read.')
        raise RuntimeError('Failed H5D data read.')

    if complexData:
        try:
            if did2.ndim == 2:
                indata2 = did2[:, :]
            elif did2.ndim == 3 and did2.shape[2] == 1:
                indata2 = did2[:, :, 0]
            else:
                indata2 = did2[:, :, info['ChannelType']-1]
            indata2 = indata2.astype('float64')
        except:
            mats.log.error('Failed H5D data read.')
            raise RuntimeError('Failed H5D data read.')

    # Convert data
    data.storage = 'ROW_MAJOR'
    if complexData:
        data.format = 'AMP_PHASE'
    else:
        data.format = 'REAL_IMAG'
    data.ares = info['AlongTrackResolution']
    data.cres = info['AcrossTrackResolution']
    data.precision = 'DOUBLE'

    if complexData:
        # TODO: Assigning via tuple is not actually implemented in Data()
         data.data = indata1 * np.exp(1j * indata2)
#        data['data'] = (indata1, indata2)
    else:
        data.data = indata1

    return


def hdf5FileLoad(fn):
    try:
        fid = h5py.File(fn, 'r')
    except:
        mats.log.error('Failed to open HDF5 file.')
        raise FileExistsError('Failed to open HDF5 file.')

    try:
        info = hdf5ReadChannelInfo(fid, '/Sonar/Sensor1/Data1/ChannelInfo')
    except:
        mats.log.error('Reading of ChannelInfo failed.')

    return fid, info


def load_ssam2(fid, info, inp):
    # Get filename from file path so we can see if data is hi/lo are in separate
    # files.
    (pathTo, filename) = osp.split(inp[0]['filename'])

    # Filename check if we have a LF file and ensure filename is using SSAM2
    # filenaming convention.
    if filename[1:3] == 'Li':
        # If the data is low frequency data we just return since we will
        # load it when we load the high frequency data.
        return []

    if not filename[:3] == 'PHi' and not filename[:3] == 'SHi':
        mats.log.error('Unknown SSAM2 filenaming detected')
        raise RuntimeError('Unknown SSAM2 filenaming detected')

    # Only expecting one channel at a time for SSAM2...
    if len(info) > 1:
        mats.log.error('Unexpected number of channels for SSAM2.')
        raise RuntimeError('Unexpected number of channels for SSAM2.')

    # Make BB data file name from HF data file name. Assumes that changing the
    # second character, which corresponds to the frequency band, in filename.
    loFilePath = inp[0]['filename']
    loFilePath = loFilePath[:len(pathTo)+2] + 'L' + loFilePath[len(pathTo)+3:]

    # Open BB file so that we can get LF data also.
    try:
        fid_lo, info_lo = hdf5FileLoad(loFilePath)
    except:
        raise RuntimeError('Failure loading LF file ({}).'.format(loFilePath))

    # As of coding the channel enums are:
    # UNKNOWN=0 PORT=1 STARBOARD=2 SUBBOTOM=3 BATHYMETRY=4 FORWARD LOOKING=5
    # Reader only loads PORT and STARBOARD. We have noticed wrong ChannelTypes
    # being written by SWARM. So, lets try to detect them and fix if possible.
    if info[0]['ChannelType'] == 0:
        raise RuntimeError("'UNKNOWN' ChannelType. Unable to load.")
    elif info[0]['ChannelType'] > 2 and info[0]['ChannelType'] < 6:
        raise RuntimeError('Unsupported ChannelType. Unable to load.')
    elif info[0]['ChannelType'] > 5:
        warnings.warn('Unexpected ChannelType. Trying to correct it.')
        if filename[:3] == "PHi":
            warnings.warn("Identified ChannelType as PORT from filename.")
            info[0]['ChannelType'] = 1
            info_lo[0]['ChannelType'] = 1
        elif filename[:3] == "SHi":
            warnings.warn("Identified ChannelType as STBD from filename.")
            info[0]['ChannelType'] = 2
            info_lo[0]['ChannelType'] = 2
        else:
            raise RuntimeError('Failed to correct ChannelType.')

    # Read Ping Data
    try:
        inp[0].add_data('HF')
        read_data(fid, info[0], inp[0].data('HF'))
    except:
        raise RuntimeError('Failure loading HF PingData.')

    try:
        inp[0].add_data('BB')
        read_data(fid_lo, info_lo[0], inp[0].data('BB'))
    except:
        raise RuntimeError('Failure loading BB PingData.')

    if info[0]['AlongTrackResolution'] == 0:
        raise RuntimeError('Zero along-track resolution for HF.')
    if info_lo[0]['AlongTrackResolution'] == 0:
        raise RuntimeError('Zero along-track resolution for BB.')

    # Read Navigation Data
    anum = inp[0].data('HF').anum
    cnum = inp[0].data('HF').cnum
    try:
        inp[0].allocate_nav(anum)
        hdf5ReadNav(fid, inp[0])
    except:
        raise RuntimeError('Reading nav data failed.')

    # Initialize other fields
    inp[0]['sensor'] = 'ONR SSAM2'
    inp[0].data('HF').ares = info[0]['AlongTrackResolution']
    inp[0].data('HF').cres = info[0]['AcrossTrackResolution']
    inp[0].data('BB').ares = info_lo[0]['AlongTrackResolution']
    inp[0].data('BB').cres = info_lo[0]['AcrossTrackResolution']

    if info[0]['ChannelType'] == 1:
        inp[0].side = 'PORT'
    elif info[0]['ChannelType'] == 2:
        inp[0].side = 'STBD'
    else:
        raise RuntimeError("Unknown ChannelType.")
    inp[0].sweetspot = [0, cnum-1]

    # Double-check along-track resolution
    lat = inp[0].get_lat()
    lon = inp[0].get_lon()
    TrackDist, _ = mats.geo.latlon2dist(
        lat[0], lon[0], lat[anum-1], lon[anum-1])
    corrected_ares = TrackDist / float(anum)

    if abs(info[0]['AlongTrackResolution']-corrected_ares)/corrected_ares > 0.05:
      warnings.warn('Ares (HF) is being corrected from {} to {} ({}).'.format(
          info[0]['AlongTrackResolution'],
          corrected_ares,
          inp[0].filename
      ))
      inp[0].data('HF').ares = corrected_ares

    fid_lo.close()

    return inp

def load_kraken(fid, info, inp):
    (pathTo, filename) = osp.split(inp[0]['filename'])
    
    if info[0]['ChannelType'] == 0:
        raise RuntimeError("'UNKNOWN' ChannelType. Unable to load.")
    elif info[0]['ChannelType'] > 2 and info[0]['ChannelType'] < 6:
        raise RuntimeError('Unsupported ChannelType. Unable to load.')
    elif info[0]['ChannelType'] > 5:
        warnings.warn('Unexpected ChannelType. Trying to correct it.')
        if filename[:3] == "PHi":
            warnings.warn("Identified ChannelType as PORT from filename.")
            info[0]['ChannelType'] = 1
        elif filename[:3] == "SHi":
            warnings.warn("Identified ChannelType as STBD from filename.")
            info[0]['ChannelType'] = 2
        else:
            raise RuntimeError('Failed to correct ChannelType.')
            
    # Read Ping Data
    try:
        inp[0].add_data('HF')
        read_data(fid, info[0], inp[0].data('HF'))
    except:
        raise RuntimeError('Failure loading HF PingData.')
        
    if info[0]['AlongTrackResolution'] == 0:
        raise RuntimeError('Zero along-track resolution for HF.')
        
    # Read Navigation Data
    anum = inp[0].data('HF')['anum']
    cnum = inp[0].data('HF')['cnum']
    try:
        inp[0].allocate_nav(anum)
        hdf5ReadNav(fid, inp[0])
    except:
        raise RuntimeError('Reading nav data failed.')
        
    # Initialize other fields
    inp[0]['sensor'] = 'Kraken'
    inp[0].data('HF')['ares'] = info[0]['AlongTrackResolution']
    inp[0].data('HF')['cres'] = info[0]['AcrossTrackResolution']

    if info[0]['ChannelType'] == 1:
        inp[0]['side'] = 'PORT'
    elif info[0]['ChannelType'] == 2:
        inp[0]['side'] = 'STBD'
    else:
        raise RuntimeError("Unknown ChannelType.")
    inp[0]['sweetspot'] = [0, cnum-1]
    
    # Double-check along-track resolution
    lat = inp[0].get_lat()
    lon = inp[0].get_lon()
    
    # only correct ares if lats and lons are somewhat valid
    if np.all(lat!=0) and np.all(lon!=0): 
        TrackDist, _ = mats.geo.latlon2dist(
            lat[0], lon[0], lat[anum-1], lon[anum-1])
        corrected_ares = TrackDist / float(anum)
    
        if abs(info[0]['AlongTrackResolution']-corrected_ares)/corrected_ares > 0.05:
          warnings.warn('Ares (HF) is being corrected from {} to {} ({}).'.format(
              info[0]['AlongTrackResolution'],
              corrected_ares,
              inp[0]['filename']
          ))
          inp[0].data('HF')['ares'] = corrected_ares
    else:
        warnings.warn('Lats/Lons have 0 values')

    return inp
        
def load_edgetech(fid, info, inp):
    # Read Ping Data
    for k in range(len(info)):
        try:
            inp[k].add_data('HF')
            read_data(fid, info[k], inp[k].data('HF'))
        except:
            mats.log.error('Failed Allocation of PingData.')
            raise RuntimeError('Failed Allocation of PingData.')

    # if anum is zero then there is no data... so we don't need to do anything
    # for this file
    anum = inp[0].data('HF')['anum']
    cnum = inp[0].data('HF')['cnum']
    if inp[0].data('HF')['anum'] == 0:
        inp = []
        return inp

    # Read Navigation Data
    inp[0].allocate_nav(anum)
    try:
        hdf5ReadNav(fid, inp[0])
    except:
        mats.log.error('Reading nav data failed.')
        raise RuntimeError('Reading nav data failed.')

    # Initialize other common fields

    # Finished loading side common fields, so lets copy the information into the
    # other sides.
    sLat = inp[0].get_lat()
    sLon = inp[0].get_lon()
    sHeading = inp[0].get_heading()
    sTime = inp[0].get_time()
    sHeight = inp[0].get_height()
    sDepth = inp[0].get_depth()
    for k in range(len(info)):
        inp[k]['sensor'] = 'EDGETECH-850'

        if info[k]['ChannelType'] == 1:
            inp[k]['side'] = 'PORT'
        elif info[k]['ChannelType'] == 2:
            inp[k]['side'] = 'STBD'
        else:
            mats.log.error('Unknown ChannelType.')
            raise RuntimeError('Unknown ChannelType.')

        if k > 0:
            inp[k].allocate_nav(anum)
            dLat = inp[k].get_lat()
            dLon = inp[k].get_lon()
            dHeading = inp[k].get_heading()
            dTime = inp[k].get_time()
            dHeight = inp[k].get_height()
            dDepth = inp[k].get_depth()
            for j in range(anum):
                dLat[j] = sLat[j]
                dLon[j] = sLon[j]
                dHeading[j] = sHeading[j]
                dTime[j] = sTime[j]
                dHeight[j] = sHeight[j]
                dDepth[j] = sDepth[j]

        inp[k]['sweetspot'] = [0, cnum - 1]

    return inp


def load_marinesonic(fid, info, inp):
    # Loading is the same as Edgetech except for a few things.
    try:
        inp = load_edgetech(fid, info, inp)
    except:
        mats.log.error('Error loading data.')
        raise RuntimeError('Error loading data.')

    # Fix fields that could be wrong from Edgetech read.
    for k in range(len(inp)):
        if math.floor(info[k]['Frequency']) == 900000:
            inp[k]['sensor'] = 'MARINESONIC-900'
        elif math.floor(info[k]['Frequency']) == 1800000:
            inp[k]['sensor'] = 'MARINESONIC-1800'
        else:
            mats.log.warn('Unknown MARINESONIC')
            inp[k]['sensor'] = 'MARINESONIC'

        # Fix bad resolution values
        anum = inp[k].data('HF')['anum']
        cnum = inp[k].data('HF')['cnum']
        if info[k]['AcrossTrackResolution'] < 0:
            inp[k].data('HF')['cres'] = float(info[k]['Range']) / float(cnum)
        else:
            inp[k].data('HF')['cres'] = info[k]['AcrossTrackResolution']

        if info[k]['AlongTrackResolution'] < 0:
            lat = inp[0].get_lat()
            lon = inp[0].get_lon()
            tmp = np.zeros((anum-1))
            for j in range(anum-1):
                tmp[j], _ = mats.geo.latlon2dist(
                    lat[j], lon[j], lat[j+1], lon[j+1])

            tmp = scipy.signal.medfilt(tmp, 11)
            inp[k].data('HF')['ares'] = np.mean(tmp)
        else:
            inp[k].data('HF')['ares'] = info[k]['AlongTrackResolution']

    return inp


def load_aqs20(fid, info, inp):
    # As of coding the channel enums are:
    # UNKNOWN=0 PORT=1 STARBOARD=2 SUBBOTOM=3 BATHYMETRY=4 FORWARD LOOKING=5
    # Reader only loads PORT and STARBOARD. We have noticed wrong ChannelTypes
    # being written by SWARM. So, lets try to detect them and fix if possible.
    if info[0]['ChannelType'] == 0:
        raise RuntimeError("'UNKNOWN' ChannelType. Unable to load.")
    elif info[0]['ChannelType'] > 2 and info[0]['MSHDF_ENUM_CHANNELTYPE'] < 6:
        raise RuntimeError('Unsupported ChannelType. Unable to load.')
    elif info[0]['ChannelType'] > 5:
        raise RuntimeError('Invalid ChannelType. Unable to load.')

    # Read Ping Data
    try:
        inp[0].add_data('HF')
        read_data(fid, info[0], inp[0].data('HF'))
    except:
        raise RuntimeError('Failure loading HF PingData.')

    if info[0]['AlongTrackResolution'] == 0:
        raise RuntimeError('Zero along-track resolution for HF.')

    # Read Navigation Data
    anum = inp[0].data('HF')['anum']
    cnum = inp[0].data('HF')['cnum']
    try:
        inp[0].allocate_nav(anum)
        hdf5ReadNav(fid, inp[0])
    except:
        raise RuntimeError('Reading nav data failed.')

    # Initialize other fields
    inp[0]['sensor'] = 'AQS20-LRSAS'
    inp[0].data('HF')['ares'] = info[0]['AlongTrackResolution']
    inp[0].data('HF')['cres'] = info[0]['AcrossTrackResolution']

    if info[0]['ChannelType'] == 1:
        inp[0]['side'] = 'PORT'
    elif info[0]['ChannelType'] == 2:
        inp[0]['side'] = 'STBD'
    else:
        raise RuntimeError("Unknown ChannelType.")
    inp[0]['sweetspot'] = [0, cnum-1]

    # Double-check along-track resolution
    lat = inp[0].get_lat()
    lon = inp[0].get_lon()
    TrackDist, _ = mats.geo.latlon2dist(
        lat[0], lon[0], lat[anum-1], lon[anum-1])
    corrected_ares = TrackDist / float(anum)

    ares = info[0]['AlongTrackResolution']
    if abs(ares-corrected_ares)/corrected_ares > 0.05:
        mats.log.warn(
            'Ares (HF) is being corrected from {} to {} ({}).'.format(
                ares, corrected_ares, inp[0]['filename']))
        inp[0].data('HF')['ares'] = corrected_ares

    if '/Sonar/Sensor1/Data2' in fid:
        inp.append(mats.Input())
        
        try:
            inp[1].add_data('HF')
            read_data(fid, info[0], inp[1].data('HF'))
        except:
            raise RuntimeError('Failure loading HF PingData.')

        anum = inp[1].data('HF')['anum']
        cnum = inp[1].data('HF')['cnum']

        # Copy navigation data from other side
        inp[1].allocate_nav(anum)
        np.copyto(inp[1].get_lat(), inp[0].get_lat())
        np.copyto(inp[1].get_lon(), inp[0].get_lon())
        np.copyto(inp[1].get_heading(), inp[0].get_heading())
        np.copyto(inp[1].get_time(), inp[0].get_time())
        np.copyto(inp[1].get_height(), inp[0].get_height())
        np.copyto(inp[1].get_depth(), inp[0].get_depth())
        inp[1]['sweetspot'] = [0, cnum - 1]

        inp[1]['filename'] = inp[0]['filename']
        inp[1]['sensor'] = 'AQS20-LRSAS'
        inp[1].data('HF')['ares'] = inp[0].data('HF')['ares']
        inp[1].data('HF')['cres'] = inp[0].data('HF')['cres']
        inp[1]['side'] = 'STBD'

    return inp


class rdrMSHDF(mats.Reader):
    def __init__(self):
        self.filetype = 'h5'

    def isValid(self, fn):
        status = True

        # Open HDF5 file so that we can extract data from it
        if not osp.exists(fn):
            return False

        try:
            fid = h5py.File(fn, 'r')
        except:
            return False

        # Used locations:
        # "/Sonar/Sensor1/Data1/ChannelInfo"
        # "/Sonar/Sensor1/Data1/PingData"
        # "/Sonar/Sensor1/Data1/Navigation" or "/Platform/Navigation"
        # "/Platform/Time"
        #
        # Optional locations (optional depending on system):
        # "/Sonar/Sensor1/Data1/PingDataPhase"
        #
        # We don't check optional data since it doesn't make it an invalid
        # data file. But should be checked later if the system is suppose to
        # have it to function.

        # Check for Platform data
        flds = [
            '/Platform', '/Platform/Time', '/Sonar', '/Sonar/Sensor1',
            '/Sonar/Sensor1/Data1', '/Sonar/Sensor1/Data1/ChannelInfo',
            '/Sonar/Sensor1/Data1/PingData'
        ]
        for fld in flds:
            if fld not in fid:
                mats.log.error("'{}' data set missing.".format(fld))
                status = False

        if '/Sonar/Sensor1/Data1/Navigation' not in fid:
            if '/Platform/Navigation' not in fid:
                mats.log.error("Unable to locate navigation information.")
                status = False
        fid.close()
        return status

    def read(self, filePath):
        mats.log.info('rdrMSHDF START')
        inp = []

        # Check if file is a valid MSHDF file
        if not self.isValid(filePath):
            mats.log.error("HDF5 file does not exist or is invalid.")
            raise FileExistsError('HDF5 file does not exist or is invalid.')

        try:
            file_id = h5py.File(filePath, 'r')
        except:
            mats.log.error('Failed to open HDF5 file.')
            raise FileExistsError('Failed to open HDF5 file.')

        dataStream = read_stream_name(file_id, '/Sonar/Sensor1/Data1')

        if dataStream == "SAS-LF":  # LF SSAM2
            # If the data is low frequency data we just return since we will
            # load it when we load the high frequency data.
            file_id.close()
            return inp

        try:
            info = hdf5ReadChannelInfo(
                file_id, "/Sonar/Sensor1/Data1/ChannelInfo"
            )
        except:
            mats.log.error('Reading of ChannelInfo failed.')
            raise RuntimeError('Failure reading of ChannelInfo.')

        if len(info) == 0:
            mats.log.error('No channel information found.')
            raise RuntimeError('No channel information found.')

        # We allocate the number of inputs based on the number of channels read.
        try:
            inp = [mats.Input() for i in range(len(info))]
        except:
            mats.log.error('Initialization of input structure failed.')
            raise RuntimeError('Failure initializing input structure.')

        # Set some common non-sensor specific information
        for x in inp:
            x['filename'] = filePath

        # Load the data into input.
        if dataStream == "JSF":  # EDGETECH
            inp = load_edgetech(file_id, info, inp)
        elif dataStream == "MST":  # MARINESONIC
            inp = load_marinesonic(file_id, info, inp)
        elif dataStream == "SAS-HF" or dataStream == "SAS-HBL" or dataStream == 'SAS':  # HF SSAM2
            sensorName = read_sensor_name(file_id, '/Sonar/Sensor1')
            if sensorName == 'SSAM 2':
                inp = load_ssam2(file_id, info, inp)
            elif sensorName == 'KRAKEN' or sensorName == 'MINSASLW':
                inp = load_kraken(file_id, info, inp)
            else:
                # Just default to SSAM 2 for now
                inp = load_ssam2(file_id, info, inp)
            
        elif dataStream == "LRSAS":  # AQS20-LRSAS
            inp = load_aqs20(file_id, info, inp)
        else:
            mats.log.error('Unknown data stream value.')
            raise RuntimeError('Unknown data stream value.')

        # Transpose data since hdf5 is row major format and all ATR
        # processing assumes column major.
        for k in range(len(inp)):
            bands = inp[k]['data_names']
            for band in bands:
                inp[k].data(band).storage = 'COL_MAJOR'

        # clean up
        file_id.close()
        mats.log.info('rdrMSHDF END')

        return inp

    def scan(self, folder):
        files = []
        tmp = glob.glob(osp.join(folder, '**', '*.'+self.filetype),
                        recursive=True)
        for fn in tmp:
            if osp.isdir(fn):
                warnings.warn('Directory with file extension ({}).'.format(
                    fn
                ))
                continue

            ext = osp.splitext(fn)[1][1:]
            if not ext == self.filetype:
                continue

            # Remove SSAM2 LF files
            name = osp.split(fn)[1]
            if name[1:3] == 'Li':
                continue
            files.append(fn)
        return files

    def configure(self, cfg):
        return True
