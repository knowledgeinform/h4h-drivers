/**
 * @file
 * @brief File contains the MATS_perf performance estimation structure.
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
#ifndef SRC_MATS_PERF_H_
#define SRC_MATS_PERF_H_

#include "MATS_data.h"


namespace mats {


/**
 * Structure for storing performance estimation information.
 */
struct MATS_perf {
  MATS_perf(): fapi(0.0f), B(0.0f) {}

  /**
   * Clear contents.
   */
  void clear() {
    pdpc.clear();
    lfa.clear();
    fapi = 0.0f;
    B = 0.0f;
    return;
  }

  MATS_data pdpc; /**< estimated PdPc at each pixel (same size as image) */
  MATS_data lfa; /**< estimated likelihood of false alarm at each pixel */
  float fapi; /**< estimated number of false alarms per image */
  float B; /**< average estimated PdPc (whole image) */
};


}  // namespace mats

#endif  // SRC_MATS_PERF_H_
