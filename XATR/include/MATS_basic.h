/**
 * @file
 * @brief File contains MATS implementations of basic subroutines. Subroutines
 * are not specific to ATR or MATS.
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
#ifndef SRC_MATS_BASIC_H_
#define SRC_MATS_BASIC_H_

#include <math.h>
#include <string>

#include "MATS_platform.h"
#include "MATS_struct.h"

#ifdef MATS_WINDOWS
#define NOMINMAX
#endif

#include <complex>

namespace mats {


/**
 * Value of pi
 */
#define MATS_PI 3.1415926535897932384626433832795
#define MATS_2PI 2.0*MATS_PI

/**
 * Obtain the lock for the FFTW planner.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int mats_lock_fftw();


/**
 * Release the lock for the FFTW planner.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int mats_unlock_fftw();


/**
 * Tests if number is "Not A Number" (NaN). Templates are only define for
 * double and float (unsigned int and int do not have a NaN capability).
 *
 * @param[in] x Number to test for NaN.
 *
 * @return Returns 1 if it is a NaN, otherwise returns 0.
 *
 * @warning Test depends on IEEE-754 standard and may or may not work on every
 * compiler.
 */
template<class DT> MATS_LIB inline int isnan(DT x) {
  volatile DT tmp = x;  // To help with compiler optimization issues
  return tmp != x;
}


/**
 * Tests if number is infinity (Inf). Templates are only define for
 * double and float (unsigned int and int do not have a Inf capability).
 *
 * @param[in] x Number to test for Inf.
 *
 * @return Returns -1 if it is -Inf, 1 if it is Inf, otherwise returns 0.
 */
template<class DT> MATS_LIB inline int isinf(DT x) {
  volatile DT tmp = x;
  if ((tmp == x) && ((tmp - x) != 0.0))
    return (x < 0.0 ? -1 : 1);
  else
    return 0;
}


#ifdef MATS_WINDOWS
#undef max
#endif


/**
 * Returns maximum of two quantities.
 */
template<class DT> MATS_LIB inline DT max(DT x, DT y) {
  return ((x) > (y)?(x):(y));
}


/**
 * Returns maximum value in an array.
 *
 * @param[in] N Size of array.
 * @param[in] X Pointer to array.
 *
 * @return Maximum value in array (returns 0 if array is size 0).
 */
template<class DT> MATS_LIB DT max(size_t N, const DT* X);


#ifdef MATS_WINDOWS
#undef min
#endif


/**
 * Returns minimum of two quantities.
 */
template<class DT> MATS_LIB inline DT min(DT x, DT y) {
  return ((x) < (y)?(x):(y));
}


/**
 * Returns minimum value in an array.
 *
 * @param[in] N Size of array.
 * @param[in] X Pointer to array.
 *
 * @return Minimum value in array (returns 0 if array is size 0).
 */
template<class DT> MATS_LIB DT min(size_t N, const DT* X);


/**
 * Returns @p x modulo @p y.
 */
template<class DT> MATS_LIB DT modulo(DT x, DT y);


/**
 * Flips a vector.
 *
 * @param[in] N Size of vector.
 * @param[in,out] X Vector to flip.
 */
template<class DT> MATS_LIB inline void vector_flip(size_t N, DT* X) {
  size_t k;
  DT tmp;

  for (k = 0; k < N/2; ++k) {
    tmp = X[k];
    X[k] = X[N-1-k];
    X[N-1-k] = tmp;
  }

  return;
}


/**
 * Perform in-place flip of matrix left to right (column reflection).
 *
 * @param[in] nr Number of rows in matrix.
 * @param[in] nc Number of columns in matrix.
 * @param[in,out] X C array matrix in column major format.
 *
 * @return Returns 0 on success.
 */
template<class DT> MATS_LIB int fliplr(size_t nr, size_t nc, DT* X);


/**
 * Perform in-place flip of matrix top to bottom (row reflection).
 *
 * @param[in] nr Number of rows in matrix.
 * @param[in] nc Number of columns in matrix.
 * @param[in,out] X C array matrix in column major format.
 *
 * @return Returns 0 on success.
 */
template<class DT> MATS_LIB int flipud(size_t nr, size_t nc, DT* X);


/**
 * Returns a pseudo-random integer in the range [imin,imax).
 *
 * @param[in] imin Minimum random integer value.
 * @param[in] imax Maximum random integer value.
 *
 * @return Random integer between imin and imax-1.
 */
MATS_LIB int randi(int imin, int imax);


/**
 * Returns an array of pseudo-random integral numbers between imin and
 * imax-1. Optionally, provide a MATS_RNG object that has been seeded to the
 * desired value for predictable output.
 *
 * @param[in] imin Minimum random integer value.
 * @param[in] imax Maximum random integer value.
 * @param[in] N Number of random integers to generate.
 * @param[out] array Array to store generated random integers.
 * @param[in] rng (Optional) Pointer to a MATS_RNG object.
 *
 * @return Returns 0 on success.
 *
 * @warning Output @p array is assumed to be already allocated to length @p N.
 */
MATS_LIB int randi(int imin, int imax, size_t N, int* array, void* rng = NULL);


/**
 * Returns a pseudo-random value drawn from the uniform distribution on
 * [0, 1].
 */
MATS_LIB double randd();


/**
 * Returns a vector containing @p k unique integers selected randomly
 * from 1 to @p n.
 *
 * @param[in] n Number of integers in sample interval.
 * @param[in] k Number of selected integers.
 * @param[out] p Array for permutation.
 *
 * @return Returns 0 on success.
 *
 * @warning Output @p p is assumed to be already allocated to length @p k.
 */
