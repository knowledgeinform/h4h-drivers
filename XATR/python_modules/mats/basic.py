# DISTRIBUTION STATEMENT D. Distribution authorized to the Department of
# Defense and U.S. DoD contractors only; Administrative or Operational Use; 1
# Jan 2017. Other U.S. requests shall be referred to Naval Surface Warfare
# Center Panama City Division, ATTN: Technical Director NSWC PCD, 110 Vernon
# Ave, Panama City, FL 32407.
"""
mats.basic
__________
This submodule provides basic match functions used by many MATS functions.
Function availablity may depend on if the PyMATS_core extension is available.
"""
import math
import scipy.ndimage
import scipy.signal
import numpy as np
try:
    import skimage.measure
    __SKIMAGE = True
except ModuleNotFoundError:
    __SKIMAGE = False

import mats


def isintegerable(x):
    """
    Returns true if x can successfully be converted into a Python integer type.

    :param x: Variable to be checked.
    :return:
    """
    try:
        return int(x) == x
    except:     # x is a non-numeric type
        return False


def isfloatable(x):
    """
    Returns true if x can successfully be converted into a Python float type.

    :param x: Variable to be checked.
    :return:
    """
    try:
        return float(x) == x
    except:     # x is a non-numeric type
        return False


def unwrap(first, second):
    corrected_value = second
    diff = second - first
    while abs(diff) > np.pi:
        sign = -1.0 if diff > 0 else 1.0
        corrected_value += sign * 2.0 * np.pi
        diff = corrected_value - first
    return corrected_value


def symmetric_pad2(data, rpad, cpad):
    """
    Symmetric extention padding of a 2-D array with rpad on top/bottom and cpad
    on left/right.  Data is assumed to be in column-major storage. The output
    array is of size (nr + 2*rpad, nc + 2*cpad).

    :param data: The image to be padded.
    :type data: numpy.array
    :param rpad: Padding size for top and bottom.
    :type rpad: int
    :param cpad: Padding size for left and right.
    :type cpad: int
    :return: The padded image.
    :rtype: numpy.array
    """
    if mats.cpp_backend:
        return mats.mc.symmetric_pad2(data, rpad, cpad)
    return np.pad(data, [rpad, cpad], mode='symmetric')


def gau_fit(img):
    """
    Calculate mean and standard deviation after removing outliers.

    .. note::
       Returns may differ slightly from C code if using Python backend due to
       Numpy mean and standard deviation implementation differences.

    :param img: Data array.
    :type img: numpy.array
    :return: Tuple with mean and standard deviation removing outliers.
    :rtype: (float, float)
    """
    if mats.cpp_backend:
        return mats.mc.gau_fit(img)

    n = img.size
    if n < 10:
        # Small data set --> use all values
        mu = np.mean(img)
        sig = np.std(img)
        return mu, sig

    data = img.astype(dtype=float, order='F')
    data = data.ravel()
    data.sort()
    # Remove extreme points
    idx1 = 0
    idx2 = n-1
    for k in range(20):
        mu = np.mean(data[idx1:idx2+1])
        sig = np.std(data[idx1:idx2+1])

        while data[idx1] < mu - 3*sig:
            idx1 = idx1 + 1
        while data[idx2] > mu + 3*sig:
            idx2 = idx2 - 1
    mu = np.mean(data[idx1:idx2+1])
    sig = np.std(data[idx1:idx2+1])
    return mu, sig


def medfilt2(img, filt_size, mode=None):
    """
    Perform median filtering of a 2-D image. Constant mode uses a contant zero
    boundary extention.

    :param img: The image to be filtered.
    :type img: numpy.array
    :param filt_size: Size of filter in each dimension.
    :type filt_size: list
    :param mode: Boundary extention method to use. Default is constant.
    :type mode: {'constant', 'symmetric'}, optional
    :return: The filtered image (same size as `data`).
    :rtype: numpy.array
    """
    if mode is None:
        mode = 'constant'
    if mode not in ['constant', 'symmetric']:
        raise ValueError('mode must be "constant" or "symmetric".')

    if mats.cpp_backend:
        if mode == 'constant':
            return mats.mc.medfilt2(img, filt_size)
        else:
            return mats.mc.medfilt2_symmetric(img, filt_size)
    if mode == 'constant':
        return scipy.ndimage.median_filter(img, filt_size, mode='constant',
                                           cval=0.0)
    return scipy.ndimage.median_filter(img, filt_size, mode='reflect')


