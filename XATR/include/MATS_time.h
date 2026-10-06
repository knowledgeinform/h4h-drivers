/**
 * @file
 * @brief File contains the MATS_datetime structure and date/time routines.
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
#ifndef SRC_MATS_TIME_H_
#define SRC_MATS_TIME_H_

#include <stdint.h>

#include <string>

#include "MATS_platform.h"


namespace mats {

/**
 * Date/time structure
 */
struct MATS_datetime {
  unsigned int year; /**< Year (C.E.) */
  unsigned int month; /**< Month of the year (01-12) */
  unsigned int day; /**< Day of the month (01-31) */
  unsigned int hour; /**< Hour value (00-24) */
  unsigned int minute; /**< Minute value (00-59) */
  double dsecond; /**< Decimal seconds value */
};


/**
 * Obtain lock for non-thread safe standard C time function call.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int mats_lock_time();


/**
 * Release lock for non-thread safe standard C time function call.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int mats_unlock_time();


/**
 * Displays a MATS_datetime as a standard date/time string.
 * String format:  MM/DD/YYYY HH:MM:SS
 * This function only works if the MATS_DEBUG flag is set.
 *
 * @param[in] date The MATS_datetime to display.
 */
MATS_LIB void display(const MATS_datetime& date);


/**
 * Converts a MATS_datetime to a double (the number of seconds since the epoch:
 * 00:00 hours, Jan 1, 1970 UTC).
 *
 * @param[in] date The MATS_datetime to convert.
 *
 * @return Returns the number of seconds since the epoch. If @p date is
 * invalid, returns 0.
 */
MATS_LIB double datenum(const MATS_datetime& date);


/**
 * Converts a standard date/time string to a double using the 1/1/1970 epoch.
 * String format:  MM/DD/YYYY HH:MM:SS
 *
 * @param[in] datetime The date/time string.
 *
 * @return Returns the number of seconds since the epoch.
 */
MATS_LIB double datenum(const std::string& datetime);


/**
 * Converts a double to a MATS_datetime assuming the 1/1/1970 epoch.
 *
 * @param[in] utc The number of seconds since the epoch.
 *
 * @return Returns the corresponding MATS_datetime.
 */
MATS_LIB MATS_datetime datetime(double utc);


/**
 * Converts a double to a standard date/time string using the 1/1/1970 epoch.
 * String format:  MM/DD/YYYY HH:MM:SS
 *
 * @param[in] utc The number of seconds since the epoch.
 * @param[out] datestring The resulting date/time string.
 */
MATS_LIB void
datestr(double utc, std::string& datestring);


/**
 * Converts a MATS date/time structure to a standard date/time string.
 * String format:  MM/DD/YYYY HH:MM:SS
 *
 * @param[in] dt MATS date/time structure.
 * @param[out] datestring The resulting date/time string.
 */
MATS_LIB void
datestr(const mats::MATS_datetime &dt, std::string& datestring);


/**
 * Returns the current date/time. Default is to return UTC date/time (GMT).
 * Set @p local to true to return local time.
 *
 * @param[in] local Enables return of local time.
 *
 * @note Function uses mats_lock_time for thread safety.
 */
MATS_LIB MATS_datetime datenow(bool local=false);


/**
 * Returns whether a year is a leap year.
 *
 * @param[in] year Year to be tested.
 *
 * @return Returns true if year is a leap year, false otherwise.
 */
MATS_LIB bool is_leap_year(unsigned int year);


/**
 * Correct MATS_datetime information for daylight savings time.
 *
 * @param[in,out] t Date/time information to be corrected.
 */
MATS_LIB void dst_correction(MATS_datetime& t);


/**
 * Converts a double to a standard date/time string using the 1/1/1970 epoch.
 * String format uses a W3C profile of ISO 8601:  "Complete date plus hours,
 * minutes, seconds and a decimal fraction of a second".  For use in
 * ContactProduct XML documents.
 *
 * String format is approximately: yyyy-mm-ddThh:mm:ss.sZ
 *
 * @param[in] utc The number of seconds since the epoch.
 * @param[out] date The date/time string in W3C format.
 */
MATS_LIB void
w3cformat(double utc, std::string& date);


/**
 * Converts a MATS date/time structure to a string. String format uses a W3C
 * profile of ISO 8601:  "Complete date plus hours, minutes, seconds and a
 * decimal fraction of a second".
 *
 * String format is approximately: yyyy-mm-ddThh:mm:ss.sZ
 *
 * @param[in] dt MATS date/time structure.
 * @param[out] date The date/time string in W3C format.
 */
MATS_LIB void
w3cformat(const mats::MATS_datetime &dt, std::string& date);


/**
 * Returns the amount of milliseconds elapsed since the UNIX epoch.
 */
MATS_LIB uint64_t clock_time_ms();


/**
 * MATS_timer object can be used to time code execution.
 */
class MATS_LIB MATS_timer {
 public:
  /**
   * MATS_timer default constructor. Initializes timer.
   */
  MATS_timer();

  /**
   * Starts timer.
   */
  void start();

  /**
   * Stops timer.
   */
  void stop();

  /**
   * Resets timer.
   */
  void reset();
  
  /**
   * Logs timer duration to log file.
   */
  int log(const char *txt=0, bool verbose=0);

 private:
  uint64_t _t0;
  uint64_t _t1;
};

}  // namespace mats

#endif  // SRC_MATS_TIME_H_