MATS_LIB int randperm(size_t n, size_t k, size_t *p);


/**
 * Perform conversion from real/imaginary to amplitude/phase. The same pointers
 * may be used for input and output arrays for in-place conversion. If no phase
 * output array is supplied, only the amplitude is calculated.
 *
 * @param[in] N The size of each array.
 * @param[in] Xr Input the real array.
 * @param[in] Xi Input the imaginary array.
 * @param[out] Xa Output the amplitude array.
 * @param[out] Xp (Optional) Output the phase array.
 *
 * @return Returns 0 on success.
 *
 * @warning @p Xr, @p Xi, and @p Xa must be non-zero pointers to existing
 * arrays. If @p Xp is supplied, it must point to an existing array.
 */
template<class DT, class DT2> MATS_LIB int
ri2ap(size_t N, const DT* Xr, const DT* Xi, DT2* Xa, DT2* Xp = NULL);


/**
 * Perform in-place conversion from amplitude/phase to real/imaginary.
 *
 * @param[in] N The size of each array.
 * @param[in, out] Xa Input the amplitude array; output the real array.
 * @param[in, out] Xp Input the phase array; output the imaginary array.
 *
 * @return Returns 0 on success.
 *
 * @warning Both @p Xa and @p Xp must be non-zero pointers to existing arrays.
 */
template<class DT> MATS_LIB int ap2ri(size_t N, DT* Xa, DT* Xp);


/**
 * Sums c array matrix in desired direction. Assumes column-major storage.
 *
 * For option 0 (entire matrix summation), threading (or simulated threading)
 * is used for large matrices.  Threading is not used for options 1 or 2.
 *
 * @param[in] nr Number of rows in matrix.
 * @param[in] nc Number of columns in matrix.
 * @param[in] data Pointer to data matrix.
 * @param[in] dim Direction of summation (0 - sums entire matrix, 1 - column
 * sums, 2 - row sums).
 * @param[out] sum_vec Vector for computed sums.
 *
 * @return Returns 0 on success.
 *
 * @warning @p sum_vec is assumed to be allocated (i.e., for @p dim = 0,
 * @p sum_vec should be a pointer to a single number. For @p dim = 1,
 * @p sum_vec is assumed length @p nc. For @p dim = 2, @p sum_vec is assumed
 * length @p nr).
 */
template<class DT> MATS_LIB int
sum(size_t nr, size_t nc, const DT* data, int dim, DT* sum_vec);


/**
 * Sums c array matrix in desired direction. Assumes column-major storage.
 * This version converts the data to double precision when summing.
 *
 * For option 0 (entire matrix summation), threading (or simulated threading)
 * is used for large matrices.  Threading is not used for options 1 or 2.
 *
 * @param[in] nr Number of rows in matrix.
 * @param[in] nc Number of columns in matrix.
 * @param[in] data Pointer to data matrix.
 * @param[in] dim Direction of summation (0 - sums entire matrix, 1 - column
 * sums, 2 - row sums).
 * @param[out] sum_vec Vector for computed sums.
 *
 * @return Returns 0 on success.
 *
 * @warning @p sum_vec is assumed to be allocated (i.e., for @p dim = 0,
 * @p sum_vec should be a pointer to a single number. For @p dim = 1,
 * @p sum_vec is assumed length @p nc. For @p dim = 2, @p sum_vec is assumed
 * length @p nr).
 */
template<class DT> MATS_LIB int
sum_double(size_t nr, size_t nc, const DT* data, int dim, double* sum_vec);


/**
 * Returns the cumulative sum of the elements along dimension dim. Matrix is
 * assumed to be column-major.
 *
 * @param[in] nr Number of rows in matrix.
 * @param[in] nc Number of columns in matrix.
 * @param[in] data Pointer to data matrix.
 * @param[in] dim Direction of cumulative sum (1 - rows, 2 - columns).
 * @param[out] B Cumulative sum matrix.
 *
 * @warning @p B is assumed to be allocated to the size of @p data.
 */
template<class DT> MATS_LIB int
cumsum(size_t nr, size_t nc, const DT *data, int dim, DT *B);


/**
 * Find the mean(s) of a [ @p nr x @p nc ] array @p data and store in
 * @p mean_vec. Assumes column-major storage.
 *
 * @param[in] nr Number of rows in matrix.
 * @param[in] nc Number of columns in matrix.
 * @param[in] data Pointer to data matrix.
 * @param[in] dim Direction of mean (0 - mean of entire matrix, 1 - column
 * means, 2 - row means).
 * @param[out] mean_vec Vector for computed means.
 *
 * @return Returns 0 on success.
 *
 * @warning @p mean_vec is assumed to be allocated (i.e., for @p dim = 0,
 * @p mean_vec should be a pointer to a single number. For @p dim = 1,
 * @p mean_vec is assumed length @p nc. For @p dim = 2, @p mean_vec is assumed
 * length @p nr).
 */
template<class DT> MATS_LIB int
mean(size_t nr, size_t nc, const DT* data, int dim, DT* mean_vec);


/**
 * Find the mean of all elements in array @p data and store in @p output.
 * This version mimics the MATLAB function %mean2() by converting elements to
 * double precision before summing.
 *
 * @param[in] N Number of elements in array.
 * @param[in] data Pointer to data matrix.
 * @param[out] output Pointer to mean of array elements.
 *
 * @return Returns 0 on success.
 */
template<class DT> MATS_LIB int mean2(size_t N, const DT* data, double* output);


