# DISTRIBUTION STATEMENT D. Distribution authorized to the Department of
# Defense and U.S. DoD contractors only; Administrative or Operational Use; 1
# Jan 2017. Other U.S. requests shall be referred to Naval Surface Warfare
# Center Panama City Division, ATTN: Technical Director NSWC PCD, 110 Vernon
# Ave, Panama City, FL 32407.
"""
mats.cluster
------------
Contains classes and functions related to clustering.
"""
import numpy
import copy
import mats


class ROI:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.a_start = 0.0
        self.a_stop = 0.0
        self.c_start = 0.0
        self.c_stop = 0.0
        self.score = 0.0
        self.count = 0

    def __str__(self):
        s = 'ROI: center @ ({},{})'.format(self.x, self.y)
        s += '\n     box = [{}:{}, {}:{}]'.format(self.c_start, self.c_stop,
                                                  self.a_start, self.a_stop)
        s += '\n     count = {}'.format(self.count)
        s += '\n     score = {}'.format(self.score)
        return s


class ROIList:
    def __init__(self):
        self.data = []

    def __repr__(self):
        return 'MATS_ROI_list ({0} contacts)'.format(self.size())

    def __getitem__(self, index):
        if int(index) == index:  # handle numpy integer types
            index = int(index)
        if type(index) is not int:
            raise TypeError('Index must be an integer')
        if index < 0 or index >= self.size():
            raise IndexError('Index is out of range')
        return self.data[index]

    def __setitem__(self, index, value):
        if int(index) == index:  # handle numpy integer types
            index = int(index)
        if not type(index) is int:
            raise TypeError('Index must be an integer')
        if index < 0 or index >= self.size():
            raise IndexError('Index is out of range')
        if type(value) is not ROI:
            raise TypeError('value must be an ROI object')
        self.data[index] = value

    def __iter__(self):
        for key in range(self.size()):
            yield self[key]

    def __len__(self):
        return self.size()

    def clear(self):
        self.data.clear()

    def resize(self, new_len):
        if type(new_len) is not int and new_len > 0:
            raise TypeError('Index must be a positive integer')
        n = self.size()
        new_data = [self.data[x]
                    if x < n else ROI() for x in range(new_len)]
        self.data = new_data

    def size(self):
        return len(self.data)

    def append(self, value):
        if type(value) is not ROI:
            raise TypeError('value must be an Ecdata object')
        self.data.append(copy.deepcopy(value))

    def pop(self, index=None):
        return self.data.pop(index)

    # Find the index of the closest element to the reference data
    def closest(self, queries, thresh=None):
        if thresh is None:
            thresh = 0
        out_inds = []
        out_errs = []
        for q in range(len(queries)):
            # print('Looking for {}'.format(queries[q]))
            # query = {'x': queries[q][0], 'y': queries[q][1]}
            query = queries[q]
            print('query #{} = {}'.format(q, query))
            diff = [dist_euclidean_alt(self[k].x,  self[k].y, query['x'], query['y']) for k in range(len(self))]
            # diff_strs = ['{:.3f}'.format(x) for x in diff]
            # print('diff = [{}]'.format(', '.join(diff_strs)))
            # print('diff = {}'.format(diff))
            min_idx = numpy.argmin(diff)
            print('min_idx = {}'.format(min_idx))
            if abs(diff[min_idx]) <= thresh:
                out_inds.append(min_idx)
                out_errs.append(diff[min_idx])
            else:
                out_inds.append(None)
                out_errs.append(diff[min_idx])
        return out_inds, out_errs

    def __str__(self):
        str_list = []
        for q in range(min(99, len(self.data))):
            r = self.data[q]
            str_q = 'ROI #{} @ [{:.3f}|{:.4f}|{:.3f}, {:.3f}|{:.4f}|{:.3f}], N={}, S={:.4f}'.format(q,
                        r.c_start, r.x, r.c_stop, r.a_start, r.y, r.a_stop,
                        r.count, r.score)
            str_list.append(str_q)
        return '['+',\n '.join(str_list)+']'


def dist_euclidean_alt(x1, y1, x2, y2):
    xdiff = x1 - x2
    ydiff = y1 - y2
    return numpy.sqrt(xdiff*xdiff + ydiff*ydiff)


def dist_euclidean(roi1, roi2):
    xdiff = roi1.x - roi2.x
    ydiff = roi1.y - roi2.y
    return numpy.sqrt(xdiff*xdiff + ydiff*ydiff)


def dist_chebyshev(roi1, roi2):
    return max(abs(roi1.x - roi2.x), abs(roi1.y - roi2.y))


