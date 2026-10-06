/**
 * @file
 * @brief File contains macros and functions for handling errors and exceptions.
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
#include <sstream>

#include "MATS_platform.h"


#ifndef SRC_MATS_ERROR_H_
#define SRC_MATS_ERROR_H_


/**
 * A macro for logging an error or message. File, function, and line number
 * are filled in automatically.
 *
 * @param[in] type Type of error, a MATS_error_action.
 * @param[in] msg Message or description of error, a C string.
 *
 * @return Returns 0 on success.
 */
#define mats_log(type, msg) mats_error_report(__FILE__, __func__, \
  __LINE__, msg, type);


/**
 * A macro for handling an exception. File, function, and line number
 * are filled in automatically.
 *
 * @param[in] type Type of error, a MATS_error_action.
 * @param[in] msg Message or description of error, a C string.
 *
 * @return Returns 0 on success.
 */
#define mats_except(type, msg) mats_except_handler(__FILE__, __func__, \
  __LINE__, msg, type);


/**
 * @var typedef enum MATS_error_action
 * @brief Different levels of error messages.
 */
enum MATS_error_action {MATS_MSG, MATS_WARN, MATS_ERROR, MATS_FAIL};


/**
 * Logs error/message to log file. If MATS_DEBUG is defined, also prints
 * error/message to error stream.
 *
 * @param[in] file Filename of file where errors occured.
 * @param[in] func Function where error occured.
 * @param[in] line Line number where error occured.
 * @param[in] msg Message or error description.
 * @param[in] action Type of message/error.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
mats_error_report(const char* file, const char* func, int line,
    const char* msg, MATS_error_action action);


/**
 * Handles an exception by submitting an error report.
 * Logs error/message to log file. If MATS_DEBUG is defined, also prints
 * error/message to error stream.
 * The message is augmented with a description of the exception type.
 *
 * @param[in] file Filename of file where errors occured.
 * @param[in] func Function where error occured.
 * @param[in] line Line number where error occured.
 * @param[in] msg Message or error description.
 * @param[in] action Type of message/error.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
mats_except_handler(const char* file, const char* func, int line,
    const char* msg, MATS_error_action action);


/**
 * Enables message logging to log file. If @p filepath is provided, the log
 * file path is changed accordingly. If @p filepath equals "{default}", the
 * log file path will be reset to the default value: "atr_log.txt" in the
 * working directory.
 *
 * @note If the log file already exists and is at least 100 lines long, it
 * is moved to a backup file with added extension ".old". Any previous backup
 * is deleted.
 *
 * @param[in] filepath (Optional) Complete path and filename to set log file
 * location.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
mats_error_enable(const char* filepath = NULL);


/**
 * Disables message logging to log file. (Message printing to screen is still
 * enabled if MATS_DEBUG is defined.)
 */
MATS_LIB void
mats_error_disable();


/**
 * Changes level of errors that are reported. Default level is MATS_WARN.
 *
 * @param[in] level Minimum message level that is reported.
 */
MATS_LIB void
mats_error_report_level(MATS_error_action level);


/**
 * Type definition for MATS logger function.
 */
typedef int (*logger_func)(MATS_error_action etype, const char *where, const char *msg);


/**
 * Register a logging function callback.
 *
 * @param[in] func Logger function.
 */
MATS_LIB int
mats_logger_add(logger_func func);

#endif /* SRC_MATS_ERROR_H_ */