/**
 * Find the standard deviation(s) of a [ @p nr x @p nc ] array @p data and
 * store in @p stdvec. Optionally, also store the mean(s) in @p meanvec.
 * Assumes column-major storage.
 *
 * @param[in] nr Number of rows in matrix.
 * @param[in] nc Number of columns in matrix.
 * @param[in] data Pointer to data matrix.
 * @param[in] dim Direction of calculation (0 - entire matrix, 1 - per column,
 * 2 - per row).
 * @param[out] stdvec Vector for computed standard deviations.
 * @param[out] meanvec (Optional) Vector for computed means.
 *
 * @return Returns 0 on success.
 *
 * @warning @p stdvec is assumed to be allocated (i.e., for @p dim = 0,
 * @p stdvec should be a pointer to a single number. For @p dim = 1,
 * @p stdvec is assumed length @p nc. For @p dim = 2, @p stdvec is assumed
 * length @p nr). If @p meanvec is not null, it is also assumed to be allocated
 * (same size as @p stdvec).
 */
template<class DT> MATS_LIB int stdDev(size_t nr, size_t nc, const DT* data,
    int dim, DT* stdvec, DT* meanvec = NULL);


/**
 * Find the moment(s) of a [ @p nr x @p nc ] array @p data and store in
 * @p mmt_vec. For central moment, use the mean as @p center.  Assumes
 * column-major storage.
 *
 * @param[in] nr Number of rows in matrix.
 * @param[in] nc Number of columns in matrix.
 * @param[in] data Pointer to data matrix.
 * @param[in] center Calculate moment(s) about this number.
 * @param[in] order Moment order to calculate.
 * @param[in] dim Direction of calculation (0 - entire matrix, 1 - per column,
 * 2 - per row).
 * @param[out] mmt_vec Vector for computed moments.
 *
 * @return Returns 0 on success.
 *
 * @warning @p mmt_vec is assumed to be allocated (i.e., for @p dim = 0,
 * @p mmt_vec should be a pointer to a single number. For @p dim = 1,
 * @p mmt_vec is assumed length @p nc. For @p dim = 2, @p mmt_vec is assumed
 * length @p nr).
 */
template<class DT> MATS_LIB int moment(size_t nr, size_t nc, const DT* data,
    DT center, int order, int dim, DT* mmt_vec);


/**
 * Find the median value of an array.
 *
 * @param[in] N Number of elements in array.
 * @param[in] data Pointer to data array.
 *
 * @return Returns median value.
 */
template<class DT> MATS_LIB DT median(size_t N, const DT* data);


/**
 * Round to the nearest integer.
 *
 * @param[in] val Value to round.
 *
 * @return Returns the nearest integer. Values ending in 0.5 are rounded away
 * from 0.
 */
template<class DT> MATS_LIB DT round(DT val);


/**
 * Returns the sign of a value.
 *
 * @param[in] val Input value.
 *
 * @return Returns 1 for a positive value, -1 for a negative value, or 0 for 0.
 */
template<class DT> MATS_LIB int sign(DT val);


/**
 * Unwrap the phase, where phase is in radians.
 *
 * @param[in] first The first phase value (radians).
 * @param[in] second The second phase value (radians).
 *
 * @return The unwrapped second phase value (radians).
 */
template<class DT> MATS_LIB DT unwrap(DT first, DT second);


/**
 * Calculate mean and standard deviation after removing outlying values.
 *
 * @param[in] N Number of elements in array.
 * @param[in] data Pointer to data array.
 * @param[out] mu Mean of array after removing outliers.
 * @param[out] sig Standard deviation of array after removing outliers.
 *
 * @return Returns 0 on success.
 */
template<class DT> MATS_LIB int
gau_fit(size_t N, const DT* data, DT* mu, DT* sig);


/**
 * Computes product of elements in a vector.
 *
 * @param[in] data Vector of numbers.
 *
 * @return Product of numbers in vector.
 */
template<class DT> MATS_LIB DT prod(const std::vector<DT>& data);


/**
 * Maximum likelihood estimate of the Rayleigh distribution parameter.
 *
 * @param[in] N Number of elements in array.
 * @param[in] data Pointer to data array.
 * @param[out] param Pointer to estimate of Rayleigh parameter.
 *
 * @return Returns 0 on success.
 */
template<class DT> MATS_LIB int raylfit(size_t N, const DT* data, DT* param);


/**
 * Fill array @p data with random numbers from the Rayleigh distribution.
 * Optionally, provide a MATS_RNG object that has been seeded to the
 * desired value for predictable output.
 *
 * @param[in] param Rayleigh distribution parameter.
 * @param[in] N Number of elements in array.
 * @param[out] data Output array of Rayleigh random numbers.
 * @param[in] rng (Optional) Pointer to a MATS_RNG object.
 *
 * @return Returns 0 on success.
 *
 * @warning @p data must be pre-allocated.
 */
template<class DT> MATS_LIB int
raylrnd(DT param, size_t N, DT* data, void* rng = NULL);


/**
 * Perform median filtering of a 1-D array.  Non-threaded.
 *
 * For @p output, the same pointer may be used as for the input @p data.
 *
 * @param[in] Ndata Number of points in the data array.
 * @param[in] data The data to be filtered.
 * @param[in] Nfilt Number of points in the median filter.
 * @param[out] output The filtered data (size @p Ndata).
 *
 * @return Returns 0 on success.
 *
 * @warning The @p output array is assumed to be already allocated.  This may
 * be the same pointer as for @p data, but if not, the array should not
 * overlap @p data.
 */
MATS_LIB int
medfilt1(size_t Ndata, const double* data, size_t Nfilt, double* output);


