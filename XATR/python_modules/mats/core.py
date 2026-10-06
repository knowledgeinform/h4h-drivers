# DISTRIBUTION STATEMENT D. Distribution authorized to the Department of
# Defense and U.S. DoD contractors only; Administrative or Operational Use; 1
# Jan 2017. Other U.S. requests shall be referred to Naval Surface Warfare
# Center Panama City Division, ATTN: Technical Director NSWC PCD, 110 Vernon
# Ave, Panama City, FL 32407.
"""
mats.core
---------
Contains function for doing basic ATR tasks.
"""
import math
import json
import csv
import mats
import mats.log
import mats.basic
import mats.geo
import mats.sensor
import mats.filesystem
import mats.cluster
import numpy
import re


def load_json(filename):
    """
    Load JSON file into dictionary.
    
    :param filename: Filename of JSON file to be loaded.
    :type filename: str

    :return: Dict containing contents of JSON file.
    :rtype: dict
    """
    with open(filename) as fp:
        return json.load(fp)


def default_sweetspot(inp):
    """
    Set sweetspot to entire data (default sweetspot calculation).

    :param inp: MATS Input to have its sweetspot field set.
    :type inp: mats.Input
    """
    ss1 = 0
    ss2 = 0

    data = inp.data(inp.ref_name)
    if data:
        cnum = data['cnum']
        ss2 = cnum - 1
    inp.sweetspot = ss1, ss2


def detsub_contact_fill(inp, con, ecd):
    """
    Fill in contact and ecdata fields based on contact position.

    :param inp: MATS Input containing the contacts in `con`.
    :type inp: mats.Input
    :param con: MATS ContactList to be filled.
    :type con: mats.ContactList
    :param ecd: MATS EcdataList to be filled.
    :type ecd: mats.EcdataList
    """
    sns = mats.sensor.mats_sensor(inp.sensor)
    ecd.uuid = con.uuid

    # Nav length must be greater then 1 for this routine to compute
    # contact nav info correctly
    if sns.has_nav:
        if inp['nav_size'] < 2:
            mats.log.error("MATS Input nav length is less than one.")
            return

        if con['y'] >= inp['nav_size']:
            mats.log.error("Along-track index exceeds nav length.")
            return

    # Initialize classifier fields to default values
    con.cls = -99
    # con.classconf = -99
    # con.type = -99

    # Set File information
    con.filename = inp.filename
    con.side = inp.side

    if sns.has_nav:
        lat, lon = get_contact_latlong(inp, con['x'], con['y'])
        ecd['lat'] = lat
        ecd['lon'] = lon

        ecd['heading'] = inp['heading'][con['y']]
        ecd['time'] = inp['time'][con['y']]
        ecd['height'] = inp['height'][con['y']]

    ecd.load_input(inp)
    add_snippets(inp, con, ecd)
    return


def add_snippets(inp, con, ecd):
    """
    Add a snippet to ecdata for each sensor band based on the (x,y) position
    of a contact in the input's reference band.

    .. note:: This function is similar to snippet_generator() from the original MATS.

    :param inp: MATS Input associated with contacts.
    :type inp: mats.Input
    :param con: MATS Contact containing (x,y) position.
    :type con: mats.Contact
    :param ecd: MATS Ecdata corresponding to `con`, updated with snippet(s).
    :type ecd: mats.Ecdata
    """
    try:
        sensor = mats.sensor.mats_sensor(inp.sensor)
        sensor.snippet_generator(inp, con, ecd)
        return
    except ValueError:
        mats.log.error('Unknown sensor. Attempting default snippet generator')
        return
    # bands = inp['data_names']
    # if len(bands) == 0:
    #     return
    #
    # # Get info pertinent to reference band
    # x = con['x']
    # y = con['y']
    # anum, cnum = inp.data(inp['ref_name']).size()
    #
    # snipDims = sensor['snippet_size']
    # snipheight = snipDims[0]
    # snipwidth = snipDims[1]
    #
    # # Calculate parameters for each band and create the snippet.
    # for band in bands:
    #     data = inp.data(band)
    #     anum1, cnum1 = data.size()
    #     x1 = math.floor(x * cnum1 / cnum)
    #     y1 = math.floor(y * anum1 / anum)
    #     snipwidth1 = math.ceil(snipwidth * cnum1 / cnum)
    #     snipheight1 = math.ceil(snipheight * anum1 / anum)
    #     snip = data.snippet(x1, y1, snipwidth1, snipheight1)
    #     ecd.set_snippet(band, snip)