# loc, labels, and scores are numpy arrays
# contents of roi list should change
def centerROIs(n, loc, labels, scores, sig, roi):
    # print('... centerROIs ...')
    for k in range(roi.size()):
        roi[k].score = 0.0
        # Copy data for easy calculations
        x = numpy.zeros((2*roi[k].count,))  # this ROI's locations
        w = numpy.zeros((roi[k].count,))    # this ROI's scores
        ix = 0
        for j in range(n):
            # If this point is in current ROI, copy to next available spot in
            #   working data arrays x and w
            if k == labels[j] - 1:
                # print('ix = {}, j = {}, len(x) = {}, len(loc) = {}'.format(ix, j, len(x), len(loc)))
                # print('loc[2*j] = {}'.format(loc[2*j]))
                x[2*ix] = loc[2*j]
                x[2*ix+1] = loc[2*j+1]
                if scores is not None:
                    w[ix] = scores[j]
                    roi[k].score += scores[j]
                else:
                    w[ix] = 1
                    roi[k].score += 1
                ix += 1
        # Start at least squares solution
        roi[k].x = 0.0
        roi[k].y = 0.0
        for j in range(roi[k].count):
            roi[k].x += w[j]*x[2*j]/roi[k].score
            roi[k].y += w[j]*x[2*j+1]/roi[k].score
        # iterate to form weighted least squares solution
        for j in range(5):
            # compute weights based on distance from box center
            roi[k].score = 0.0
            for i in range(roi[k].count):
                xdiff = x[2*i] - roi[k].x
                ydiff = x[2*i+1] - roi[k].y
                w[i] = xdiff*xdiff + ydiff*ydiff
                w[i] = numpy.exp(-w[i]/sig)
                roi[k].score += w[i]
            if roi[k].score > 0:
                roi[k].x = 0.0
                roi[k].y = 0.0
                for i in range(roi[k].count):
                    roi[k].x += w[i]*x[2*i]/roi[k].score
                    roi[k].y += w[i]*x[2*i+1]/roi[k].score
            else:
                break
    return


# roiDim and dataDim are numpy arrays
def findBox(roi, roiDim, dataDim):
    width_buff = (roiDim[1] - 1.0)/2.0
    height_buff = (roiDim[0] - 1.0)/2.0

    # Find outer-most snippet centers
    # minx = numpy.ceil(width_buff)   # left-most valid center
    # miny = numpy.ceil(height_buff)  # top-most valid center
    # maxx = dataDim[1] - numpy.floor(width_buff) - 1.0   # right-most valid center
    # maxy = dataDim[0] - numpy.floor(height_buff) - 1.0  # bottom-most valid center
    minx = width_buff + 1   # left-most valid center
    miny = height_buff + 1  # top-most valid center
    maxx = dataDim[1] - width_buff      # right-most valid center
    maxy = dataDim[0] - height_buff     # bottom-most valid center

    for k in range(roi.size()):
        # Adjust center position if near an edge of the image
        roi[k].x = max(min(roi[k].x, maxx), minx)
        roi[k].y = max(min(roi[k].y, maxy), miny)

        # roi[k].c_start = roi[k].x - numpy.ceil(width_buff)
        # roi[k].c_stop = roi[k].x + numpy.floor(width_buff)
        # roi[k].a_start = roi[k].y - numpy.ceil(height_buff)
        # roi[k].a_stop = roi[k].y + numpy.floor(height_buff)
        roi[k].c_start = roi[k].x - width_buff
        roi[k].c_stop = roi[k].x + width_buff
        roi[k].a_start = roi[k].y - height_buff
        roi[k].a_stop = roi[k].y + height_buff
    return


def updateROIs(n, loc, labels, scores, sig, roi):
    if len(roi) == 0: return

    # Drop any empty ROIs
    ix = 0
    while ix < roi.size():
        if roi[ix].count > 0:   # Not empty --> skip to next ROI in list
            ix += 1
            continue
        # Remove ROI
        roi.pop(ix)
        # Shift labels back
        for k in range(n):
            if labels[k] > ix + 1:
                labels[k] -= 1
    # Find ROI centers
    centerROIs(n, loc, labels, scores, sig, roi)
    return


def roiMove(to_ind, from_ind, n, labels, roi):
    if to_ind == from_ind: return   # nothing to move

    if to_ind > from_ind:   # switch, so to index will be before from index
        k = to_ind
        to_ind = from_ind
        from_ind = k

    # Update ROI counts
    roi[to_ind].count += roi[from_ind].count
    roi[from_ind].count = 0
    # Relabel data (shift by 1 b/c groups start at 1, indices start at 0)
    for k in range(n):
        if labels[k] == from_ind + 1:
            labels[k] = to_ind + 1
    # ROI will get removed on update because count is zero.
    return


