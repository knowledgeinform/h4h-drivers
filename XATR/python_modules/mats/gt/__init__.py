# DISTRIBUTION STATEMENT D. Distribution authorized to the Department of
# Defense and U.S. DoD contractors only; Administrative or Operational Use; 1
# Jan 2017. Other U.S. requests shall be referred to Naval Surface Warfare
# Center Panama City Division, ATTN: Technical Director NSWC PCD, 110 Vernon
# Ave, Panama City, FL 32407.
"""
mats.gt
-------
Contains functions related to ground truth.
"""
import os
import os.path as osp
import re

import csv
import yaml
import math
import json
from glob import glob

from mats import sys_config
import mats.log
import mats.sensor

from .gtc import GtContact


def __load_mats_cfg():
    """
    Load MATS configuration GT settings if present.

    :rtype: None
    """
    global gt_repo
    global mlo_type_encoding
    global non_mlo_type_encoding
    mats_cfg_fn = osp.join(os.getcwd(), 'mats.yml')
    if osp.exists(mats_cfg_fn):
        with open(mats_cfg_fn, 'r') as fh:
            cfg_in = yaml.safe_load(fh)
        if 'gt_repo' in cfg_in:
            gt_repo = cfg_in['gt_repo']
        else:
            mats.log.info('No "gt_repo" setting found in mats.yml.')
        if 'mlo_type_encoding' in cfg_in:
            mlo_type_encoding = cfg_in['mlo_type_encoding']
        else:
            mats.log.info('No "mlo_type_encoding" setting found in mats.yml.')
        if 'non_mlo_type_encoding' in cfg_in:
            non_mlo_type_encoding = cfg_in['non_mlo_type_encoding']
        else:
            mats.log.info(
                'No "non_mlo_type_encoding" setting found in mats.yml.')
    else:
        mats.log.info(f'Did not find MATS configuration file ({mats_cfg_fn}).')
    return


gt_repo = []  # Search locations for GT files.
# For the mapping of integers to type names the mats.sysconfig
# 'gt_type_encoding' field is used. It should have a list of encoding for
# each sensor. Two types of encodings are expected 'mlo' (Mark-Like Object) and
# 'mno' (Mark-like, None Object). For consistency when there are no types, keep
# 'UNKNOWN' as the encoding for each type. The following is an example of what
# mats.yml should look like for GT encodings:

# << in the mats.yml file >>
# gt_type_encoding:
#   - Default:
#     mlo: ['UNKNOWN']
#     mno: ['UNKNOWN']
#   - Sensor1:
#     mlo: ['UNKNOWN', 'MARK_TYPE1', 'MARK_TYPE2']
#     mno: ['UNKNOWN', 'NON_MARK_TYPE1', 'NON_MARK_TYPE2']
#   - Sensor2:
#     mlo: ['UNKNOWN', 'OTHER_TYPE1', 'OTHER_TYPE2']
#     mno: ['UNKNOWN', 'NON_OTHER_TYPE1', 'NON_OTHER_TYPE2']


def _fetch_encoding(sensor):
    if sensor is None:
        mlo_types = sys_config['gt_type_encoding']['Default']['mlo']
        mno_types = sys_config['gt_type_encoding']['Default']['mno']
        return mlo_types, mno_types
    if sensor not in sys_config['gt_type_encoding']:
        mats.log.warn(f"Not gt_type_encoding for sensor '{sensor}'. "
                      f"Using default.")
        return _fetch_encoding(None)
    mlo_types = sys_config['gt_type_encoding'][sensor].get(
        'mlo', sys_config['gt_type_encoding']['Default']['mlo'])
    mno_types = sys_config['gt_type_encoding'][sensor].get(
        'mno', sys_config['gt_type_encoding']['Default']['mno'])
    return mlo_types, mno_types


def _type2int(gt_type, type_encoding):
    """
    Returns the type encoding for a GT type name. Unknown types are encoded
    to 0.

    Parameters
    ----------
    gt_type : str
        GT type name.
    type_encoding : `list` of `str`
        List of string type labels. If None, the MATS configured encoding is
        applied.

    Returns
    -------
    int
        GT integer type encoding.
    """
    return next((k for k, t in enumerate(type_encoding) if gt_type == t), 0)


def _type2str(gt_type, type_encoding):
    """
    Returns the type decoding for a GT type name. Unknown types are encoded
    to 0.

    Parameters
    ----------
    gt_type : int
        GT integer type.
    type_encoding : `list` of `str`
        List of string type labels. If None, the MATS configured encoding is
        applied.

    Returns
    -------
    str
        GT string type.
    """
    if gt_type >= len(type_encoding) or gt_type < 0:
        return type_encoding[0]
    return type_encoding[gt_type]