/**
 * Symmetric extention padding of a 2-D array with rpad on top/bottom and cpad
 * on left/right.  Data is assumed to be in column-major storage. The output
 * array, pPadded, must be pre-allocated and of size (nr + 2*rpad, nc + 2*cpad).
 *
 * @param[in] nr Number of rows in the image.
 * @param[in] nc Number of columns in the image.
 * @param[in] data The image to be padded.
 * @param[in] rpad Padding size for top and bottom.
 * @param[in] cpad Padding size for left and right.
 * @param[in] pPadded The padded image.
 *
 * @warning The @p pPadded array is assumed to be already allocated and
 * different from @p data.
 */
MATS_LIB int
symmetric_pad2(size_t nr, size_t nc, const double *data, size_t rpad,
    size_t cpad, double * const pPadded);


/**
 * Replicate extention padding of a 2-D array with rpad on top/bottom and cpad
 * on left/right.  Data is assumed to be in column-major storage. The output
 * array, pPadded, must be pre-allocated and of size (nr + 2*rpad, nc + 2*cpad).
 *
 * @param[in] nr Number of rows in the image.
 * @param[in] nc Number of columns in the image.
 * @param[in] data The image to be padded.
 * @param[in] rpad Padding size for top and bottom.
 * @param[in] cpad Padding size for left and right.
 * @param[in] pPadded The padded image.
 *
 * @warning The @p pPadded array is assumed to be already allocated and
 * different from @p data.
 */
MATS_LIB int
replicate_pad2(size_t nr, size_t nc, const double *data, size_t rpad,
    size_t cpad, double * const pPadded);


/**
 * Perform median filtering of a 2-D image (column-major).
 *
 * For @p output, the same pointer may be used as for the input @p data.
 *
 * @param[in] Mdata Number of rows in the image.
 * @param[in] Ndata Number of columns in the image.
 * @param[in] data The image to be filtered.
 * @param[in] Mfilt Number of rows in the median filter.
 * @param[in] Nfilt Number of columns in the median filter.
 * @param[out] output The filtered image ([ @p Mdata x @p Ndata ]).
 *
 * @return Returns 0 on success.
 *
 * @warning The @p output array is assumed to be already allocated.  This may
 * be the same pointer as for @p data, but if not, the array should not
 * overlap @p data.
 */
MATS_LIB int medfilt2(size_t Mdata, size_t Ndata, const double* data,
    size_t Mfilt, size_t Nfilt, double* output);


/**
 * Perform median filtering of a 2-D image (column-major) with symmetrically
 * extended boundaries.
 *
 * For @p output, the same pointer may be used as for the input @p data.
 *
 * @param[in] Mdata Number of rows in the image.
 * @param[in] Ndata Number of columns in the image.
 * @param[in] data The image to be filtered.
 * @param[in] Mfilt Number of rows in the median filter.
 * @param[in] Nfilt Number of columns in the median filter.
 * @param[out] output The filtered image ([ @p Mdata x @p Ndata ]).
 *
 * @return Returns 0 on success.
 *
 * @warning The @p output array is assumed to be already allocated.  This may
 * be the same pointer as for @p data, but if not, the array should not
 * overlap @p data.
 */
MATS_LIB int medfilt2_symmetric(size_t Mdata, size_t Ndata, const double* data,
    size_t Mfilt, size_t Nfilt, double* output);


// TODO(Carrie): conv2() and imfilter() are very similar.  They can probably be
// replaced by a single function using options.

/**
 * Perform 2-D convolution.  The output image is the same size as the input
 * image, taken from the central part of the convolution.
 *
 * This is comparable to calling MATLAB's conv2 with option 'same'.
 *
 * For @p output, the same pointer may be used as for the input @p data.
 *
 * @note NOT circular (input array not assumed periodic), and values outside
 * boundary are assumed to be 0. Arrays are assumed to be column-major.
 *
 * @param[in] Mdata Number of rows in the image.
 * @param[in] Ndata Number of columns in the image.
 * @param[in] data The image to be filtered.
 * @param[in] Mfilt Number of rows in the filter.
 * @param[in] Nfilt Number of columns in the filter.
 * @param[in] filter The filter to convolve with the image.
 * @param[out] output The filtered image ([ @p Mdata x @p Ndata ]).
 *
 * @return Returns 0 on success.
 *
 * @warning This function uses the FFTW planner.  If the library is compiled
 * with threading enabled, this function is thread-safe provided that any
 * other uses of the FFTW planner use the mats_lock_fftw() and
 * mats_unlock_fftw() functions.  If the library is compiled without threading
 * enabled, this function is not thread-safe and must not be run simultaneously
 * with other uses of the FFTW planner.
 *
 * @warning The @p output array is assumed to be already allocated.  This may
 * be the same pointer as for @p data, but if not, the array should not
 * overlap @p data.
 */
MATS_LIB int conv2(size_t Mdata, size_t Ndata, const double* data,
    size_t Mfilt, size_t Nfilt, const double* filter, double* output);