def roi_find(inLoc, inScore, roiDim, dataDim, opt):
    """
    Group image points of interest into non-overlapping ROIs.

    .. note:: Points of interest matrix (`inLoc`) order is different from the
       order used in the MATLAB version of function.

       Function behavior is different depending on type of `roiDim` and
       `dataDim`. Using integers for `roiDim` and `dataDim` will cause the
       function to behave like MATLAB's ``roiFind``. Using float or double for
       these parameters will cause the function to behave like MATLAB's
       ``roiFindm``.

       If the number of points is greater than the limit (currently 2000), the
       entries of `labels` will be reordered relative to the entries of `loc`
       and `scores`. Specifically, the first 2000 entries of `labels` will
       correspond to the highest 2000 entries of `scores`, in order of
       decreasing `scores`. In this case, only the first 2000 entries of
       `labels` will be filled in.

    :param inLoc: Array of pixel locations of points of interest to be grouped
        into ROIs, e.g., [x1 y1 x2 y2 ...]. Matrix dimensions should be 2 by the
        number of points.
    :type inLoc: numpy.ndarray
    :param inScore: Array of weights indicating importance of points in `loc`
        (higher value means more important). Values are used to center ROIs on
        the more important points.
    :type inScore: numpy.ndarray
    :param roiDim: Dimensions of ROI box [along-track, cross-track].
    :type roiDim: numpy.ndarray
    :param dataDim: Dimensions of data to restrict ROIs [anum cnum].
    :type dataDim: numpy.ndarray
    :param opt: Optional parameter overrides.
    :type opt: mats.Struct

    :return: Group labels assigned to `inLoc` point of interest and ROIs.
    :rtype: (numpy.ndarray, numpy.ndarray)
    """
    if mats.cpp_backend:
        return mats.mc.roi_find(inLoc, inScore, roiDim, dataDim, opt)
    raise NotImplementedError('Python implementation incomplete.')
#    int* labels, std::vector<mats::MATS_roi>& rois)

    MAXITER = 200   # max number of iterations before we give up
    LIMIT = 2000    # maximum number of points to group
    iter_num = 0

    # Compute maxClusters for initial clustering
    maxClusters = int(min(20.0, numpy.floor(n*0.1)))
    labels = numpy.zeros((n,), dtype=numpy.int)

#  // TODO(Bradley): Test the case where n > LIMIT.
#  if (n > LIMIT) {
#    size_t *bigInds;  // temp sorting index vector
#    size_t ix;
#    double *newloc, *newscores;
#    std::stringstream msg;
#
#    msg << "More than " << LIMIT << " points.  Limiting to first " << LIMIT
#        << ".";
#    mats_log(MATS_WARN, msg.str().c_str());
#
#    // Allocate new arrays.
#    newloc = new double[2*LIMIT];
#    newscores = new double[n];
#    bigInds = new size_t[n];
#
#    for (k=0; k < n; k++)
#      newscores[k] = inScore[k];
#
#    // Sort scores and loc.
#    mats::sort_with_indices(n, newscores, bigInds);  // ascending order
#    for (k = 0; k < LIMIT; k++) {
#      ix = bigInds[n-1-k];
#      newloc[2*k] = inLoc[2*ix];
#      newloc[2*k+1] = inLoc[2*ix+1];
#      newscores[k] = newscores[n-1-k];  // scores already sorted
#    }
#    delete[] bigInds;
#
#    // Transfer ownership to const double pointers.
#    loc = newloc;
#    scores = newscores;
#    n = LIMIT;
#    limited = true;
#  } else {
    loc = inLoc
    scores = inScore