def gt_contact_list(inp, gt, con):
    """
    Apply ground truth to a contact list.

    :param inp: MATS Input associated with contacts.
    :type inp: mats.Input
    :param gt: Groundtruth information.
    :type gt: [dict]
    :param con: MATS Contact List. Returned with updated groundtruth info.
    :type con: mats.ContactList
    """
    if mats.cpp_backend:
        return mats.mc.gt_contact_list(inp, gt, con)

    sensor_name = inp['sensor']
    if type(sensor_name) is str and len(sensor_name) > 0:
        sensor_obj = mats.sensor.mats_sensor(sensor_name)
        if sensor_obj is not None:
            gt_dist = sensor_obj.gt_dist_thresh
        else:
            gt_dist = None
    else:
        gt_dist = None

    if gt_dist is None:
        gt_dist = 2.0
        msg = "Unknown sensor '{}'. Defaulting to {} meter GT radius."
        mats.log.warn(msg.format(sensor_name, gt_dist))

    # Set all GT to false to ensure GT of contacts not near GT are false
    #   (could have been set true else where).
    for k in range(len(con)):
        con[k]['gt'] = 0
    # from C:  mats::file_basename(input.filename(), fn);
    fn = mats.filesystem.file_basename(inp['filename'])
    # data = inp.data(inp['ref_name'])
    ares = inp.data('HF').ares
    cres = inp.data('HF').cres

    for j in range(len(gt)):
        gtFn = mats.filesystem.file_basename(gt[j]['fn'])
        msg = "Compare: {:s} - {:s} ({:d}) to {:s} - {:s} ({:d})"
        mats.log.info(msg.format(fn, inp['side'], len(fn),
                                 gtFn, gt[j]['side'], len(gtFn)))
        if gtFn == fn and gt[j]['side'] == inp['side']:
            mats.log.info("  !! Matched")
            for k in range(con.size()):
                da = ares*(con[k]['y'] - gt[j]['y'])
                dc = cres*(con[k]['x'] - gt[j]['x'])
                dist = math.sqrt(da*da+dc*dc)
                if dist < gt_dist:
                    mats.log.info(f"  !! Adding GT ({con[k]['uuid']:s})")
                    con[k]['gt'] = 1
                    con[k]['type'] = gt[j]['type']
    return


def calc_good_segments(bad_regions, full_y, des_y):
    """
    Determines good image segments from problematic regions.

    .. note:: Bad region elements may overlap.

    :param bad_regions: List of dicts describing bad regions of data. See
           `region_dict` for a description.
    :type bad_regions: [dict]
    :param full_y: The full along-track size of the image.
    :type full_y: int
    :param des_y: The desired along-track chunk size. Chunks that are
        significantly smaller than this will be folded into adjacent chunks or
        dropped entirely.
    :type des_y: int

    :return: Regions of data that can be processed, based on the areas that have
        been identified to contain errors. Only the y_starts and y_ends fields
        are filled in. These regions are not chunked except for the boundaries
        created by bad regions.
    :rtype: dict
    """
    if mats.cpp_backend:
        return mats.mc.calc_good_segments(bad_regions, full_y, des_y)

    # segments smaller than this will be purged
    len_thresh = 0.5 * des_y

    # Merge all bad regions
    good_mask = numpy.ndarray((full_y,), dtype=bool)
    good_mask.fill(True)
    for reg in bad_regions:
        good_mask[reg['start']:reg['end']+1] = False

    # Find boundaries of the good regions
    starts = [x for x in range(1, full_y) if good_mask[x] and not good_mask[x-1]]
    if good_mask[0]:
        starts.insert(0, 0)
    ends = [x for x in range(full_y-1) if good_mask[x] and not good_mask[x+1]]
    if good_mask[-1]:
        ends.append(full_y-1)

    lens = [y-x+1 for x, y in zip(starts, ends)]
    return {'y_starts': [x for x, l in zip(starts, lens) if l > len_thresh],
            'y_ends': [x for x, l in zip(ends, lens) if l > len_thresh]}


def calc_image_partitions(inp, good_segs):
    """
    Calculate the boundaries of image chunks within full image represented
    by a MATS Input.

    :param inp: MATS Input to be chunked.
    :type inp: mats.Input
    :param good_segs: Good regions of MATS Input.
    :type good_segs: [dict]

    :return: Calculated boundaries of image chunks.
    :rtype: dict
    """
    if mats.cpp_backend:
        return mats.mc.calc_image_partitions(inp, good_segs)

    # Ensure vectors defining good segments are present and balanced
    flds = ['y_starts', 'y_ends']
    assert(all([x in good_segs.keys() for x in flds]))
    num_segs = len(good_segs[flds[0]])
    for x in flds[1:]:
        assert(len(good_segs[x]) == num_segs)

    sweet_start, sweet_end = inp['sweetspot']
    hf_ptr = inp.data('HF')     # TODO: Other reference bands
    ares = hf_ptr.ares
    cres = hf_ptr.cres