namespace future {

/**
 * Perform 2-D convolution.  The output image is the same size as the input
 * image, taken from the central part of the convolution.
 *
 * This is comparable to calling MATLAB's conv2 with option 'same'.
 *
 * For @p output, the same pointer may be used as for the input @p data.
 *
 * @note NOT circular (input array not assumed periodic), and values outside
 * boundary are assumed to be 0. Arrays are assumed to be column-major.
 *
 * @param[in] Mdata Number of rows in the image.
 * @param[in] Ndata Number of columns in the image.
 * @param[in] data The image to be filtered.
 * @param[in] Mfilt Number of rows in the filter.
 * @param[in] Nfilt Number of columns in the filter.
 * @param[in] filter The filter to convolve with the image.
 * @param[out] output The filtered image ([ @p Mdata x @p Ndata ]).
 *
 * @return Returns 0 on success.
 *
 * @warning This function uses the FFTW planner.  If the library is compiled
 * with threading enabled, this function is thread-safe provided that any
 * other uses of the FFTW planner use the mats_lock_fftw() and
 * mats_unlock_fftw() functions.  If the library is compiled without threading
 * enabled, this function is not thread-safe and must not be run simultaneously
 * with other uses of the FFTW planner.
 *
 * @warning The @p output array is assumed to be already allocated.  This may
 * be the same pointer as for @p data, but if not, the array should not
 * overlap @p data.
 */
MATS_LIB int conv2(size_t Mdata, size_t Ndata, const double* data,
    size_t Mfilt, size_t Nfilt, const double* filter, const char *shape,
    double* output);
}  // namespace future


/**
 * Perform 2-D correlation.  The output image is the same size as the input
 * image, taken from the central part of the correlation.
 *
 * This is comparable to calling MATLAB's imfilter with options 'same' and
 * 'circular'.
 *
 * For @p output, the same pointer may be used as for the input @p data.
 *
 * @note Circular (input array assumed periodic). Arrays are assumed to be
 * column-major.
 *
 * @param[in] Mdata Number of rows in the image.
 * @param[in] Ndata Number of columns in the image.
 * @param[in] data The image to be filtered.
 * @param[in] Mfilt Number of rows in the filter.
 * @param[in] Nfilt Number of columns in the filter.
 * @param[in] filter The filter to convolve with the image.
 * @param[out] output The filtered image ([ @p Mdata x @p Ndata ]).
 *
 * @return Returns 0 on success.
 *
 * @warning This function uses the FFTW planner.  If the library is compiled
 * with threading enabled, this function is thread-safe provided that any
 * other uses of the FFTW planner use the mats_lock_fftw() and
 * mats_unlock_fftw() functions.  If the library is compiled without threading
 * enabled, this function is not thread-safe and must not be run simultaneously
 * with other uses of the FFTW planner.
 *
 * @warning The @p output array is assumed to be already allocated.  This may
 * be the same pointer as for @p data, but if not, the array should not
 * overlap @p data.
 */
MATS_LIB int imfilter(size_t Mdata, size_t Ndata, const double* data,
    size_t Mfilt, size_t Nfilt, const double* filter, double* output);


/**
 * Compute a ring windows mean and variance for every pixel of an image using a
 * sliding window.
 *
 * @param[in] nr Number of rows in the image.
 * @param[in] nc Number of columns in the image.
 * @param[in] img The image to process.
 * @param[in] core_sz Diameter of missing center of ring.
 * @param[in] ring_sz Diameter of ring.
 * @param[out] out_mean Computed mean matrix.
 * @param[out] out_vars Computed variance matrix.
 *
 * @warning @p out_mean and @p out_vars arrays are assumed to be already
 * allocated. They should be allocated to the same size as @p img.
 */
template<class DT> MATS_LIB int
img_ring_stats(size_t nr, size_t nc, const DT *img, size_t core_sz,
    size_t ring_sz, DT *out_mean, DT *out_vars);


/**
 * Dilates an image with a square kernel (constant border).
 *
 * @param[in] nr Number of rows in the image.
 * @param[in] nc Number of columns in the image.
 * @param[in] img_src Source image.
 * @param[in] kernel_size Size of kernel.
 * @param[in] iter Number of iterations to apply.
 * @param[out] img_dst Dilated image.
 * @return int Returns zero on success.
 */
template<class DT> MATS_LIB int
dilate(size_t nr, size_t nc, const DT *img_src, size_t kernel_size, size_t iter,
    DT *img_dst);


/**
 * Dilates an image with a square kernel (constant border).
 *
 * @note A vector<bool> is specialization of vector that is more efficient than
 *       (and not compatible with) a bool array. Hence, our specialization to
 *       make use of it.
 * @param[in] nr Number of rows in the image.
 * @param[in] nc Number of columns in the image.
 * @param[in] img_src Source image.
 * @param[in] kernel_size Size of kernel.
 * @param[in] iter Number of iterations to apply.
 * @param[out] img_dst Dilated image.
 * @return int Returns zero on success.
 */
MATS_LIB int
dilate(size_t nr, size_t nc, const std::vector<bool> &img_src,
    size_t kernel_size, size_t iter, std::vector<bool> &img_dst);


/**
 * Erodes an image with a square kernel (constant border).
 *
 * @param[in] nr Number of rows in the image.
 * @param[in] nc Number of columns in the image.
 * @param[in] img_src Source image.
 * @param[in] kernel_size Size of kernel.
 * @param[in] iter Number of iterations to apply.
 * @param[out] img_dst Dilated image.
 * @return int Returns zero on success.
 */
template<class DT> MATS_LIB int
erode(size_t nr, size_t nc, const DT *img_src, size_t kernel_size, size_t iter,
    DT *img_dst);


/**
 * Erodes an image with a square kernel (constant border).
 *
 * @note A vector<bool> is specialization of vector that is more efficient than
 *       (and not compatible with) a bool array. Hence, our specialization to
 *       make use of it.
 * @param[in] nr Number of rows in the image.
 * @param[in] nc Number of columns in the image.
 * @param[in] img_src Source image.
 * @param[in] kernel_size Size of kernel.
 * @param[in] iter Number of iterations to apply.
 * @param[out] img_dst Dilated image.
 * @return int Returns zero on success.
 */
