/**
 * @file
 * @brief File contains MATS implementations of clustering routines.
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
#ifndef SRC_MATS_CLUSTER_H_
#define SRC_MATS_CLUSTER_H_

#include <cstdlib>
#include "MATS_platform.h"
#include "MATS_struct.h"

namespace mats {

/**
 * Structure for storing a region of interest (ROI).
 */
struct MATS_roi {
  MATS_roi(): x(0.0), y(0.0), a_start(0.0), a_stop(0.0),
      c_start(0.0), c_stop(0.0), score(0.0), count(0) {}

  /**
   * Less-than operator.  Returns true if the score of the first MATS_roi is
   * less than the score of the second MATS_roi.
   *
   * @param[in] in MATS_roi to compare.
   */
  bool operator<(const MATS_roi& in) const {return (score < in.score);}

  /**
   * Greater-than operator.  Returns true if the score of the first MATS_roi
   * is greater than the score of the second MATS_roi.
   *
   * @param[in] in MATS_roi to compare.
   */
  bool operator>(const MATS_roi& in) const {return (score > in.score);}

  double x; /**< center cross-track */
  double y; /**< center along-track */
  double a_start; /**< along-track start */
  double a_stop; /**< along-track stop */
  double c_start; /**< cross-track start */
  double c_stop; /**< cross-track stop */
  double score; /**< score (e.g., detection score) */
  int count; /**< count */
};


/**
 * Returns the Euclidean distance between two ROIs.
 *
 * @param[in] R1 Region of interest.
 * @param[in] R2 Region of interest.
 */
MATS_LIB inline double
dist_euclidean(const MATS_roi& R1, const MATS_roi& R2);


/**
 * Returns the Chebyshev distance between two ROIs.
 *
 * @param[in] R1 Region of interest.
 * @param[in] R2 Region of interest.
 */
MATS_LIB inline double
dist_chebyshev(const MATS_roi& R1, const MATS_roi& R2);


/**
 * A standard kmeans clustering algorithm.
 *
 * @param[in] n Number of samples.
 * @param[in] dim Dimension of samples.
 * @param[in] data Data matrix (dim x n).
 * @param[in] numClusters Number of clusters to find.
 * @param[in] tol
 * @param[out] labels Cluster label for samples (1 x n).
 * @param[out] centroid Centroid matrix (dim x numClusters).
 * @param[out] ccDist Distance of points to centroids (n x numClusters).
 */
MATS_LIB void
batch_kmeans(size_t n, size_t dim, const double* data, size_t numClusters,
    double tol, int* labels, double* centroid, double* ccDist);


/**
 * Kmeans algorithm using elbow criterion to determine the number of
 * clusters.
 *
 * @param[in] n
 * @param[in] dim
 * @param[in] data
 * @param[in,out] labels
 * @param[in] maxtol
 * @param[in] maxClusters
 * @param[out] numClusters
 * @param[out] centroid
 *
 * @warning The output @p centroid is allocated in this function as size
 * @p numclusters x @p dim. It should be freed by the calling function.
 */
MATS_LIB void
elbkmeans(size_t n, size_t dim, const double* data, int* labels, double maxtol,
    size_t maxClusters, size_t* numClusters, double* &centroid);


/**
 * This function attempts to group image points of interest into
 * non-overlapping ROIs.
 *
 * @param[in] n Number of points to group.
 * @param[in] loc Array of pixel locations of points of interest to be grouped
 * into ROIs, e.g., [x1 y1 x2 y2 ...]. Size 2 * @p n. Note this order is
 * different from the order used in the MATLAB version of %roiFind().
 * @param[in] scores Array of weights indicating importance of points in @p loc
 * (higher value means more important). Values are used to center ROIs on the
 * more important points. Size @p n.
 * @param[in] roiDim Dimensions of ROI box. [along-track cross-track]
 * @param[in] dataDim Dimensions of data to restrict ROIs to. [anum cnum]
 * @param[in] opt Optional parameter overrides.
 * @param[out] labels Array of group labels assigned to @p loc point of
 * interest. Size @p n.
 * @param[out] rois Vector of ROIs.
 *
 * @warning Note that this is a template function. Using size_t for @p roiDim
 * and @p dataDim will cause the function to behave like MATLAB's %roiFind().
 * Using float or double for these parameters will cause the function to behave
 * like MATLAB's %roiFindm().
 *
 * @warning If @p n is greater than the limit (currently 2000), the entries of
 * @p labels will be reordered relative to the entries of @p loc and @p scores.
 * Specifically, the first 2000 entries of @p labels will correspond to the
 * highest 2000 entries of @p scores, in order of decreasing @p scores. In
 * this case, only the first 2000 entries of @p labels will be filled in.
 */
template<class DT> MATS_LIB void
roiFind(size_t n, const double* loc, const double* scores, const DT* roiDim,
    const DT* dataDim, const MATS_struct* opt, int* labels,
    std::vector<MATS_roi>& rois);

}  // namespace mats

#endif  // SRC_MATS_CLUSTER_H_