#    sweet_start, sweet_end = mats_in.sweetspot
#    cres = mats_in.hf_cres
    useable_width_m = (sweet_end - sweet_start)*cres
    if useable_width_m < 5:  # not enough area to process on --> no chunks
        return None

    full_x = hf_ptr.cnum - 1

    des_y, y_mult = 1000, 1
#    [des_y, y_mult] = input_struct.sensor.calcChunkSize(input_struct);
    des_y = int(numpy.floor(float(full_x)*cres/ares))

    overlap_y = 100    # track overlap (in pixels)
    overlap_y = int(numpy.floor(overlap_y/y_mult)*y_mult)
    chunk_data = {'x_starts': [], 'x_ends': [], 'y_starts': [], 'y_ends': [],
                  'sweetspot_starts': [], 'sweetspot_ends': []}
    for q in range(num_segs):
        y_starts = [x for x in range(good_segs['y_starts'][q],
                                     good_segs['y_ends'][q], des_y-overlap_y)]
        y_ends = [min(x+des_y-1, good_segs['y_ends'][q]) for x in y_starts]
        # print('y_starts = {}\ny_ends = {}'.format(y_starts, y_ends))
        # Examine the size of the last segment
        if len(y_ends) > 1 and y_ends[-1]-y_starts[-1] < 0.5*des_y:
            # Last segment is too small, so merge this segment with the
            # previous one
            y_ends.pop(-2)
            y_starts.pop(-1)
            # print('y_starts = {}\ny_ends = {}'.format(y_starts, y_ends))
        # Add to master set of chunk definitions
        for k in range(len(y_starts)):
            chunk_data['y_starts'].append(y_starts[k])
            chunk_data['y_ends'].append(y_ends[k])
            chunk_data['x_starts'].append(0)
            chunk_data['x_ends'].append(full_x)
            chunk_data['sweetspot_starts'].append(sweet_start)
            chunk_data['sweetspot_ends'].append(sweet_end)
    return chunk_data


def region_dict():
    """
    Creates an empty Region dict.

    :return: A Dict describing a region of data. It contains the following
      fields:

      - start: Starting along-track index of bad region.
      - end: Ending along-track index of bad region.
      - reason: String describing why the region is bad.
      - state: TBD
      - perf: TBD

    :rtype: dict
    """
    return {'start': 0, 'end': 0, 'state': '', 'reason': '', 'perf': []}