MATS_LIB int
erode(size_t nr, size_t nc, const std::vector<bool> &img_src,
    size_t kernel_size, size_t iter, std::vector<bool> &img_dst);


/**
 * Sort the values in @p data.  Also, return the reordered indices.
 *
 * @param[in] N The length of the data array.
 * @param[in,out] data The array of values to be sorted.
 * @param[out] indices The array of indices after sorting.
 *
 * @return Returns 0 on success.
 *
 * @warning Function assumes @p indices is already allocated.
 */
template<class DT> MATS_LIB int
sort_with_indices(size_t N, DT* data, size_t* indices);


/**
 * Sort the values in @p data.  Also, return the reordered indices.
 *
 * @param[in,out] data The array of values to be sorted.
 * @param[out] indices The array of indices after sorting.
 *
 * @return Returns 0 on success.
 */
template<class DT> MATS_LIB int
sort_with_indices(std::vector<DT>* data, std::vector<size_t>* indices);


/**
 * Find the unique values in input (in sorted order).  N must be at least 1.
 *
 * @param[in] N Number of elements in data array.
 * @param[in] data The array of values.
 * @param[out] output The (sorted) unique values in the data array.
 *
 * @return Returns 0 on success.
 *
 * @warning The @p data array is changed.
 */
template<class DT> MATS_LIB int
unique(size_t N, DT* data, std::vector<DT>* output);


/**
 * Find the maximum element in an array and its index.
 *
 * @param[in] N Number of elements in data array.
 * @param[in] data The array of values.
 * @param[out] maximum The maximum element value.
 * @param[out] index The index of the (first occurring) maximum.
 *
 * @return Returns 0 on success.
 */
template<class DT> MATS_LIB int
max_with_index(size_t N, const DT* data, DT* maximum, size_t* index);


/**
 * Find the minimum element in an array and its index.
 *
 * @param[in] N Number of elements in data array.
 * @param[in] data The array of values.
 * @param[out] minimum The minimum element value.
 * @param[out] index The index of the (first occurring) minimum.
 *
 * @return Returns 0 on success.
 */
template<class DT> MATS_LIB int
min_with_index(size_t N, const DT* data, DT* minimum, size_t* index);


/**
 * Uses 1D nearest-neighbor method to fill in NaN values.
 *
 * @param[in] dir Direction to fill (1 - along rows, 2 - along columns).
 * @param[in] nr Number of rows.
 * @param[in] nc Number of columns.
 * @param[in,out] A Array to be filled.
 */
template<class DT> MATS_LIB int
fillmissing(int dir, size_t nr, size_t nc, DT *A);


/**
 * General square matrix inversion.
 *
 * @note Uses Eigen Matrix inversion.
 *
 * @param[in] N Number of rows of matrix (equal to number of columns).
 * @param[in,out] A Matrix to be inversed ([ @p N x @p N ]).
 *
 * @return Returns 0 on success.
 */
template<class DT> MATS_LIB int inverse(int N, DT* A);


/**
 * Performs matrix multiplication:
 *
 * C := A*B
 *
 * @note Uses Eigen Matrix multiplication.  Column-major storage is assumed.
 *
 * @param[in] m Specifies the number of rows of the matrix 'A' and 'C'. Must be
 * at least zero.
 * @param[in] n Specifies the number of columns of the matrix 'B' and 'C'.
 * Must be at least zero.
 * @param[in] k Specifies the number of columns of the matrix 'A' and the
 * number of rows of the matrix 'B'. Must be at least zero.
 * @param[in] A Input Matrix [ @p m x @p k ]
 * @param[in] B Input Matrix [ @p k x @p n ]
 * @param[out] C Output Matrix [ @p m x @p n ]
 *
 * @return Returns 0 on success.
 */
template<class DT> MATS_LIB int
mtimes(int m, int n, int k, const DT* A, const DT* B, DT* C);


/**
 * Performs in-place matrix transpose.  Assumes column-major storage.
 *
 * @param[in] nr Number of rows.
 * @param[in] nc Number of columns.
 * @param[in,out] X Matrix to be transposed.
 *
 * @return Returns 0 on success.
 */
template<class DT> MATS_LIB int
inplace_transpose(size_t nr, size_t nc, DT* X);


/**
 * Downsample matrix.  Assumes column-major storage.
 *
 * Downsampling the imaginary portion @p Xi is optional.  If not used, set
 * this parameter to null.
 *
 * @param[in] nr Number of rows (in original matrix).
 * @param[in] nc Number of columns (in original matrix).
 * @param[in] Xr Matrix to downsample (real portion), [ @p nr x @p nc ].
 * @param[in] Xi Matrix to downsample (imaginary portion), [ @p nr x @p nc ].
 * @param[in] n Downsampling factor.
 * @param[in] phase Number of samples to offset when downsampling.
 * @param[in] dir Downsampling direction. Use 1 to downsample each row;
 * otherwise each column will be downsampled.
 * @param[out] Yr Downsampled matrix (real portion).
 * @param[out] Yi Downsampled matrix (imaginary portion).
 *
 * @return Returns 0 on success.
 *
 * @warning Output @p Yr (and @p Yi, if @p Xi is provided) must be
 * pre-allocated. One dimension will stay the same size, depending on whether
 * rows or columns are downsampled. The other dimension will be reduced to
 * ceil((original size - @p phase) / @p n).
 */
template<class DT> MATS_LIB int
downsample(size_t nr, size_t nc, const DT* Xr, const DT* Xi, size_t n,
    size_t phase, int dir, DT* Yr, DT* Yi);


