/**
 * @file
 * @brief File contains routines for handling UUIDs.
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
#ifndef SRC_MATS_UUID_H_
#define SRC_MATS_UUID_H_

#include <string>

#include "MATS_platform.h"
#include "MATS_error.h"


namespace mats {

/**
 * Generate a new UUID string of the form 00000000-0000-0000-0000-000000000000.
 */
MATS_LIB std::string uuid_generator();


/**
 * Tests if two UUIDs are equal. Throws an exception if one of the inputs is
 * not a valid UUID.
 *
 * @param[in] uuidStr1 A UUID string.
 * @param[in] uuidStr2 A UUID string.
 *
 * @return Returns true if UUID strings are equal and false for not equal.
 */
MATS_LIB bool
uuid_equal(const std::string& uuidStr1, const std::string& uuidStr2);


/**
 * Verifies if a string is a valid UUID.
 *
 * @param[in] uuidStr A UUID string.
 *
 * @return Returns true if UUID string is of the form
 * 00000000-0000-0000-0000-000000000000. Otherwise, returns false.
 */
MATS_LIB bool is_uuid(const std::string& uuidStr);


/**
 * Convert a 36-character UUID string to a 16-character UUID char array.
 *
 * @param[in] uuidIn Input 36-character UUID string.
 * @param[out] uuidOut Output 16-character UUID char array (stored in string).
 *
 * @return Returns 0 on success.
 */
MATS_LIB int uuid_to_char(const std::string& uuidIn, std::string& uuidOut);

}  // namespace mats

#endif  // SRC_MATS_UUID_H_