def detect_height_anomaly(inp):
    """
    Detect ATR problematic data regions with height data.

    :param inp: MATS Input to be analyzed.
    :type inp: mats.Input

    :return: List of bad regions. Each region is described by a dict with the
      following fields:

      - start: Starting along-track index of bad region.
      - end: Ending along-track index of bad region.
      - reason: String describing why the region is bad.

    :rtype: [dict]
    """
    bad_regions = []
    if inp['nav_size'] == 0:
        return bad_regions
    blk_size = 100
    stable = True
    ht = inp.get_height()

    # Divide data into complete blocks
    num_blocks = round(inp['nav_size'] / blk_size)
    if num_blocks < 1:
        num_blocks = 1

    starts = numpy.zeros((num_blocks,), dtype=int)
    ends = numpy.zeros((num_blocks,), dtype=int)
    avgs = numpy.zeros((num_blocks,))
    stds = numpy.zeros((num_blocks,))
    keeps = numpy.zeros((num_blocks,), dtype=bool)

    for idx in range(num_blocks):
        starts[idx] = idx * blk_size
        ends[idx] = (idx+1) * blk_size
    ends[num_blocks-1] = inp['nav_size']

    # Get stats on each block
    # NOTE: Size of final block (2nd param to max()) will be larger than
    #   standard blk_size if num_blocks rounded down above.
    # maxSize = max(blk_size, ends[num_blocks-1] - starts[num_blocks-1])

    for idx in range(num_blocks):
        stds[idx] = numpy.std(ht[starts[idx]:ends[idx]])
        avgs[idx] = numpy.mean(ht[starts[idx]:ends[idx]])

        # Find blocks with big jumps; discard them
        # Quick-but-not-instantaneous drops so far have had std = 1.7-2.2
        if stds[idx] < 1.0:
            keeps[idx] = True
        else:
            keeps[idx] = False
            stable = False

    if stable:  # no jumps; must be relatively stable
        # NOTE: Original source had goto to finish section with free statements
        return bad_regions

    # Look for a jump in the middle
    midJump = False
    true_inds = numpy.nonzero(keeps)
    first_stable = true_inds[0][0]
    last_stable = true_inds[0][-1]

    if first_stable > -1 and first_stable < last_stable:
        for idx in range(first_stable+1, last_stable):
            if not keeps[idx]:
                midJump = True
                break
    if midJump:
        numel = numpy.zeros((10,), dtype=numpy.int)
        # Which stable areas are "normal"?
        # Find lowest and highest avg block heights that are being kept.
        avgL = avgs[first_stable]
        avgH = avgL
        num_work_blocks = 0
        for idx in range(first_stable, last_stable+1):  # incl. last_stable
            if keeps[idx]:
                avgL = min(avgL, avgs[idx])
                avgH = max(avgH, avgs[idx])
                num_work_blocks += 1
        # distance to next bin; should catch a little variation:
        buffer = (avgH - avgL) / 10.0
        # biggest must be a bit bigger than it would if uniform (trying to
        # split a stable area)
        thresh = num_work_blocks / 5.0  # 2*length(work_blocks)/length(nel)

        # Divide the heights into 10 bins.
        for idx in range(first_stable, last_stable+1):
            if keeps[idx]:
                idx2 = int(numpy.ceil(10.0 * (avgs[idx]-avgL) / (avgH-avgL)))
                if idx2 < 1:
                    idx2 = 1
                if idx2 > 10:
                    idx2 = 10
                numel[idx2-1] += 1
        biggest_bin_val = numpy.max(numel)  # NOTE: C code has combo subroutine
        maxind = numpy.argmax(numel)        # for these two

        if biggest_bin_val < thresh:
            # ambiguous case
            # Do nothing else; only the jumps will register as anomalies
            # (or should we throw out the whole image?)
            # NOTE: Original source had goto to finish section with free
            # statements
            return bad_regions
        normal_ref = avgL + (maxind + 0.5) * buffer

        # Discard blocks significantly different from the normal level (i.e.,
        # anomalous plateaus)
        for idx in range(first_stable, last_stable+1):
            if keeps[idx]:
                if abs(normal_ref - avgs[idx]) > buffer:
                    keeps[idx] = False
    # end if midJump
    # Else:  There may be a jump at one end of the image.  Assume the bulk of
    # the image is good.  (It could be that the entire image is an anomaly,
    # but that is unlikely.)

    avg_good_avg = 0
    avg_good_std = 0
    count = 0  # count of good blocks
    count2 = 0  # count of bad blocks

    for idx in range(num_blocks):
        if keeps[idx]:
            avg_good_avg += avgs[idx]
            avg_good_std += stds[idx]
            count += 1
        else:
            count2 += 1
    if count > 0:
        avg_good_avg /= count
        avg_good_std /= count

    # Determine bad regions from bad blocks

    # Initialize regions (objects in C)
    bad_regions = [region_dict() for q in range(count2)]
    l_idx = 0    # list index
    for idx in range(num_blocks):
        if not keeps[idx]:
            bad_regions[l_idx]['start'] = starts[idx]
            bad_regions[l_idx]['end'] = ends[idx] - 1  # index of last ping
            l_idx += 1

    # Merge adjacent blocks
    if len(bad_regions) > 1:
        l_idx = 1
        while l_idx != len(bad_regions):
            if bad_regions[l_idx]['start'] == bad_regions[l_idx-1]['end'] + 1:
                # previous block is adjacent -> absorb current block
                bad_regions[l_idx-1]['end'] = bad_regions[l_idx]['end']
                bad_regions.pop(l_idx)
            else:
                l_idx += 1

    # Try to expand regions outward to catch partial blocks
    for l_idx in range(len(bad_regions)):
        while bad_regions[l_idx]['start'] > 0 and abs(ht[bad_regions[l_idx]['start']] - avg_good_avg) > 2*avg_good_std:
            # stop when plausibly within stable region
            bad_regions[l_idx]['start'] -= 1
        while bad_regions[l_idx]['end'] < inp['nav_size'] - 1 and abs(ht[bad_regions[l_idx]['end']] - avg_good_avg) > 2*avg_good_std:
            # stop when plausibly within stable region
            bad_regions[l_idx]['end'] += 1

    # Add reason field to bad_regions;
    for l_idx in range(len(bad_regions)):
        bad_regions[l_idx]['state'] = "BAD"
        bad_regions[l_idx]['reason'] = "Sudden change in height detected"
    return bad_regions