/**
 * Calculate covariance matrix of two real vectors, normalized by @p N - 1.
 * Output is a real, symmetric matrix in double precision.
 *
 * @param[in] N Length of each vector, @p A and @p B.
 * @param[in] A First vector.
 * @param[in] B Second vector.
 * @param[out] C Covariance matrix, [ 2 x 2 ].
 *
 * @return Returns 0 on success.
 *
 * @warning Output @p C must be pre-allocated (4 elements).
 */
template<class DT> MATS_LIB int
covmat(size_t N, const DT* A, const DT* B, double* C);


/**
 * Calculate major and minor axis lengths for a region.  Inputs @p A and @p B
 * are length @p N arrays of x and y coordinates, respectively.
 *
 * @param[in] N Number of points.
 * @param[in] A Length @p N array of x coordinates.
 * @param[in] B Length @p N array of y coordinates.
 * @param[out] majorLength Major axis length.
 * @param[out] minorLength Minor axis length.
 * @param[out] orientation (Optional) Orientation in degrees, CCW from x-axis.
 *
 * @return Returns 0 on success.
 */
template<class DT> MATS_LIB int axisLengths(size_t N, const DT* A, const DT* B,
    double* majorLength, double* minorLength, double* orientation = NULL);


/**
 * Calculate eigenvalues of a real, symmetric 2x2 matrix @p A.
 * Largest eigenvalue is first, smallest eigenvalue is second.
 *
 * @param[in] A Real, symmetric matrix [ 2 x 2 ].
 * @param[out] eigval Pointer to eigenvalue array (2 elements).
 *
 * @return Returns 0 on success.
 *
 * @warning Output @p eigval must be pre-allocated (2 elements).
 * @warning The input matrix @p A is assumed to be symmetric.  Only elements 0,
 * 1, and 3 are used.
 */
MATS_LIB int eigenvalRS2(const double* A, double* eigval);


/**
 * In-place counterclockwise rotation of points about a reference point.
 *
 * @param[in] ref Reference point for rotation. [ 2 x 1 ]
 * @param[in] rot Amount of rotation (radians).
 * @param[in] N Number of points.
 * @param[in,out] pts Points to be rotated, column-major order. [ 2 x @p N ]
 *
 * @return Returns 0 on success.
 */
template<class DT> MATS_LIB int
rotatePoints(const DT* ref, DT rot, size_t N, DT* pts);


/******************************************************************************
 Image Processing Functions
 *****************************************************************************/

/**
 * Finds connected regions of a binary image (column-major).
 *
 * @param[in] nr Number of rows in binary image.
 * @param[in] nc Number of columns in binary image.
 * @param[in] bw Binary image [nr x nc].
 * @param[out] lbls Labeled image [nr x nc].
 *
 * @return Returns the number of regions.
 *
 * @warning Function assumes @p lbls is already allocated.
 */
MATS_LIB int bwlabel(size_t nr, size_t nc, const bool* bw, int* lbls);


/**
 * Finds connected regions of a binary image (column-major).
 *
 * @param[in] nr Number of rows in binary image.
 * @param[in] nc Number of columns in binary image.
 * @param[in] bw Binary image [nr x nc].
 * @param[out] lbls Labeled image [nr x nc].
 *
 * @return Returns the number of regions.
 *
 * @warning Function assumes @p lbls is already allocated.
 */
MATS_LIB int
bwlabel(size_t nr, size_t nc, const std::vector<bool> &bw, int* lbls);


/**
 * Measures properties of binary image regions (column-major).
 *
 * @param[in] nr Number of rows in binary image.
 * @param[in] nc Number of columns in binary image.
 * @param[in] bw Binary image [nr x nc].
 *
 * @return Vector of %MATS structures containing properties for each binary
 * image region. Current properties include:
 * @li Area         - (int) Scalar that specifies the number of pixels in the
 *                    region.
 * @li BoundingBox  - (int [1x4]) Smallest rectangle containing region
 *                    [upperLeftRowIndex upperLeftColIndex rowWidth colWidth].
 * @li Centroid     - (double [1x2]) Center of mass for region [row, col].
 * @li PixelIdxList - (int) Array of linear indices of the pixels in the region.
 * @li MajorAxisLength - (double) Length (in pixels) of the major axis of the
 *                       ellipse that has the same normalized second central
 *                       moments as the region.
 * @li MinorAxisLength - (double) Length (in pixels) of the minor axis of the
 *                       ellipse that has the same normalized second central
 *                       moments as the region.
 * @li Orientation  - (double) Angle between the x-axis and the major axis of
 *                    the ellipse that has the same second-moments as the
 *                    region. The value is in degrees, between -90 and 90.
 *
 * @warning Note that this function gives some properties, such as Centroid
 * and BoundingBox entries, in a different order than the MATLAB version. Also,
 * the MATLAB version gives the first two BoundingBox entries as a half-index.
 */
MATS_LIB std::vector<mats::MATS_struct>
regionprops(size_t nr, size_t nc, const bool* bw);


/**
 * Measures properties of binary image regions (column-major).
 *
 * @param[in] nr Number of rows in binary image.
 * @param[in] nc Number of columns in binary image.
 * @param[in] bw Binary image [nr x nc].
 *
 * @return Vector of %MATS structures containing properties for each binary
 * image region. Current properties include:
 * @li Area         - (int) Scalar that specifies the number of pixels in the
 *                    region.
 * @li BoundingBox  - (int [1x4]) Smallest rectangle containing region
 *                    [upperLeftRowIndex upperLeftColIndex rowWidth colWidth].
 * @li Centroid     - (double [1x2]) Center of mass for region [row, col].
 * @li PixelIdxList - (int) Array of linear indices of the pixels in the region.
 * @li MajorAxisLength - (double) Length (in pixels) of the major axis of the
 *                       ellipse that has the same normalized second central
 *                       moments as the region.
 * @li MinorAxisLength - (double) Length (in pixels) of the minor axis of the
 *                       ellipse that has the same normalized second central
 *                       moments as the region.
 * @li Orientation  - (double) Angle between the x-axis and the major axis of
 *                    the ellipse that has the same second-moments as the
 *                    region. The value is in degrees, between -90 and 90.
 *
 * @warning Note that this function gives some properties, such as Centroid
 * and BoundingBox entries, in a different order than the MATLAB version. Also,
 * the MATLAB version gives the first two BoundingBox entries as a half-index.
 */