#  }

    # NOTE: We are using euclidean distance because its easier.
    rad = max(roiDim[0]/2.0, roiDim[1]/2.0)
    sig = max(rad/4.0, 1.0)
    sig = 2*sig*sig
    ROIBuffer = max(max(roiDim[0]/2.0, roiDim[1]/2.0), 10)

    # Load option changes given
    if opt is not None:
        if "ROIBuffer" in opt: ROIBuffer = opt["ROIBuffer"]
        ROIThres = int(opt["ROIThres"]) if "ROIThres" in opt else 0

    print("rad: {}".format(rad))
    print("sig: {}".format(sig))
    print("ROIBuffer: {}".format(ROIBuffer))
    print("maxClusters: {}".format(maxClusters))

    rois = ROIList()
    # We don't have to do much if only a single point given.
    if n == 1:
        labels[0] = 1
        rois.resize(1)
        rois[0].count = 1
        centerROIs(n, loc, labels, scores, sig, rois)
        findBox(rois, roiDim, dataDim)
        return (labels, rois)

    # Start by just assigning points to groups.
    if maxClusters > 0:
        rois.resize(maxClusters)
    else:
        rois.resize(n)
    for k in range(n):
        # A label of 0 means the point is ungrouped
        # (see prune_duplicate_contacts() in MATS_core).
        if maxClusters > 0:
            # NOTE: I think this was supposed to be (k-1) though it doesn't
            # matter
            labels[k] = ((k+1) % maxClusters) + 1
        else:
            labels[k] = k + 1
        rois[labels[k]-1].count += 1
    print('ROIS before initial update:\n{}'.format(rois))
    updateROIs(n, loc, labels, scores, sig, rois)
    print('ROIS after initial update:\n{}'.format(rois))

    # Determine the center of each ROI.
    while iter_num < MAXITER:
        print("Num ROIs: {}".format(rois.size()))
        ccChk = 0

        # Check clusters and see if any are too close to each other
        # (need more than one cluster to do this)
        if rois.size() > 1:
            for k in range(rois.size()):
                if rois[k].count == 0: continue
                for j in range(rois.size()):
                    if rois[j].count == 0: continue

                    if j != k:
                        # Compute distance between ROIs.
                        dist = dist_chebyshev(rois[k], rois[j])  # TODO

                        if dist < rad:
                            print('Removing ROI')
                            roiMove(k, j, n, labels, rois)
                            ccChk = -1
                # end j loop
                if ccChk < 0: break
            # end k loop
            if ccChk < 0:
                # print('Before post-removal update:\n{}'.format(rois))
                updateROIs(n, loc, labels, scores, sig, rois)
                # print('After post-removal update\n{}'.format(rois))
                ccChk = 0
            else:
                ccChk = 1

        # Check if we can form new ROI from points that are way outside ROIs.
        for k in range(rois.size()):
            mdist = 0
            mix = -1
            for j in range(n):
                if k + 1 == labels[j]:
                    # Dist. from ROI = the largest 1-D dist. from ROI
                    xdiff = abs(rois[k].x - loc[2*j])
                    ydiff = abs(rois[k].y - loc[2*j+1])
                    dist = max(xdiff, ydiff)

                    if dist > rad+ROIBuffer and dist > mdist:
                        mix = j
                        mdist = dist
            # end j loop
            # Check if we need to add an ROI.
            if mix >= 0:
                # print("  Added ROI #{}".format(rois.size() + 1))
                roi = ROI()
                rois[labels[mix]-1].count -= 1
                labels[mix] = rois.size() + 1
                roi.x = loc[2*mix]
                roi.y = loc[2*mix+1]
                roi.count = 1
                rois.append(roi)
                print("  Added ROI #{} @ ({}, {})".format(rois.size(), roi.x, roi.y))
                ccChk = 0
        # end k loop
        # regroup based on distance to ROIs
        for k in range(rois.size()):
            rois[k].count = 0

        for k in range(n):
            mix = 0
            xdiff = abs(rois[0].x - loc[2*k])
            ydiff = abs(rois[0].y - loc[2*k+1])
            mdist = max(xdiff, ydiff)

            for j in range(1, rois.size()):
                xdiff = abs(rois[j].x - loc[2*k])
                ydiff = abs(rois[j].y - loc[2*k+1])
                dist = max(xdiff, ydiff)

                if dist < mdist:
                    mix = j
                    mdist = dist
            labels[k] = mix + 1
            rois[mix].count += 1
        # end k loop
        updateROIs(n, loc, labels, scores, sig, rois)
        if ccChk:
            break

        iter_num = iter_num + 1
    # end of while

    if iter_num == MAXITER:
        print("roiFind: Reach max iteration")
        updateROIs(n, loc, labels, scores, sig, rois)

    # remove ROIs with 1 or less points
    j = 0
    while j < rois.size():
        if rois[j].count > ROIThres:
            j += 1
            continue
        # Remove ROI
        print('removing small roi')
        rois.pop(j)

        # Shift labels back; unlabel points from the cut ROI
        for k in range(n):
            if labels[k] > j+1:
                labels[k] -= 1
            elif labels[k] == j+1:
                labels[k] = 0
    # end while
    # form ROIs box
    findBox(rois, roiDim, dataDim)

    return labels, rois