def detect_turns_hb(mats_in, blk_sz=None, turn_ind=None, comp_turn=None):
    """
    Detect vehicle turning regions.

    :param mats_in: MATS Input to be analyzed.
    :type mats_in: mats.Input
    :param blk_sz: Block size for dividing data. Default is 100.
    :type blk_sz: int, optional
    :param turn_ind: Initial threshold for turn in radians. Default is 0.05.
    :type turn_ind: float, optional
    :param comp_turn: Turn threshold in radians for extending turn region.
                      Default is 0.01.
    :type comp_turn: float, optional

    :return: List of bad regions. Each region is described by a dict with the
      following fields:

      - start: Starting along-track index of bad region.
      - end: Ending along-track index of bad region.
      - reason: String describing why the region is bad.

    :rtype: [dict]
    """
    if blk_sz is None:
        blk_sz = 100
    if turn_ind is None:
        turn_ind = 0.05
    if comp_turn is None:
        comp_turn = 0.01

    min_gap = 250
    bad_regions = []
    if mats_in['nav_size'] <= 1:
        # if missing or global heading value, abort (I think only SSAM does
        # this, and operationally there are no turns in that data)
        return bad_regions

    # allocate space for head, based on the size in the input structure
    head = numpy.ndarray((mats_in['nav_size'],))
    head[0] = numpy.pi/float(180.0) * mats_in.heading(0)
    for idx in range(1, mats_in['nav_size']):
        # convert headings into radians
        head[idx] = numpy.pi/float(180.0) * mats_in.heading(idx)
        # smooth out jumps of more than pi
        # unwrapped heading (in radians)
        head[idx] = mats.basic.unwrap(head[idx-1], head[idx])

    # Divide data into complete blocks
    num_blocks = round(mats_in['nav_size'] / blk_sz)
    if num_blocks < 1:
        num_blocks = 1

    starts = numpy.ndarray((num_blocks,), dtype=numpy.int)
    ends = numpy.ndarray((num_blocks,), dtype=numpy.int)
    avgs = numpy.ndarray((num_blocks,))
    stds = numpy.ndarray((num_blocks,))
    keeps = numpy.ndarray((num_blocks,), dtype=numpy.bool)

    for idx in range(num_blocks):
        starts[idx] = idx * blk_sz
        ends[idx] = (idx+1) * blk_sz
    ends[num_blocks-1] = mats_in['nav_size']

    # The initial threshold for block is based on the standard deviation
    # of the heading
    count = 0   # keep track of number of bad regions
    for idx in range(num_blocks):
        stds[idx] = numpy.std(head[starts[idx]:ends[idx]])
        avgs[idx] = numpy.mean(head[starts[idx]:ends[idx]])
        # print('{} > {}'.format(stds[idx], turn_ind))
        if stds[idx] > turn_ind:
            keeps[idx] = False
            count += 1
        else:
            keeps[idx] = True

    # temp = [(starts[q], ends[q], keeps[q]) for q in range(num_blocks)]
    # print(temp)

    if count == 0:
        return bad_regions

    # Determine bad regions from bad blocks

    # Initialize regions (objects in C)
    bad_regions = [region_dict() for q in range(count)]
    l_idx = 0    # list index
    for idx in range(num_blocks):
        if not keeps[idx]:
            bad_regions[l_idx]['start'] = starts[idx]
            bad_regions[l_idx]['end'] = ends[idx] - 1  # index of last ping
            l_idx += 1

    # Merge adjacent blocks
    if len(bad_regions) > 1:
        l_idx = 1
        while l_idx < len(bad_regions):  # while l_idx != len(bad_regions):
            if bad_regions[l_idx]['start'] == bad_regions[l_idx-1]['end'] + 1:
                # previous block is adjacent -> absorb current block
                bad_regions[l_idx-1]['end'] = bad_regions[l_idx]['end']
                bad_regions.pop(l_idx)
            else:
                l_idx += 1

    # Expand turning mask to capture turn edges
    for l_idx in range(len(bad_regions)):
        this_reg = bad_regions[l_idx]
        prev_reg = bad_regions[max(l_idx-1, 0)]                     # aka, it2
        next_reg = bad_regions[min(l_idx+1, len(bad_regions)-1)]    # aka, it3
        # start of turn, expand backwards
        if this_reg['start'] > 0:
            # find length of stable values
            if l_idx == 0:
                section_length = this_reg['start']
                med = numpy.median(head[0:this_reg['start']])
            else:
                section_length = this_reg['start'] - prev_reg['end'] - 1
                med = numpy.median(head[prev_reg['end']+1:this_reg['start']])

            # inch backward
            count = 1   # make sure we don't go too far
            while (this_reg['start'] > 1 and count < section_length and
                    abs(head[this_reg['start']-1] - med) > comp_turn):
                this_reg['start'] -= 1
                count += 1
            this_reg['start'] -= 1  # to match MATLAB
        # end if

        # end of turn, expand forward
        if this_reg['end'] < mats_in['nav_size']-1:
            # find length of stable values
            if l_idx == len(bad_regions)-1:
                section_length = mats_in['nav_size'] - this_reg['end'] - 1
                med = numpy.median(head[this_reg['end']+1:mats_in['nav_size']])
            else:
                section_length = next_reg['start'] - this_reg['end'] - 1
                med = numpy.median(head[this_reg['end']+1:next_reg['start']])

            # inch forward
            count = 0   # make sure we don't go too far
            while (this_reg['end'] < mats_in['nav_size']-1 and count < section_length
                   and abs(head[this_reg['end']] - med) > comp_turn):
                this_reg['end'] += 1
                count += 1

    l_idx = 1
