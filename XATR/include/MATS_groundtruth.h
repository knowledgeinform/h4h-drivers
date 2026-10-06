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
#ifndef SRC_MATS_GROUNDTRUTH_H_
#define SRC_MATS_GROUNDTRUTH_H_

#include "MATS_platform.h"
#include <string>
#include <vector>
#include <map>


namespace mats {

/**
 * %MATS ground truth substructure.
 */
struct MATS_LIB MATS_groundtruth {
  size_t x; /**< Cross-range pixel index. */
  size_t y; /**< Along-track pixel index. */
  size_t num; /**< Identifier for ground truth object. */
  size_t dim[2]; /**< Bounding box dimensions of ground truth object. */

  /**
   * Object type (multi-class classifiers only). Set to -99 for unknown.
   */
  int type;

  std::string fn; /**< Filename of file containing ground truth object. */
  std::string side; /**< Side of vehicle ground truth object is located. */
};


/**
 * Move @p source MATS_groundtruth vector to the end of @p dest
 * MATS_groundtruth vector.
 *
 * @param[in,out] dest Destination MATS_groundtruth vector.
 * @param[in,out] source Source MATS_groundtruth vector (will be cleared upon
 * successful completion).
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
mats_gt_list_append(std::vector<mats::MATS_groundtruth>& dest,
    std::vector<mats::MATS_groundtruth>& source);


/**
 * Read ground truth data from a file. Ground truth files must have a comment
 * heading that indicates what the columns of data are.  Fields X, Y, and
 * FILENAME are required in all cases. TYPE is also required in the multiclass
 * case.
 *
 * @param[in] gtf Ground truth filename (include path to file).
 * @param[out] gt Ground truth information from file.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
generic_gt_reader(const char* gtf, std::vector<MATS_groundtruth>& gt);

}  // namespace mats

#endif  // SRC_MATS_GROUNDTRUTH_H_