def type_encode(gt_data, sensor=None):
    """
    Converts groundtruth type field to integers using type encoding.

    :param gt_data: Groundtruth to be encoded.
    :type gt_data: dict or GtContact or [GtContact]
    :param sensor: Name of sensor for groundtruth data.
    :type sensor: str or None

    :return: None
    """
    mlo_types, mno_types = _fetch_encoding(sensor)
    for gt in gt_data:
        if type(gt['type']) == int:
            continue
        if gt['MLO']:
            gt['type'] = _type2int(gt['type'], mlo_types)
        else:
            gt['type'] = _type2int(gt['type'], mno_types)
    return


def type_decode(gt_data, sensor=None) -> None:
    """
    Converts groundtruth type field to string names using type encoding.

    :param gt_data: Groundtruth for application of decode.
    :type gt_data: dict|[dict]
    :param sensor: Name of sensor for groundtruth data.
    :type sensor: str
    """
    mlo_types, mno_types = _fetch_encoding(sensor)
    for gt in gt_data:
        if type(gt['type']) == str:
            continue
        if gt['MLO']:
            gt['type'] = _type2str(gt['type'], mlo_types)
        else:
            gt['type'] = _type2str(gt['type'], mno_types)
    return


def read_txt(gtf):
    """
    Reads MATS groundtruth text file.

    .. note:: Every line of a GT text file should be a GT entry. A valid GT text
        file should have a column definition line such as:

        '% COLUMNS: X Y SIDE FILENAME NOTES'

        This defines the order of information for GT entries, which should
        immediately follow. Entries can be disabled by adding a '%' to the start
        of the line. Spaces are not allowed for entry information, except for
        NOTES which must come last if present.

        Valid GT entry fields are the following:

        - X: (Required) Across-track pixel location. If side is omitted, a negative value indicates PORT.
        - Y: (Required) Along-track pixel location.
        - NUM: (Optional) Entries ID.
        - TYPE: (Optional) Object integer type ID.
        - SIDE: (Optional) Side of vehicle (PORT|STBD).
        - FILENAME: (Required) Name of file that entry is located within.
        - NOTE: (Optional) Comment for entries.

    :param gtf: File path to a groundtruth text file.
    :type gtf: str

    :return: List of loaded groundtruth entries.
    :rtype: [dict]
    """
    if not osp.exists(gtf):
        raise FileExistsError(f"Unable to find GT file ({gtf}).")

    gt_data = []
    fields = ['X', 'Y', 'NUM', 'TYPE', 'SIDE', 'FILENAME', 'NOTE']

    with open(gtf, 'r') as fh:
        # First we find the column definition, which indicates the start of GT
        # entries.
        for line in fh:
            defn = re.match(r'^%\s*COLUMNS:', line)
            if defn:
                break

        # Parse column definition to determine entry information order
        cols = str.split(line[defn.end(0):])
        is_note = 'NOTE' in cols
        keys = []
        for fld in cols:
            if fld not in fields:
                mats.log.warn(f"Unknown GT text field {fld} in {gtf}")
                continue
            keys.append(fld.lower())

        # Check for required fields
        for req_key in ['x', 'y', 'filename']:
            if req_key not in keys:
                raise ValueError(
                    f'GT column definition does not have "{req_key}".')

        # Load GT entries
        for line in fh:
            if line[0] == '%':
                line = line[1:]
                enabled = False
            else:
                enabled = True
            val = line.rstrip().split(' ')
            val = list(filter(None, val))

            if is_note:
                # Remaining part of line becomes note
                if len(val) < len(cols):  # No note for entry
                    val.append('')
                elif len(val) > len(cols):  # Note with spaces
                    ix = len(cols)-1
                    note = ' '.join(val[ix:])
                    val = val[:ix+1]
                    val[ix] = note

            if not len(val) == len(cols):
                mats.log.warn(f'GT entry does not match definition. '
                              'Skipping line: {line}')
                continue
            gt = dict(zip(keys, val))

            # Correct field types and add defaults for missing fields
            gt['x'] = int(gt['x'])
            gt['y'] = int(gt['y'])
            if 'side' not in gt:
                if gt['x'] < 0:
                    gt['side'] = 'PORT'
                else:
                    gt['side'] = 'STBD'
                gt['x'] = abs(gt['x'])

            if 'num' in gt:
                gt['num'] = int(gt['num'])
            else:
                gt['num'] = 0

            if 'type' in gt:
                gt['type'] = int(gt['type'])
            else:
                gt['type'] = -99

            if 'note' not in gt:
                gt['note'] = ''
            gt['enabled'] = enabled

            # rename filename field to fn
            gt['fn'] = gt.pop('filename')

            gt_data.append(gt)
    return gt_data