#    while l_idx != len(bad_regions)-1:
    while l_idx < len(bad_regions):
        if bad_regions[l_idx]['start'] - bad_regions[l_idx-1]['end'] <= min_gap:
            # adjacent previous block: shift this block onto previous; del this
            bad_regions[l_idx-1]['end'] = bad_regions[l_idx]['end']
            bad_regions.pop(l_idx)
        else:
            l_idx += 1

    # Add reason field to bad_regions;
    # Convert our list to a vector for output
    for l_idx in range(len(bad_regions)):
        head_f = head[bad_regions[l_idx]['end']]
        head_i = head[bad_regions[l_idx]['start']]
        turn_deg = int(numpy.round((head_f - head_i) * 180.0/numpy.pi))
        bad_regions[l_idx]['state'] = "BAD"
        bad_regions[l_idx]['reason'] = f"Turn detected (net {turn_deg} degrees)"

    return bad_regions


def get_contact_latlong(inp, x, y):
    """
    Determine the lat/long coordinates of a specified image location using
    vehicle data.

    .. note:: This version uses the geolocate() function.

    :param inp: MATS Input containing interpolated vehicle nav data.
    :type inp: mats.Input
    :param x: Cross-track index of contact (0-based).
    :type x: int
    :param y: Along-track index of contact (0-based).
    :type y: int

    :return: Latitude and longitude of (x,y) location (degrees).
    :rtype: (float, float)
    """
    if mats.cpp_backend:
        return mats.mc.get_contact_latlong(inp, x, y)

    if len(inp['data_names']) == 0:
        return None, None
    if y >= inp['nav_size']:
        print("Along-track index exceeds nav_len.")
        return None, None
    if inp['side'].upper() == "PORT":
        side_sign = -1
    else:
        side_sign = 1

    # Assume vehicle lat/long and heading are given in degrees.
    heading = inp['heading'][y] * numpy.pi / 180.0
    altitude = inp['height'][y]
    ref_image = inp.data(inp['ref_name'])
    rng = side_sign * (x+1) * ref_image['cres']
    # Convert to radians temporarily for geolocate
    veh_lat = inp['lat'][y] * numpy.pi / 180.0
    veh_long = inp['lon'][y] * numpy.pi / 180.0
    print('x = {}; range = {}'.format(x, rng))
    print('y = {}'.format(y))
    lat, lng = mats.geo.geolocate(veh_lat, veh_long, heading, 0, rng, altitude)
    lat = lat * 180.0 / numpy.pi
    lng = lng * 180.0 / numpy.pi
    return lat, lng


def prune_duplicate_contacts(conlist, ecdlist):
    """
    Remove duplicate contacts from a contact list using the ecdata.groupnum
    field.  If multiple contacts have the same groupnum value, only the one
    with the highest classifier confidence is retained and the others in that
    group are discarded from the contact list as well as the corresponding
    ecdata.
    
    :param conlist: MATS Contact List to be pruned.
    :type conlist: mats.ContactList
    :param ecdlist: MATS Ecdata List corresponding to `conlist`.
    :type ecdlist: mats.EcdataList

    :return: True if changes have been made to conlist/ecdlist.
    """
    if mats.cpp_backend:
        return mats.mc.prune_duplicate_contacts(conlist, ecdlist)

    # Assume lists are properly synchronized
    assert(len(conlist) == len(ecdlist))
    id_match = [conlist[q]['uuid'] == ecdlist[q]['uuid']
                for q in range(len(conlist))]
    assert(all(id_match))

    rem_mask = numpy.zeros((len(conlist),), dtype=bool)
    used_mask = numpy.zeros((len(conlist),), dtype=bool)
    scores = [x['classconf'] for x in conlist]
    if any([x < 0 for x in scores]):
        scores = [x['detscore'] for x in ecdlist]
    for q in range(len(conlist)):
        # Skip to next if this contact has already been examined as part
        #   of an earlier group
        if used_mask[q]:
            continue
        # Determine how many contacts have this group number
        grp_inds = [x for x in range(len(ecdlist))
                    if ecdlist[x]['groupnum'] == ecdlist[q]['groupnum']]
        if len(grp_inds) == 1:
            used_mask[q] = True
        else:
            # print('grp_inds = {}'.format(grp_inds))
            # grp_confs = [scores[x] for x in grp_inds]
            # print('grp_confs = {}'.format(grp_confs))
            # Find highest confidence contact
            max_ind = grp_inds[0]
            max_val = scores[max_ind]
            for k in range(1, len(grp_inds)):
                if scores[grp_inds[k]] > max_val:
                    max_ind = grp_inds[k]
                    max_val = scores[grp_inds[k]]
            # Mark ones with lower classconf for deletion
            for k in range(len(grp_inds)):
                used_mask[grp_inds[k]] = True
                if grp_inds[k] != max_ind:
                    rem_mask[grp_inds[k]] = True
    inds_to_remove = [x for x in range(len(conlist)) if rem_mask[x]]  # increasing
    # print('inds_to_remove = {}'.format(inds_to_remove))
    # uuids_to_remove = [conlist[q]['uuid'] for q in inds_to_remove]
    # print('uuids_to_remove = {}'.format(uuids_to_remove))
    # Remove contacts and ecdata marked for deletion in reverse order
    # (Otherwise desired indices might shift as contacts are removed)
    for q in inds_to_remove[::-1]:
        conlist.pop(q)
        ecdlist.pop(q)
    return len(inds_to_remove) > 0