# 2D convolution
def conv2(A, B):
    # NOTE: This module function is very close to C implementation, but it
    # trims the output slightly differently when using the 'same' mode, so
    # we'll trim ourselves
    out = scipy.signal.convolve(A, B)
    M, N = B.shape
    if M % 2 == 0:
        top = int(M/2)
        bottom = int(M/2) - 1
    else:
        top = int((M-1)/2)
        bottom = int((M-1)/2)
    if N % 2 == 0:
        left = int(N/2)
        right = int(N/2) - 1
    else:
        left = int((N-1)/2)
        right = int((N-1)/2)
    # print('[{}:{}, {}:{}]'.format(top, bottom, left, right))
    out_rows, out_cols = out.shape
    return out[top:out_rows-bottom, left:out_cols-right]


def imfilter(data, filt):
    """
    Perform 2-D correlation.  The output image is the same size as the input
    image, taken from the central part of the correlation.

    .. note::
       This is comparable to calling MATLAB's imfilter with options 'same' and
       'circular'.
    .. note::
       This function uses the FFTW planner. If the library is compiled with
       threading enabled, this function is thread-safe provided that any other
       uses of the FFTW planner use the mats_lock_fftw() and mats_unlock_fftw()
       functions. If the library is compiled without threading enabled, this
       function is not thread-safe and must not be run simultaneously with other
       uses of the FFTW planner.

    :param data: The image to be filtered.
    :type data: array-like
    :param filt: The filter to convolve with the image.
    :type filt: array-like
    :return: The filtered image (same size as `data`).
    :rtype: array-like
    """
    # if mats.cpp_backend:
    #     return mats.mc.imfilter(data, filt)
    return scipy.ndimage.correlate(data, filt, mode='wrap')


# Welford's Algorithm for single-pass variance calculation. */
def __ol_var_add(s, data):
    for val in data.flatten():
        s['N'] += 1
        dx = val - s['Mx']
        s['Mx'] += dx/s['N']
        s['Vx'] += dx*(val-s['Mx'])
    return


# Removes values from previous variance calculation.
def __ol_var_remove(s, data):
    for val in data.flatten():
        if s['N'] == 0:
            # mats.log.error("No samples to remove.")
            return
        elif s['N'] == 1:
            s['N'] = 0
            s['Mx'] = 0.0
            s['Vx'] = 0.0
        else:
            dx = val - s['Mx']
            s['Mx'] = (s['N']*s['Mx']-val)/(s['N']-1)
            s['Vx'] -= dx*(val - s['Mx'])
            s['N'] -= 1
    return


def __ol_var(s):
    v = s['Vx']/(s['N'] - 1)
    if v < 0.0:
        return 1e-16
    return v


def __ring_window_slide(core_rad, ring_rad, r, img):
    print('START RING {}'.format(r))
    nr, nc = img.shape
    out_mean = np.zeros(nc)
    out_vars = np.zeros(nc)
    # return out_mean, out_vars

    # Reset running statistics
    ring = {'N': 0, 'Vx': 0.0, 'Mx': 0.0}

    # Compute starting core index ranges
    core_rix1 = max(0, r - core_rad)
    core_rix2 = min(nr - 1, r + core_rad)
    core_cix1 = 0
    core_cix2 = min(nc - 1, core_rad)

    # Compute starting ring index ranges and statistics
    ring_rix1 = max(0, r - ring_rad)
    ring_rix2 = min(nr - 1, r + ring_rad)
    ro_cix1 = 0
    ro_cix2 = min(nc - 1, ring_rad)
    ri_cix1 = -core_rad - 1
    ri_cix2 = +core_rad + 1

    # Note: R1 never exists for first column
    if ring_rix1 <= core_rix1 - 1:  # R2
        __ol_var_add(ring, img[ring_rix1:core_rix1, core_cix1:core_cix2 + 1])

    if ring_rix2 >= core_rix2 + 1:  # R3
        __ol_var_add(ring,
                     img[core_rix2 + 1:ring_rix2 + 1, core_cix1:core_cix2 + 1])

    if ro_cix2 >= core_cix2 + 1:  # R4
        __ol_var_add(ring,
                     img[ring_rix1:ring_rix2 + 1, core_cix2 + 1:ro_cix2 + 1])

    out_mean[0] = ring['Mx']
    out_vars[0] = __ol_var(ring)

    # Start sliding right and updating statistics
    for c in range(1, nc):
        # Now we need to slide our core mean right
        if core_cix1 < c - core_rad:
            # remove left column of core
            core_cix1 += 1

        if core_cix2 + 1 < nc:
            core_cix2 += 1

        # Going to start with the long edges
        if ro_cix1 < c - ring_rad:
            # remove far left column of ring
            __ol_var_remove(ring, img[ring_rix1:ring_rix2 + 1, ro_cix1])
            ro_cix1 += 1

        ro_cix2 += 1
        if ro_cix2 + 1 < nc:
            # add outer right column
            __ol_var_add(ring, img[ring_rix1:ring_rix2 + 1, ro_cix2])

        # Now for the short edges
        if ri_cix2 < nc:
            # remove inner right column
            __ol_var_remove(ring, img[core_rix1:core_rix2 + 1, ri_cix2])
            ri_cix2 += 1

        ri_cix1 += 1
        if 0 <= ri_cix1 < nc:
            # add inner left column
            __ol_var_add(ring, img[core_rix1:core_rix2 + 1, ri_cix1])

        # Save mean and variance calculations for ring
        out_mean[c] = ring['Mx']
        out_vars[c] = __ol_var(ring)
    print('END RING {}'.format(r))
    return out_mean, out_vars