def read_coin_csv(gtf):
    with open(gtf, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        cons = []
        for row in reader:
            con = {}

            if row['File Name'] == 'null':
                print('!! NULL FILE NAME FOR CONTACT')
                continue
            con['fn'] = row['File Name']

            if row['File Channel'] == 'null':
                repeat_contact = True
                con['side'] = 'PORT'
            else:
                repeat_contact = False
                con['side'] = row['File Channel']

            if row['X Location'] == 'null':
                con['x'] = 500
            else:
                con['x'] = int(row['X Location'])

            if row['Y Location'] == 'null':
                con['y'] = 500
            else:
                con['y'] = int(row['Y Location'])

            con['note'] = '{}-{}'.format(
                row['Observation Type'], row['Shape'])

            cons.append(con)

            if repeat_contact:
                con2 = con.copy()
                con2['side'] = 'STBD'
                cons.append(con2)
    return cons


def write_txt(gtf, gt_data):
    """
    Writes ground truth data to a text file.

    :param gtf: Name of ground truth file to be created.
    :type gtf: str
    :param gt_data: List of ground truth dicts.
    :type gt_data: [dict]
    """
    fmt = {
        'X': '{x:<6d}',
        'Y': '{y:<6d}',
        'NUM': '{num:<4d}',
        'TYPE': '{type:<4d}',
        'SIDE': '{side:<6s}',
    }

    # Check if type is strings or integers
    if any([type(x['type']) == str for x in gt_data]):
        raise TypeError(
            'String "type" detected for some GT. '
            'Convert to int (`mats.gt.type_encode`).')
    # Ensure integers
    for g in gt_data:
        g['x'] = round(g['x'])
        g['y'] = round(g['y'])

    # Check if we need to write out optional fields
    if all(['num' in x for x in gt_data]):
        is_num = any([x['num'] > 0 for x in gt_data])
    else:
        is_num = False
    if all(['type' in x for x in gt_data]):
        is_type = any([not x['type'] == -99 for x in gt_data])
    else:
        is_type = False
    if all(['note' in x for x in gt_data]):
        is_note = any([len(x['note']) > 0 for x in gt_data])
    else:
        is_note = False

    fh = open(gtf, 'w')

    # Write column defn string
    colstr = '%COLUMNS: X Y'
    fmtstr = '   ' + fmt['X']+' '+fmt['Y']
    if is_num:
        colstr += ' NUM'
        fmtstr += ' '+fmt['NUM']
    if is_type:
        colstr += ' TYPE'
        fmtstr += ' '+fmt['TYPE']
    colstr += ' SIDE FILENAME'
    fmtstr += ' '+fmt['SIDE']+' {fn}'
    if is_note:
        colstr += ' NOTE'
        fmtstr += ' {note}'
    colstr += '\n'
    fmtstr += '\n'
    fh.write(colstr)

    # Write out GT data
    for gt in gt_data:
        if 'enabled' in gt and not gt['enabled']:
            fh.write('%')
        fh.write(fmtstr.format(**gt))
    fh.close()
    return


def read_yml(gtf):
    with open(gtf, 'r') as fh:
        gt = yaml.safe_load(fh)
    return gt


def read_rlac_yml(gtf, mlo=None):
    if mlo is None:
        mlo = True

    with open(gtf, 'r') as fh:
        gt = yaml.safe_load(fh)
    if gt is None:
        return []

    try:
        gtd = [GtContact(g['Position'], int(g.get('EID', 0)), 'PORT', g['Type'],
                         g['UXO'], g.get('Note', ''), g['Filename'], g['Enabled'])
               for g in gt]
    except ValueError:
        gtd = [GtContact(g['Position'], 0, 'PORT', g['Type'], g['UXO'],
                         g.get('Note', ''), g['Filename'], g['Enabled'])
               for g in gt]
    except KeyError:
        gtd = [GtContact(g['Position'], 0, 'PORT', g['Type'], True,
                         g.get('Note', ''), g['Filename'], g['Enabled'])
               for g in gt]

    # TODO(Bradley): This uses the new GtContact, but to make it compatible with
    #   everything else we are going to make them dictionaries again.
    gtd = [dict(g) for g in gtd]

    type_encode(gtd, 'Image-RGB')
    # if type(mlo) == bool:
    #     gtd = [g for g in gtd if g['MLO'] == mlo]
    return gtd


def write_yml(gtf, gt_data):
    with open(gtf, 'w') as fh:
        yaml.dump(gt_data, fh, default_flow_style=False)


def read_via_json(gtf):
    gt = []
    with open(gtf, 'r') as fh:
        fdata = fh.read()
    vdata = json.loads(fdata)
    for tag in vdata:
        item = vdata[tag]
        if len(item['regions']) > 0:
            for reg in item['regions']:
                width = reg['shape_attributes']['width']
                height = reg['shape_attributes']['height']
                gt.append({
                    'fn': item['filename'],
                    'x': reg['shape_attributes']['x'] + width // 2,
                    'y': reg['shape_attributes']['y'] + height // 2,
                    'width': width,
                    'height': height,
                    'type': reg['region_attributes']['type'],
                    'num': 0,
                    'side': 'PORT',
                    'note': reg['region_attributes']['type'],
                    'enabled': True,
                    'MLO': True
                })
    type_encode(gt, 'Image-RGB')
    return gt


def groundtruth_remove(arc_folder):
    fns = glob(osp.join(arc_folder, '*.h5'))
    for fn in fns:
        mats.remove_gt(fn)
    return


def groundtruth_archive(arc, gt, sensor=None):
    """
    Apply groundtruth to a contact list.

    :param arc: MATS Input associated with contacts.
    :type arc: mats.Archive
    :param gt: Groundtruth information.
    :type gt: [dict]
    :param sensor: Name of sensor for groundtruth data.
    :type sensor: str or None
    """
    inp = arc.input()
    con = arc.contact()

    if type(inp['sensor']) is str and len(inp['sensor']) > 0:
        sensor_obj = mats.sensor.mats_sensor(inp['sensor'])
        if sensor_obj is not None:
            gt_dist = sensor_obj.gt_dist_thresh
        else:
            gt_dist = None
    else:
        gt_dist = None

    if gt_dist is None:
        gt_dist = 2.0
        mats.log.warn(f"Unknown sensor '{inp['sensor']}'. Defaulting to {gt_dist} meter GT radius.")

    # TODO: Sensor reference data and data names should be available via Sensor
    #       object, but it is not right now. So we are going to hardcode it for
    #       now.
    data_names = sensor_obj.data_names

    # Set all GT to false to ensure GT of contacts not near GT are false
    #   (could have been set true else where).
    for c in con:
        c['gt'] = 0

    fn = mats.filesystem.file_basename(inp['filename'])
    data = inp['data'][data_names[0]]
    ares = data['ares']
    cres = data['cres']

    # If 'enabled' is a field, we should remove things that are not enabled.
    if any(['enabled' in g for g in gt]):
        if not all(['enabled' in g for g in gt]):
            raise ValueError('Not all GT have "enabled" field.')
        filtered_gt = [g for g in gt if g['enabled']]
    else:
        # Keep all the GT
        filtered_gt = gt
    if not all(['x' in g for g in gt]):
        raise ValueError('Not all GT have "x" field.')
    if not all(['y' in g for g in gt]):
        raise ValueError('Not all GT have "y" field.')
    if not all(['side' in g for g in gt]):
        raise ValueError('Not all GT have "side" field.')
    if not all(['fn' in g for g in gt]):
        raise ValueError('Not all GT have "fn" field.')
    if not all(['type' in g for g in gt]):
        raise ValueError('Not all GT have "type" field.')

    # Remove GT not in file
    filtered_gt = [g for g in filtered_gt
                   if mats.filesystem.file_basename(g['fn']) == fn]

    # Convert GT type to integers
    type_encode(filtered_gt, sensor)

    # If MLO is a field, then the contact GT should only be true if MLO is true.
    for j, g in enumerate(filtered_gt):
        gtfn = mats.filesystem.file_basename(g['fn'])
        msg = "Compare: {:s} - {:s} ({:d}) to {:s} - {:s} ({:d})"
        mats.log.info(msg.format(fn, inp['side'], len(fn),
                                 gtfn, g['side'], len(gtfn)))
        if gtfn == fn and g['side'] == inp['side']:
            mats.log.info("  !! Matched")
            for k, c in enumerate(con):
                da = ares*(c['y'] - g['y'])
                dc = cres*(c['x'] - g['x'])
                dist = math.sqrt(da*da+dc*dc)
                if dist < gt_dist:
                    mats.log.info("  !! Adding GT ({:s})".format(c['uuid']))
                    if 'MLO' in g:
                        c['gt'] = g['MLO']
                    else:
                        c['gt'] = 1
                    c['type'] = g['type']
    arc.update_contacts(con)
    arc.update_groundtruth(filtered_gt)
    return


def groundtruth_results(arc_folder, gt):
    """
    Apply groundtruth to existing archive results.

    :param arc_folder: Results folder with archives.
    :type arc_folder: str, list of dict
    :param gt: Groundtruth to use. Can be a filename or list of groundtruth.
    :type gt: str
    :return: None
    """
    arc = mats.Archive()

    if type(gt) == str:
        if gt.endswith('.txt'):
            gt = read_txt(gt)
        elif gt.endswith('.yml'):
            gt = read_yml(gt)
        else:
            raise ValueError('Unrecognized groundtruth format.')

    files = glob(osp.join(arc_folder, '*.h5'))
    for fn in files:
        arc.load(fn)
        groundtruth_archive(arc, gt)
    return
