/**
 * @file
 * @brief File contains functions for file compression and extraction.
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
#ifndef SRC_MATS_GZIP_H_
#define SRC_MATS_GZIP_H_

#include "MATS_platform.h"


namespace mats {

/**
 * Compress a file.
 *
 * @param[in] source Path to source file.
 * @param[in] dest Path to destination file.
 * @param[in] level Compression level. Possible values include:
 *     - Z_NO_COMPRESSION         0
 *     - Z_BEST_SPEED             1
 *     - Z_BEST_COMPRESSION       9
 *     - Z_DEFAULT_COMPRESSION  (-1)
 *
 * @return Returns 0 on success. Return codes are as follows:
 *     - Null pointer    3
 *     - Z_OK            0
 *     - Z_STREAM_END    1
 *     - Z_NEED_DICT     2
 *     - Z_ERRNO        (-1)
 *     - Z_STREAM_ERROR (-2)
 *     - Z_DATA_ERROR   (-3)
 *     - Z_MEM_ERROR    (-4)
 *     - Z_BUF_ERROR    (-5)
 *     - Z_VERSION_ERROR (-6)
 */
MATS_LIB int
file_deflate(const char* source, const char* dest, int level);


/**
 * Decompress a file.
 *
 * @param[in] source Path to source file.
 * @param[in] dest Path to destination file.
 *
 * @return Returns 0 on success. Return codes are as follows:
 *     - Null pointer    3
 *     - Z_OK            0
 *     - Z_STREAM_END    1
 *     - Z_NEED_DICT     2
 *     - Z_ERRNO        (-1)
 *     - Z_STREAM_ERROR (-2)
 *     - Z_DATA_ERROR   (-3)
 *     - Z_MEM_ERROR    (-4)
 *     - Z_BUF_ERROR    (-5)
 *     - Z_VERSION_ERROR (-6)
 */
MATS_LIB int
file_inflate(const char* source, const char* dest);

}  // namespace mats

#endif  // SRC_MATS_GZIP_H_