MATS_LIB std::vector<mats::MATS_struct>
regionprops(size_t nr, size_t nc, const std::vector<bool> &bw);


/**
 * Tries to find target highlight in image. Algorithm assumes image data is
 * zero mean and std one.
 *
 * The following fields should be included in the @p opt input:
 *     @li F1 (double): Filter array for finding highlight.
 *     @li energyfn (int): Selection of function for calculating energy in a
 * region. Use 0 for mean, or 1 for sum.
 *
 * @param[in] nr Number of rows in image.
 * @param[in] nc Number of columns in image.
 * @param[in] img Image (column-major storage).
 * @param[in] minMass Minimum number of pixels for highlight.
 * @param[in] opt Additional parameters.
 * @param[out] reg Properties of highlight region.
 *
 * @return Returns 0 on success.
 */
template<class DT> MATS_LIB int find_highlight(size_t nr, size_t nc,
    const DT* img, double minMass, const mats::MATS_struct& opt,
    mats::MATS_struct* reg);


/**
 * Crops image to given index ranges. Function assumes column major storage and
 * uses input matrix for output. Memory is not reallocated. Desired image
 * portion is moved to the beginning of input matrix.
 *
 * @param[in] nr Number of rows.
 * @param[in] nc Number of columns.
 * @param[in,out] X Array with matrix values.
 * @param[in] rix1 Starting row index.
 * @param[in] rix2 Ending row index.
 * @param[in] cix1 Starting column index.
 * @param[in] cix2 Ending column index.
 *
 * @return Returns 0 on success.
 */
template<class DT> MATS_LIB int img_inplace_crop(size_t nr, size_t nc, DT* X,
    size_t rix1, size_t rix2, size_t cix1, size_t cix2);


/**
 * Histogram of image data.
 *
 * @param[in] n Number of samples in image data.
 * @param[in] x Image data matrix.
 * @param[in] nbins Number of bins.
 * @param[out] counts Vector of counts for each bin (1 x nbins).
 * @param[out] bins Location of each bin (1 x nbins).
 *
 * @return Returns 0 on success.
 */
template<class DT> MATS_LIB int imhist(size_t n, DT *x, size_t nbins,
    size_t *counts, DT *bins);


/**
 * Dynamic range compression for sas imagery.  Specificialy for cases where
 * gammaclip is not providing acceptable results. This algorithm stretches the
 * dynamic range of typical bottom returns to range between 0 and lowRangeMax.
 * The highlight dynamic range is also stretched to range between upperRangeMin
 * and 1.  The mid-intensity points (clipBot to clipTop) dynamic range is
 * compressed.
 *
 * @param[in] nr Number of rows.
 * @param[in] nc Number of columns.
 * @param[in,out] M Array to be clipped.
 * @param[in] rangeMax Upper limit of lower and mid ranges return after
 *     adjustment (length 2 array).
 * @param[in] rangePercent Percent of values to be placed in the lower and mid
 *     range (length 2 array).
 * @param[in] clipRange Clipping minimum and maximum for intensities
 *     (length 2 array).
 *
 * @note Suggested values are:
 *         rangeMax = [0.05, 0.6]
 *         rangePercent = [0.05, 0.99]
 *         clipRange = [0.02, 0.95]
 *       or mimic the original clipping scheme:
 *         rangeMax = [0.4, 1.0]
 *         rangePercent = [0.99, 1.0]
 *         clipRange = [0.001, 0.7]
 */
template<class DT> MATS_LIB int clip_image(size_t nr, size_t nc, DT *M,
    const DT *rangeMax = 0, const DT *rangePercent = 0,
    const DT *clipRange = 0);


/******************************************************************************
 String Manipulation Functions
 *****************************************************************************/

/**
 * Splits a string into a vector of strings based given delimiter. For example,
 * if your delimiter is '|', the string 'blue|red|green' will return the strings
 * 'blue', 'red', 'green'. Leading and trailing delimiter are removed. Empty
 * strings between delimiters are also removed.
 *
 * @param[in] inStr Input string.
 * @param[in] delimiter Character that indicates where strings should be split.
 *
 * @return Returns vector of strings after splitting.
 */
MATS_LIB std::vector<std::string>
str_split(const std::string& inStr, char delimiter);


/**
 * Removes special characters ('\\t', '\\n', '\\r', '\\v', '\\f') from string.
 *
 * @param[in,out] inStr String to be processed.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int str_clean(std::string* inStr);


/**
 * Removes hidden characters from beginning and end of string.
 *
 * @param[in,out] inStr String to be processed.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int str_trim(std::string* inStr);


/**
 * Convert numerical value to a string. Valid numerical types are int, unsigned
 * int, float, double.
 *
 * @param[in] val Numerical value.
 *
 * @return Returns string corresponding to numerical value.
 */
template<class DT> MATS_LIB std::string to_string(DT val);

}  // namespace mats

#endif  // SRC_MATS_BASIC_H_
