import warnings
import math
import numpy as np


def clip_image(M, **kwargs):
    """
    Dynamic range compression for sas imagery. Specificialy for cases where
    gammaclip is not providing acceptable results.

    This algorithm stretches the dynamic range of typical bottom returns to
    range between 0 and lowRangeMax. The highlight dynamic range is also
    stretched to range between upperRangeMin and 1.  The mid-intensity points
    (clipBot to clipTop) dynamic range is compressed.

    :param M: Data array
    """
    # lowRangeMax - Upper limit of lower range return after adjustment
    # lowerPercent - Percent of values to be placed in the lower range
    # midRangeMax - Upper limit of mid range after adjustment
    # midRangePercent - Percent of values to be placed in the mid and lower
    #                   range (cumulative)
    # lowEndClip - Clipped minimum for intensity
    # highEndClip - Clipped maximum intensity
    opt = {
        'lowRangeMax': 0.40,
        'lowerPercent': 0.99, # 99% of values will be in the lower range
                              # (i.e. 99% of return is from the bottom, 1% from
                              # target)
        'midRangeMax': 1,     # Default settings use only one partition
        'midRangePercent': 1, # Default settings use only one partition
        'lowEndClip': 0.001,  # Default setting does not clip the shadow
        'highEndClip': 0.70   # Default setting does not clip the highlight
    }
    for param in kwargs:
        if param in opt:
            opt[param] = kwargs[param]
        else:
            warnings.warn('Unknown arg "{}".'.format(param))

    M = np.abs(M)  # Convert from imaginary to intensity only values
    M = M - M.min()  # Scale values to range between 0  and 1
    M = M / M.max()

    # Create a histogram of the image intensities.  Rescale later based on
    # values corresponding to a particular percent of image pixels being below
    # a specified value.
    # [counts,x] = imhist(M);
    # sumCounts = cumsum(counts)/sum(counts);

    # Max low-range intensity before rescale
    # clipBot = x(find(sumCounts>lowerPercent,1,'first'));

    # Max mid-range intensity before rescale
    # clipMid = x(find(sumCounts>=midRangePercent,1,'first'));

    # ==========================================================================
    # 3-Part rescaling scheme:
    # ==========================================================================
    # First determine if the mid-range is getting larger or smaller.  This will
    # determine the order in which the sections are rescaled.

    # change in size = width of range (initial) - width of range (final)
    # midRangeDifference = (clipMid-clipBot) - (midRangeMax - lowRangeMax);

    # % If the mid-range is being compressed, then compress the mid-range and
    # % expand the high-range data.
    # if midRangeDifference > 0
    #     % Expanding the mid-range and compressing the high range
    #     % First expand the mid range intensities:
    #     % Isolate the subset to be compressed:
    #     %      subset = M(M >= clipBot & M <= clipTop)
    #     % Scale subset to be between 0 and 1:  subset/subsetWidth
    #     % Rescale subset to be between 0 and new subset max
    #     %      subset = newMax*subset/subsetWidth
    #     % Add max value of lower group (background) to make results continuous:
    #     %      scaledSubset = scaledSubset + lowRangeMax
    #     M(M >= clipBot & M <= clipMid) = lowRangeMax + ...
    #         (midRangeMax - lowRangeMax) * (M(M >= clipBot & M <= clipMid) - clipBot) ...
    #         /(clipMid - clipBot);

    #     % Now rescale upper-range with a similar equation:
    #     M(M > clipMid) = midRangeMax + (1 - midRangeMax) * (M(M > clipMid) ...
    #         - clipMid) / (1 - clipMid);
    # elseif midRangeDifference <= 0
    #     %Scale the upper-range first, then the mid-range.
    #     M(M > clipMid) = midRangeMax + (1 - midRangeMax) * (M(M > clipMid) ...
    #         - clipMid) / (1 - clipMid);
    #     % Scaling mid-range data
    #     M(M >= clipBot & M <= clipMid) = lowRangeMax + ...
    #         (midRangeMax - lowRangeMax) * (M(M >= clipBot & M <= clipMid) - clipBot) ...
    #         /(clipMid - clipBot);
    # end


    # Now expand intensities for the average bottom return to show bottom
    # detail. Same procedure as above example.
    # M(M < clipBot) = lowRangeMax * M(M < clipBot) / clipBot;

    # Now perform the final clip
    # M(M<lowEndClip) = lowEndClip;
    # M(M>highEndClip) = highEndClip;
    # M = (M - lowEndClip)/(highEndClip - lowEndClip);

    return M


def imadjust(img, inRng, outRng, gamma):
    """
    IMADJUST Adjust image intensity values or colormap.

    J = IMADJUST(I,[LOW_IN; HIGH_IN],[LOW_OUT; HIGH_OUT],GAMMA) maps the
    values of I to new values in J as described in the previous syntax.
    GAMMA specifies the shape of the curve describing the relationship
    between the values in I and J. If GAMMA is less than 1, the mapping is
    weighted toward higher (brighter) output values. If GAMMA is greater
    than 1, the mapping is weighted toward lower (darker) output values. If
    you omit the argument, GAMMA defaults to 1 (linear mapping).

    Note that if HIGH_OUT < LOW_OUT, the output image is reversed, as in a
    photographic negative.

    Input-output specs
    ------------------
    I,J          real, full matrix, 2-D
                 uint8, uint16, double, single, int16

    [LOW_IN; HIGH_IN]    double, real, full matrix
                         For I, size can only be 2 elements.
                         For RGB or MAP, size can be 2 elements OR
                         2-by-3 matrix.
                         LOW_IN < HIGH_IN

    [LOW_OUT; HIGH_OUT]  Same size restrictions as [LOW_IN; HIGH_IN]
                         LOW_OUT can be less than HIGH_OUT

    LOW_IN, HIGH_IN, LOW_OUT, HIGH_OUT all must be in the range [0,1];

    GAMMA         real, double, nonnegative
                  scalar for I
                  scalar or 1-by-3 vector for RGB and MAP
    """
    # Parse inputs and initialize variables
    if not isinstance(img, np.ndarray):
        raise ValueError('img must be an numpy.ndarray.')
    if not (isinstance(inRng, list) and len(inRng) == 2):
        raise ValueError('inRng must be list of length 2.')
    if outRng:
        if not (isinstance(outRng, list) and len(outRng) == 2):
            raise ValueError('inRng must be list of length 2.')
        if outRng[0] > outRng[1]:
            raise ValueError('outRng[0] > outRng[1]')
    if not (isinstance(gamma, float) and gamma >= 0):
        raise ValueError('gamma, must be nonnegative float.')
    if inRng[0] > inRng[1]:
        raise ValueError('inRng[0] > inRng[1]')

    # make sure img is in the range [lIn;hIn]
    out = np.clip(img, inRng[0], inRng[1])
    out = ( (out - inRng[0]) / (inRng[1] - inRng[0]) ) ** gamma
    if outRng:
        out = out * (outRng[1] - outRng[0]) + outRng[0]

    return out