def sort_contacts(conlist, ecdlist):
    """
    Sorts MATS Contact and Ecdata Lists by along-track index.

    :param conlist: MATS ContactList to be sorted.
    :type conlist: mats.ContactList
    :param ecdlist: MATS EcdataList to be sorted.
    :type ecdlist: mats.EcdataList
    """
    if mats.cpp_backend:
        return mats.mc.sort_contacts(conlist, ecdlist)

    # Get indices for reordering contacts and ecdata
    dec = [(con['y'], q) for q, con in enumerate(conlist)]
    dec.sort()
    inds = [d[1] for d in dec]

    # Since this function doesn't return anything, move contacts/ecdata out of
    #   provided lists and repopulate in a reordered fashion
    temp_con = []
    temp_ecd = []
    for q in range(len(conlist)):
        temp_con.append(conlist.pop(0))
        temp_ecd.append(ecdlist.pop(0))
    for q in inds:
        conlist.append(temp_con[q])
        ecdlist.append(temp_ecd[q])


def group_contacts(inp, contacts, ecdata):
    """
    Contact correlation phase. Group-related values will be modified.

    :param inp: MATS Input corresponding to contacts and ecdata.
    :type inp: mats.Input
    :param contacts: Vector of contacts to be grouped.
    :type contacts: mats.ContactList
    :param ecdata: Vector of ecdata objects, corresponding to contacts.
    :type ecdata: mats.EcdataList
    """
    if mats.cpp_backend:
        return mats.mc.group_contacts(inp, contacts, ecdata)

    if contacts.size() == 0:
        return 0  # no contacts
    if len(inp['data_names']) == 0:
        return 1  # no data

    # Setup options to be passed to roiFind.
    opt = mats.Struct()
    opt['ROIBuffer'] = 0.05

    # Allocate storage for roiFind
    n = contacts.size()
    loc = numpy.zeros((2*n,))
    scores = numpy.zeros((n,))
    # labels = numpy.ones((n,), dtype=numpy.int)
    roiDim = numpy.zeros((2,))
    dataDim = numpy.zeros((2,))
    # Translate contacts and ecdata into roiFind() inputs.
    ref_data = inp.data(inp['ref_name'])
    for k in range(n):
        loc[2*k] = (contacts[k]['x']+1) * ref_data.cres
        loc[2*k+1] = (contacts[k]['y']+1) * ref_data['ares']
        scores[k] = 1.0

    # TODO(Bradley): hard-coded roiDim for Edgetech
    roiDim[0] = 2.5
    roiDim[1] = 2.5  # in meters
    dataDim[0] = ref_data['anum']*ref_data['ares']
    dataDim[1] = ref_data['cnum']*ref_data['cres']

    labels, rois = mats.cluster.roi_find(loc, scores, roiDim, dataDim, opt)
    for roi in rois:
        print(roi)

    # Translate roiFind() outputs into contacts and ecdata.
    for k in range(n):
        print('------ {} ------'.format(k))
        lab = numpy.uint8(labels[k])
        ecdata[k]['groupnum'] = lab
        if lab > 0:
            print('label = {}'.format(lab))
            print('x = {}; y = {}'.format(contacts[k]['x'], contacts[k]['y']))
            x_px = numpy.floor(rois[lab-1].x/ref_data['cres'])
            group_x = numpy.uint32(max(1.0, x_px) - 1)
            y_px = numpy.floor(rois[lab-1].y/ref_data['ares'])
            group_y = numpy.uint32(max(1.0, y_px) - 1)
            (lat, lng) = get_contact_latlong(inp, group_x, group_y)
            # TODO: CHECK OUTPUTS
            ecdata[k]['grouplat'] = lat
            ecdata[k]['grouplon'] = lng
    return 0


