/**
 * @file
 * @brief File contains routines for handling files, directories, and paths.
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
#ifndef SRC_MATS_FILESYSTEM_H_
#define SRC_MATS_FILESYSTEM_H_

#include <string>
#include <stdarg.h>

#include "MATS_platform.h"


namespace mats {

/**
 * Set/return the %MATS install directory.  If @p path equals "{default}", the
 * install directory will be reset to the default value.
 *
 * @param[in] path (Optional) Path to set install directory.
 *
 * @return Returns the %MATS install directory.
 */
MATS_LIB std::string
mats_install_dir(const char* path = NULL);


/**
 * Set/return the %MATS working directory.  If @p path equals "{default}", the
 * working directory will be reset to the default value.
 *
 * @param[in] path (Optional) Path to set working directory.
 *
 * @return Returns the %MATS working directory.
 */
MATS_LIB std::string
mats_working_dir(const char* path = NULL);


/**
 * Set/return the %MATS log file path.  If @p filepath equals "{default}", the
 * log file path will be reset to the default value: "atr_log.txt" in the
 * working directory.
 *
 * @param[in] filepath (Optional) Complete path and filename to set log file
 * location.
 *
 * @return Returns the %MATS log file path.
 */
MATS_LIB std::string
mats_log_file(const char* filepath = NULL);


/**
 * Get the path to the %MATS configuration directory.
 *
 * @return Returns the %MATS configuration directory.
 */
MATS_LIB std::string
mats_config_dir();


/**
 * Get the path to the %MATS output directory.
 *
 * @return Returns the %MATS output directory.
 */
MATS_LIB std::string
mats_output_dir();


/**
 * Get the path to the %MATS package directory.
 *
 * @return Returns the %MATS package directory.
 */
MATS_LIB std::string
mats_package_dir();


/**
 * Get the path to the %MATS Python directory.
 *
 * @return Returns the %MATS Python directory.
 */
MATS_LIB std::string
mats_python_dir();


/**
 * Get the path to the %MATS unit test directory.
 *
 * @return Returns the %MATS unit test directory.
 */
MATS_LIB std::string
mats_test_dir();


/**
 * Get the file path separator character used on the current system, e.g.,
 * '/' for Unix, '\' for Windows.
 *
 * @return Returns the file path separator character.
 */
MATS_LIB char
mats_filesep();


/**
 * Get the file path delimiter character used on the current system, e.g.,
 * ':' for Unix, ';' for Windows.
 *
 * @return Returns the file path delimiter character.
 */
MATS_LIB char
mats_filedelim();


/**
 * Check whether a file exists.
 *
 * @param[in] filename File to check.
 *
 * @return Returns true if the file exists; false otherwise.
 */
MATS_LIB bool
file_exist(const char* filename);


/**
 * Check whether a file exists.
 *
 * @param[in] filename File to check.
 *
 * @return Returns true if the file exists; false otherwise.
 */
MATS_LIB bool
file_exist(const std::string &filename);


/**
 * Split a full path into the folder path and the filename.
 *
 * @param[in] filePath Full path to be split.
 * @param[out] pathTo Folder containing the file (including file separator at
 * the end).
 * @param[out] filename Just the filename (with extension).
 */
MATS_LIB void
file_parts(const char* filePath, std::string& pathTo, std::string& filename);


/**
 * Add a partial path onto an existing path.
 *
 * @param[in,out] filePath Existing path to be extended.
 * @param[in] part Partial path to be appended onto existing path.
 */
MATS_LIB void
file_path(std::string& filePath, const std::string& part);


/**
 * Add a partial path onto an existing path.
 *
 * @param[in,out] filePath Existing path to be extended.
 * @param[in] part Partial path to be appended onto existing path.
 */
MATS_LIB void
file_path(std::string& filePath, const char* part);


/**
 * Retrieve the basename of a file from a full path or full filename.
 *
 * @param[in] filename Path or filename.
 * @param[out] basename Basename of the file (name of the file up to but not
 * including the first dot, and not including the path).
 */
MATS_LIB void
file_basename(const char* filename, std::string& basename);


/**
 * Retrieve the extension of a file from a full path or full filename.
 *
 * @param[in] filename Path or filename.
 * @param[out] ext Extension of the file.
 */
MATS_LIB void
file_extension(const char* filename, std::string& ext);


#ifdef MATS_LINUX
/**
 * Read value of symbolic link.
 *
 * @param[in] filename Filename of symbolic link.
 * @param[out] linkpath Read symbolic link path.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
file_readlink(const char* filename, std::string& linkpath);
#endif


/**
 * Returns size of file in bytes.
 *
 * @param[in] filename Filename.
 *
 * @return Returns file size in bytes upon success. Upon failure, returns -1.
 */
MATS_LIB int file_size(const char* filename);


/**
 * Makes a copy of a file from @p src to @p dst.
 *
 * @param[in] src Source path the file.
 * @param[in] src. Destination file path.
 */
MATS_LIB int file_copy(const char *src, const char *dst);


/**
 * Returns time file was last modified (typically, the number of seconds
 * elapsed since 00:00 hours, Jan 1, 1970 UTC).
 *
 * @param[in] filename Filename.
 *
 * @return Returns file modification time upon success. Upon failure,
 * returns -1.
 */
MATS_LIB double file_mod_time(const char* filename);


/** Structure for file handling */
struct MATS_file {
  std::string name;  /**< Name of file */
  std::string path;  /**< Path to directory containing file */
  bool isdir;  /**< Directory flag */
  double date;  /**< Modification date timestamp */

  /**
   * Less-than operator. First compares file path then name.
   *
   * @param[in] in MATS_file to compare.
   */
  bool operator<(const MATS_file& in) const {
    return (path < in.path && name < in.name);
  }

  /**
   * Greater-than operator. First compares file path then name.
   *
   * @param[in] in MATS_file to compare.
   */
  bool operator>(const MATS_file& in) const {
    return (path > in.path && name > in.name);
  }
};


/**
 * Returns true if given path is a directory.
 *
 * @param[in] path Filesystem path.
 *
 * @return Returns true if path is a directory; false otherwise.
 */
MATS_LIB bool
is_dir(const char* path);


/**
 * Returns true if given path is a directory.
 *
 * @param[in] path Filesystem path.
 *
 * @return Returns true if path is a directory; false otherwise.
 */
MATS_LIB bool
is_dir(const std::string &path);


/**
 * Returns a list of files in a directory.
 *
 * @param[in] dirname Path to directory.
 *
 * @return Returns list of MATS_file objects corresponding to files in
 * directory.
 */
MATS_LIB std::vector<MATS_file>
dir_list(const char* dirname);


/**
 * Creates directory if it does not exist.
 *
 * @param[in] dirname Name of directory.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
create_directory(const char* dirname);


/**
 * Creates directory if it does not exist.
 *
 * @param[in] dirname Name of directory.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
create_directory(const std::string &dirname);


/**
 * Removes an empty directory.
 *
 * @param[in] dirname Name of directory.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
remove_directory(const char* dirname);


/**
 * Return full filename of MATS_file object.
 *
 * @param[in] file MATS_file object.
 *
 * @return Returns combined path and name fields of MATS_file input.
 */
MATS_LIB std::string
full_filename(const MATS_file &file);

}  // namespace mats

#endif  // SRC_MATS_FILESYSTEM_H_