def img_ring_stats(img, csz, rsz):
    """
    Compute a ring windows mean and variance for every pixel of an image using
    a sliding window.

    :param img: The image to process.
    :type img: numpy.array
    :param csz: Diameter of missing center of ring.
    :type csz: int
    :param rsz: Diameter of ring.
    :type rsz: int
    :return: Computed mean and variance matrices (same size as `img`).
    :rtype: (numpy.array, numpy.array)
    """
    if mats.cpp_backend:
        return mats.mc.img_ring_stats(img, csz, rsz)
    nr, nc = img.shape
    #          core_cix1
    #          |     core_cix2
    #          v     v
    # R1 R1 R1 R2 R2 R2 R4 R4 R4 <- ring_rix1
    # R1 R1 R1 R2 R2 R2 R4 R4 R4
    # R1 R1 R1 R2 R2 R2 R4 R4 R4
    # R1 R1 R1 CC CC CC R4 R4 R4 <- core_rix1
    # R1 R1 R1 CC CC CC R4 R4 R4
    # R1 R1 R1 CC CC CC R4 R4 R4 <- core_rix2
    # R1 R1 R1 R3 R3 R3 R4 R4 R4
    # R1 R1 R1 R3 R3 R3 R4 R4 R4
    # R1 R1 R1 R3 R3 R3 R4 R4 R4 <- ring_rix2
    # ^     ^           ^     ^
    # |     ri_cix1     |     ro_cix2
    # ro_cix1           ri_cix2
    core_rad = int(csz / 2)
    ring_rad = int(rsz / 2)

    # We are going to compute the statistics for the first column of every row
    # then we will just update for remaining columns.
    out_mean = np.zeros((nr, nc))
    out_vars = np.zeros((nr, nc))
    for r in range(0, nr):
        out_mean[r, :], out_vars[r, :] = __ring_window_slide(core_rad, ring_rad,
                                                             r, img)
    # work = tuple([core_rad, ring_rad, r, img] for r in range(0, nr))
    # print('STARTING POOL')
    # results = []
    # with Pool(processes=4) as p:
    #     result = p.imap(__ring_window_slide, work)
    return out_mean, out_vars


# Find connected regions of an image stored in numpy.ndarray
# NOTE: The input image does not technically have to be a boolean array as in
#   the C equivalent, but all non-zero values in arr are treated as the same,
#   i.e., label(arr) == label(arr > 0).
def bwlabel(arr):
    # Specify connectivity to include diagonal directions
    connections = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
    labels, _ = scipy.ndimage.label(arr, connections)
    return labels