def data_integ_verif_phase(inp):
    """
    Data Integrity Verification (DIV) Phase:
    Analyze the input data and determine which ping ranges have corrupt or
    unusable data (e.g., turns, sudden spikes in vehicle data).

    :param inp: MATS Input to be analyzed.
    :type inp: mats.Input

    :return: List of bad regions. Each region is described by a dict. See
        `region_dict` for a description of the dict.
    :rtype: [dict]
    """
    if mats.cpp_backend:
        return mats.mc.data_integ_verif_phase(inp)

    if inp['nav_size'] < 600:
        mats.log.warn("Skipping DIV due to data length.")
        return None

    turn_rejects = []
    bad_regions = []
    if inp['sensor'] == "EDGETECH-850":
        bad_regions = detect_height_anomaly(inp)
        turn_rejects = detect_turns_hb(inp)
    elif inp['sensor'] in ["MARINESONIC", "MARINESONIC-900", "MARINESONIC-1800"]:
        bad_regions = detect_height_anomaly(inp)
        turn_rejects = detect_turns_hb(inp, 50, 0.3, 0.05)

    # Otherwise, no DIV modules are run.
    # TODO(Bradley): Add detect_bad_image_data() for iRadar data.
    # TODO(Bradley): Select which DIV functions to use based on the sensor.

    # join arrays
    if len(turn_rejects) > 0:
        bad_regions.extend(turn_rejects)
    mats.log.info("Number of detected bad regions: {}".format(len(bad_regions)))

    return bad_regions


def calc_sweetspot(inp):
    """
    Calculates the area of the image (in range) which is most suitable to ATR.
    The calculation uses a different method for different sensors. The values
    are put into the MATS Input.

    :param inp: A MATS Input to have its sweetspot field set.
    :type inp: mats.Input
    """
    try:
        sensor = mats.sensor.mats_sensor(inp.sensor)
        sensor.sweetspot(inp)
    except RuntimeError:
        mats.log.warn("Failed to retrieve Sensor. Using default calc_sweetspot")
        default_sweetspot(inp)
    return


def input_chunk(inp, starts, ends):
    chunk = mats.Input()
    chunk.filename = inp.filename
    # self._ref_name = indata['ref_name']
    # DK Modification for running PSO code
    chunk['sensor'] = inp.sensor
    chunk.side = inp['side']
    # chunk.sensor = inp.sensor
    # chunk.side = inp.side

    chunk.allocate_nav(ends-starts+1)
    chunk.get_lat()[:] = inp.get_lat()[starts:ends+1]
    chunk.get_lon()[:] = inp.get_lon()[starts:ends+1]
    chunk.get_heading()[:] = inp.get_heading()[starts:ends+1]
    chunk.get_time()[:] = inp.get_time()[starts:ends+1]
    chunk.get_height()[:] = inp.get_height()[starts:ends+1]
    chunk.get_depth()[:] = inp.get_depth()[starts:ends+1]

    ref_anum = inp.data(inp['ref_name']).anum
    for dn in inp['data_names']:
        chunk.add_data(dn)
        chunk.data(dn).ares = inp.data(dn).ares
        chunk.data(dn).cres = inp.data(dn).cres
        chunk.data(dn).storage = inp.data(dn).storage
        chunk.data(dn).format = inp.data(dn).format
        chunk.data(dn).precision = inp.data(dn).precision

        if dn == inp['ref_name']:
            x0 = starts
            x1 = ends
        else:
            anum = inp.data(dn).anum
            x0 = max(0, round(starts * anum / ref_anum))
            x1 = min(anum - 1, round(ends * anum / ref_anum))
        # NOTE: Using x1+1 because the index range above is inclusive and python
        # ':' operator excludes end range.
        chunk.data(dn).load_data(inp.data(dn).data[x0:x1+1, :])

    # sweetspot adjustment
    mats.core.calc_sweetspot(chunk)
    return chunk


def input_chunk_apply(chunk, starts, ends, inp):
    for dname in inp.data_names:
        # Copy chunk data back to original MATS_input.
        (anum, cnum) = inp.data(dname).size()

        # Make sure we still have the same format, etc.
        chunk.data(dname).precision = inp.data(dname).precision
        chunk.data(dname).storage = inp.data(dname).storage
        chunk.data(dname).format = inp.data(dname).format

        cd0 = chunk.data(dname).component(0)
        # NOTE: It is 'ends+1' because we want to include last index.
        inp.data(dname).component(0)[starts:ends+1, :] = cd0
        if chunk.data(dname).is_complex():
            cd1 = chunk.data(dname).component(1)
            inp.data(dname).component(1)[starts:ends+1, :] = cd1
    return
