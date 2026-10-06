# DISTRIBUTION STATEMENT D. Distribution authorized to the Department of
# Defense and U.S. DoD contractors only; Administrative or Operational Use; 1
# Jan 2017. Other U.S. requests shall be referred to Naval Surface Warfare
# Center Panama City Division, ATTN: Technical Director NSWC PCD, 110 Vernon
# Ave, Panama City, FL 32407.
"""
mats.interp
-----------
Contains functions for interpolation.
"""
import numpy
import mats
import mats.log

if not mats.cpp_backend:
    import scipy.interpolate


def linear(x, yr, yi, xx, yyr=None, yyi=None):
    """
    1D linear interpolation.

    :param x: Array of x values for source. (length n; monotonically increasing)
    :type x: numpy.ndarray
    :param yr: Array of real component values for source. (length n)
    :type yr: numpy.ndarray
    :param yi: Array of imaginary component values for source. (length n)
    :type yi: numpy.ndarray
    :param xx: Array of desired x values for return arrays. (length nn;
               monotonically increasing)
    :type xx: numpy.ndarray
    :param yyr: Return array for real component values. (length nn; optional)
    :type yyr: numpy.ndarray
    :param yyi: Return array for imaginary component values.
                (length nn; optional)
    :type yyi: numpy.ndarray
    """
    is_complex = yi is not None
    return_outs = yyr is None
    # Assume all inputs are 1D numpy arrays!
    assert (type(x) is numpy.ndarray and len(x.shape) == 1)
    n = x.size
    assert (type(yr) is numpy.ndarray and len(yr.shape) == 1)
    assert (yr.size == n)
    if is_complex:
        assert (type(yi) is numpy.ndarray and len(yi.shape) == 1)
        assert (yi.size == n)
    assert (type(xx) is numpy.ndarray and len(xx.shape) == 1)
    nn = xx.size
    if return_outs:
        # Initialize output arrays
        yyr = numpy.zeros((nn,))
        if is_complex:
            yyi = numpy.zeros((nn,))
        else:
            yyi = None
    else:
        # Ensure that the specified output arrays are the correct size/type
        assert (type(yyr) is numpy.ndarray and len(yyr.shape) == 1)
        assert (yyr.size == nn)
        if is_complex:
            assert (type(yyi) is numpy.ndarray and len(yyi.shape) == 1)
            assert (yyi.size == nn)

    j = 0
    for i in range(nn):
        # Find first x >= current xx to calculate
        while x[j] < xx[i] and j < n - 1:
            j += 1

        if x[j] == xx[i]:
            yyr[i] = yr[j]
            if is_complex:
                yyi[i] = yi[j]
        elif j == 0:
            yyr[i] = (xx[i] - x[j]) * (yr[j + 1] - yr[j]) / \
                     (x[j + 1] - x[j]) + yr[j]
            if is_complex:
                yyi[i] = (xx[i] - x[j]) * (yi[j + 1] - yi[j]) / (
                            x[j + 1] - x[j]) + yi[j]
        else:
            yyr[i] = (xx[i] - x[j]) * (yr[j] - yr[j - 1]) / \
                     (x[j] - x[j - 1]) + yr[j]
            if is_complex:
                yyi[i] = (xx[i] - x[j]) * (yi[j] - yi[j - 1]) / (
                            x[j] - x[j - 1]) + yi[j]

    if return_outs:
        if is_complex:
            return yyr, yyi
        else:
            return yyr
    return


def interp1(x, yr, yi, xx, yyr, yyi, mode):
    """
    1D interpolation.

    :param x: Array of x values for source. (length n; monotonically increasing)
    :type x: numpy.ndarray
    :param yr: Array of real component values for source. (length n)
    :type yr: numpy.ndarray
    :param yi: Array of imaginary component values for source. (length n)
    :type yi: numpy.ndarray
    :param xx: Array of desired x values for return arrays. (length nn;
               monotonically increasing)
    :type xx: numpy.ndarray
    :param yyr: Return array for real component values. (length nn; optional)
    :type yyr: numpy.ndarray
    :param yyi: Return array for imaginary component values.
                (length nn; optional)
    :type yyi: numpy.ndarray
    :param mode: Type of interpolation to use [linear].
    :type mode: str
    :return: Returns 0 on success.
    :rtype: int
    """
    if x.size < 1:
        mats.log.error("n must be at least 1.")
        return 1

    if mode == 'linear':
        linear(x, yr, yi, xx, yyr, yyi)
        return 0
    mats.log.error("Unknown interp1 mode specified.")
    return 1


def grid_interp2(rv, cv, img, rv_new, cv_new):
    """
    Linear interpolation for 2D gridded data. Extrapolation values are set to
    zero. Row and column sample point vectors are used to form sample point grid
    for sample matrix. Row and column query point vectors are used to form query
    point grid.

    :param rv: Row sample array.
    :type rv: numpy.array
    :param cv: Column sample array.
    :type cv: numpy.array
    :param img: 2D sample matrix to be interpolated.
    :type img: numpy.array
    :param rv_new: Array of row query points.
    :type rv_new: numpy.array
    :param cv_new: Array of column query points.
    :type cv_new: numpy.array

    :return: 2D matrix of interpolated values.
    :rtype: np.array

    .. note:: Sample and query point vectors are assumed to be monotonically
               increasing.
    """
    if mats.cpp_backend:
        return mats.mc.grid_interp2(rv, cv, img, rv_new, cv_new)
    f = scipy.interpolate.RegularGridInterpolator((rv, cv), img, bounds_error=False, fill_value=0)
    cv_new, rv_new = numpy.meshgrid(cv_new, rv_new)
    points = numpy.array([rv_new.ravel(), cv_new.ravel()]).T
    return f(points).reshape(cv_new.shape)


def img_resize(img, nnr, nnc):
    """
    Resize an image using bilinear interpolation.

    :param img: Original image to be resized.
    :type img: numpy.array
    :param nnr: Number of rows in resized image.
    :type nnr: numpy.array
    :param nnc: Number of columns in resized image.
    :type nnc: numpy.array

    :return: Resized image.
    :rtype: numpy.array
    """
    if mats.cpp_backend:
        return mats.mc.img_resize(img, nnr, nnc)
    raise NotImplementedError('No python implementation.')