if __SKIMAGE:
    def regionprops(bw):
        """
        Measures properties of binary image regions (column-major).

        .. note::
           PixelIdxList may be different form C due to memory ordering on numpy
           array.

        :param bw: Binary image.
        :param bw: array-like
        :return: Structs containing properties for each binary image region.
                 Current properties include:

                 **Area** [int]:
                   Scalar that specifies the number of pixels in the region.

                 **BoundingBox** [array-like]:
                   Smallest rectangle containing region
                   [upperLeftRowIndex, upperLeftColIndex, rowWidth, colWidth].

                 **Centroid** [array-like]:
                   Center of mass for region [row, col].

                 **PixelIdxList** [array-like]:
                   Array of linear indices of the pixels in the region.

                 **MajorAxisLength** [double]:
                   Length (in pixels) of the major axis of the ellipse that has
                   the same normalized second central moments as the region.
                 **MinorAxisLength** [double]:
                   Length (in pixels) of the minor axis of the ellipse that has
                   the same normalized second central moments as the region.
                 **Orientation** [double]:
                   Angle between the x-axis and the major axis of the ellipse
                   that has the same second-moments as the region. The value is
                   in degrees, between -90 and 90.
        :rtype: list of mats.Struct
        """
        if mats.cpp_backend:
            return mats.mc.regionprops(bw)
        # TODO(Bradley): Orientation is not implemented.
        lbls = skimage.measure.label(bw)
        regs = skimage.measure.regionprops(lbls)

        # Area, BoundingBox, and Centroid look the same, but the rest are
        # different
        new_regs = []
        for reg in regs:
            rix, cix = np.where(lbls == reg.label)

            # Finish major/minor axis length calculation
            if reg.area >= 1:
                major_length, minor_length = axis_lengths(rix, cix)
            else:
                major_length, minor_length = (0, 0)

            # skimage returns (min_row, min_col, max_row, max_col) and we want
            # [upperLeftRowIndex upperLeftColIndex rowWidth colWidth]
            bbox = (reg.bbox[0], reg.bbox[1],
                    reg.bbox[2]-reg.bbox[0], reg.bbox[3]-reg.bbox[1])

            new_reg = {
                'Area': reg.area,
                'BoundingBox': bbox,
                'Centroid': reg.centroid,
                'MajorAxisLength': major_length,
                'MinorAxisLength': minor_length,
                'Orientation': None,
                'PixelIdxList': np.where(lbls.ravel() == reg.label)[0]
            }
            new_regs.append(new_reg)
        return new_regs
else:
    def regionprops(bw):
        raise NotImplemented('Implmentation requires "skimage" module.')


def region_axis_lens(reg):
    coords = reg['coords']
    major, minor = axis_lengths(coords[:, 0], coords[:, 1])
    return major, minor


# A,B are coordinate vectors
def axis_lengths(a, b):
    assert(len(a) == len(b))
    n = len(a)

    # Calculate covariances.
    aval = a - np.mean(a)
    bval = b - np.mean(b)
    cov_aa = np.sum(aval * aval)
    cov_ab = np.sum(aval * bval)
    cov_bb = np.sum(bval * bval)

    # 1/12 is the normalized second central moment of a pixel with unit length.
    cov_aa = cov_aa / n + (1.0/12.0)
    cov_bb = cov_bb / n + (1.0/12.0)
    cov_ab /= n

    # Final calculation
    common = np.sqrt((cov_aa - cov_bb)*(cov_aa - cov_bb) + 4*cov_ab*cov_ab)
    major_len = 2.0 * np.sqrt(2.0) * np.sqrt(cov_aa + cov_bb + common)
    minor_len = 2.0 * np.sqrt(2.0) * np.sqrt(cov_aa + cov_bb - common)
    return major_len, minor_len


def decimate(indata, dim, rate, mode):
    """
    Perform decimation on 2-D data.

    :param indata: The data to be decimated.
    :type indata: array-like
    :param dim: Dimension to decimate (0 = along-track | 1 = cross-track).
    :type dim: int
    :param rate: The decimation rate.  Must be positive.
    :type rate: int
    :param mode: Decimate method to use (0 = average method | 1 = peak-pick).
    :type mode: int
    :return: Decimated data.
    :rtype: array-like
    """
    if rate == 1:
        # No decimation necessary
        return indata.copy()
    if rate == 0:
        raise ValueError("Decimation rate must be positive.")
    if dim not in [0, 1]:
        raise ValueError("Invalid dimension given.")
    if mode not in [0, 1]:
        raise ValueError("Invalid mode given.")

    # Get initial array size and storage type.
    anum, cnum = indata.shape
    if anum == 0 or cnum == 0:
        raise ValueError("Cannot decimate empty dataset.")
    anum2 = math.ceil(anum/rate)

    # Prepare to decimate along major dimension.
    if dim == 1:  # decimate cross-track
        indata = np.tranpose(indata)

    # Perform decimation.
    if mode == 0:
        outdata = np.mean(indata.reshape(rate, anum2, cnum), axis=1)
    else:
        outdata = np.max(indata.reshape(rate, anum2, cnum), axis=1)

    if dim == 1:
        outdata = np.transpose(outdata)
    return outdata
