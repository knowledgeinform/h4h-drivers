/**
 * @file
 * @brief File contains routines for hashing and authorizing applications and
 * configurations.
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
#ifndef SRC_MATS_SECURITY_H_
#define SRC_MATS_SECURITY_H_

#include <vector>
#include <string>

#include "MATS_platform.h"


namespace mats {


/**
 * Initialize application and configuration authorization. For checking to
 * provide the maximum level of security, install directory should require
 * admin rights to write. This function will generate the 'mats_auth.json' file
 * and save it in the install directory. The 'mats_manager' program will be
 * authorized and all default programs.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
auth_init();


/**
 * Checks if application is authorized for use of sensitive %MATS functions.
 *
 * @return Returns true if application is authorized.
 */
MATS_LIB bool
auth_check();


/**
 * Remove an application's authorization.
 *
 * @remark Checks authorization before performing any actions.
 *
 * @param[in] app_name Name of application (basename only).
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
auth_remove(const std::string& app_name);


/**
 * Add or modify an application's authorization.
 *
 * @remark Checks authorization before performing any actions.
 *
 * @param[in] app_name Full path for application executable.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
auth_add(std::string app_name);


/**
 * Returns list of current authorized applications.
 *
 * @param[out] apps List of authorized applications.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
auth_display(std::vector<std::string>& apps);


/**
 * Checks if a configuration is authorized. Authorized configurations are
 * checked for tampering via checksum.
 *
 * @param[in] cfg_name Name of configuration (basename of file, usually a UUID).
 *
 * @return Returns true if configuration is authorized and has not been altered.
 */
MATS_LIB bool
cfg_auth_check(const std::string& cfg_name);


/**
 * Removes authorization for a configuration.
 *
 * @remark Checks authorization before performing any actions.
 *
 * @param[in] cfg_name Name of configuration (basename of file, usually a UUID).
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
cfg_auth_remove(const std::string& cfg_name);


/**
 * Adds authorization for a configuration.
 *
 * @remark Checks authorization before performing any actions.
 *
 * @param[in] cfg_name Name of configuration (basename of file, usually a UUID).
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
cfg_auth_add(const std::string& cfg_name);


/**
 * Returns SHA1 hash of a file.
 *
 * @param[in] fn Filename (full path).
 *
 * @return Returns the SHA1 hash of the file.
 */
MATS_LIB std::string
sha1_hash(const std::string& fn);


/**
 * Returns SHA1 hash of a string.
 *
 * @param[in] str String to be hashed.
 *
 * @return Returns the SHA1 hash of the string.
 */
MATS_LIB std::string
sha1_str_hash(const std::string& str);


/**
 * Returns SHA1 hash of a array.
 *
 * @param[in] str Array to be hashed.
 *
 * @return Returns the SHA1 hash of the array.
 */
template<class DT> MATS_LIB std::string
sha1_array_hash(size_t n, const DT *array);


/**
 * Append a random string to a password and return the SHA1 hash of the result.
 *
 * @param[in] passwd The password to be salted.
 *
 * @return Returns the SHA1 hash of the salted password.
 *
 * @note The salt (appended string) is randomly generated for each build.
 */
MATS_LIB std::string
mats_salt_password(const std::string& passwd);

}  // namespace mats

#endif  // SRC_MATS_SECURITY_H_
