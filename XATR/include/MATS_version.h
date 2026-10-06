/**
 * @file MATS_version.h
 * @brief File provides the routine for getting the version of MATS_core
 * being compiled against; must be included in a package for version checking.
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
#ifndef SRC_MATS_VERSION_H_
#define SRC_MATS_VERSION_H_


#include "MATS_platform.h"


namespace mats {

/**
 * The version of the MATS_core header (the version of the MATS_core library
 * compiled against).
 */
static const char* mats_core_version = "1.2.0b6-ddb7ddee";

}  // namespace mats

/**
 * Get the MATS_core version compiled against.
 *
 * @return Returns the MATS_core version compiled against.
 */
extern "C" MATS_LIB const char* get_mats_core_version() {
  return mats::mats_core_version;
}

#endif  // SRC_MATS_VERSION_H_
