/**
 * @file
 * @brief File contains MATS implementations of interpolation routines.
 */

/**************************************************************************
 *
 * DISTRIBUTION STATEMENT D. Distribution authorized to the Department of
 * Defense and U.S. DoD contractors only; Administrative or Operational Use; 1
 * Jan 2017. Other U.S. requests shall be referred to Naval Surface Warfare
 * Center Panama City Division, ATTN: Technical Director NSWC PCD, 110 Vernon
 * Ave, Panama City, FL 32407.
 *
 * POC:
 *
 * Bradley Marchand
 * NSWC Panama City Division, Code X24 (850)-230-7385
 * bradley.marchand@navy.mil
 *
 * Derek Kolacinski
 * NSWC Panama City Division, Code X23 (850)-230-7218
 * derek.kolacinski@navy.mil
 *
 *************************************************************************/
#ifndef SRC_MATS_INTERP_H_
#define SRC_MATS_INTERP_H_

#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <assert.h>
#include <string.h>

#include <vector>

#include "MATS_platform.h"


namespace mats {


/**
 * 1D Linear interpolation. Allows for extrapolation to be enabled/disabled.
 * When not extrapolating, values are set to zero.
 *
 * @param[in] n Number of source points in source arrays.
 * @param[in] x Array of x values for source. Assumed to be monotone increasing.
 * @param[in] Yr Array of real component values for source.
 * @param[in] Yi Array of imaginary component values for source.
 * @param[in] nn Number of values in return arrays.
 * @param[in] xx Array of desired x values for return arrays. Assumed to be
 * monotone increasing.
 * @param[out] YYr Return array for real component values.
 * @param[out] YYi Return array for imaginary component values.
 * @param[in] extrapolate Flag to enable/disable extrapolation.
 */
template<class DT1, class DT2> MATS_LIB void
linear_interp1(size_t n, const DT1* x, const DT2* Yr, const DT2* Yi,
    size_t nn, const DT1* xx, DT2* YYr, DT2* YYi, bool extrapolate);


/**
 * 1D interpolation.
 *
 * @param[in] n Number of source points in source arrays.
 * @param[in] x Array of x values for source. Assumed to be monotone increasing.
 * @param[in] Yr Array of real component values for source.
 * @param[in] Yi Array of imaginary component values for source.
 * @param[in] nn Number of values in return arrays.
 * @param[in] xx Array of desired x values for return arrays. Assumed to be
 * monotone increasing.
 * @param[out] YYr Return array for real component values.
 * @param[out] YYi Return array for imaginary component values.
 * @param[in] mode Interpolation method. Options include:
 *     - "linear"
 *
 * @return Returns 0 on success.
 */
template<class DT> MATS_LIB int
interp1(size_t n, const DT* x, const DT* Yr, const DT* Yi,
    size_t nn, const DT* xx, DT* YYr, DT* YYi, const char* mode);


/**
 * Linear interpolation for 2D gridded data. Extrapolation values are set to
 * zero. Row and column sample point vectors are used to form sample point grid
 * for sample matrix. Row and column query point vectors are used to form query
 * point grid.
 *
 * @param[in] Rv Row sample points.
 * @param[in] Cv Column sample points.
 * @param[in] X Sample values.
 * @param[in] RRv Row query points.
 * @param[in] CCv Column query points.
 * @param[out] XX Computed query values.
 *
 * @warning Sample and query point vectors are assumed to be monotonically
 * increasing.
 */
template<class DT> MATS_LIB void
grid_interp2(const std::vector<DT>& Rv, const std::vector<DT>& Cv,
    const std::vector<DT>& X, const std::vector<DT>& RRv,
    const std::vector<DT>& CCv, std::vector<DT>& XX);


template<class DT> MATS_LIB void
grid_interp2(
    size_t nr, size_t nc, const DT *Rv, const DT *Cv, const DT *X,
    size_t nnr, size_t nnc, const DT *RRv, const DT *CCv, DT *XX);


/**
 * Resize an image using bilinear interpolation.
 *
 * @param[in] nr Number of rows in original image.
 * @param[in] nc Number of columns in original image.
 * @param[in] X Original image (nr x nc).
 * @param[in] nnr Number of rows in resized image.
 * @param[in] nnc Number of columns in resized image.
 * @param[out] XX Resized image.
 */
template<class DT> MATS_LIB void
img_resize(size_t nr, size_t nc, const DT *X, size_t nnr,
    size_t nnc, DT *XX);


/**
 * Rotates image by the given number of degrees counter clockwise around its
 * center.
 *
 * @param[in] nr Number of rows in image.
 * @param[in] nc Number of columns in image.
 * @param[in] img Image to be rotated.
 * @param[in] angle Angle in degrees counter clockwise.
 * @param[in] method Resampling filter method.
 * @param[out] out Rotated image.
 */
template<class DT> MATS_LIB void
img_rotate(size_t nr, size_t nc, const DT *img, DT angle, DT *out);

}  // namespace mats

#endif  // SRC_MATS_INTERP_H_
