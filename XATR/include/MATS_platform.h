/**
 * @file
 * @brief File contains macros and routines to support cross-platform
 * compatibility, versioning, and threading.
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
#ifndef SRC_MATS_PLATFORM_H_
#define SRC_MATS_PLATFORM_H_

#include <stdint.h>

#include <vector>
#include <string>

#ifdef _WIN32
#  ifdef MATS_EXPORT
#    define MATS_LIB __declspec(dllexport)
#  elif defined(MATS_IMPORT)
#    define MATS_LIB __declspec(dllimport)
#  else
#    define MATS_LIB
#  endif
#else
#  ifdef __GNUC__
#    if __GNUC__ >= 4
#      define MATS_LIB __attribute__((visibility ("default")))
#    else
#      define MATS_LIB
#    endif
#  else
#    define MATS_LIB
#  endif
#endif

// Platform type macros
#ifdef _WIN32
#  define MATS_WINDOWS
#elif defined(__linux__)
#  define MATS_LINUX
#elif defined(__APPLE__)
#  define MATS_APPLE
#endif


#ifdef UINT32_MAX
typedef uint32_t UINT32;
#else
typedef unsigned long UINT32;
#endif


#ifdef UINT16_MAX
typedef uint16_t UINT16;
#else
typedef unsigned int UINT16;
#endif


#ifdef UINT8_MAX
typedef uint8_t UINT8;
#else
typedef unsigned char UINT8;
#endif


/**
 * The mats namespace contains most %MATS classes and functions.
 */
namespace mats {

/**
 * The file path separator character used on the current system, e.g.,
 * '/' for Unix, '\' for Windows.
 */
extern const char filesep;


/**
 * The file path delimiter character used on the current system, e.g.,
 * ':' for Unix, ';' for Windows.
 */
extern const char filedelim;


/**
 * The version of the MATS_core library.
 */
extern const char* mats_version;


/**
 * %MATS version structure.
 */
struct MATS_version {
  MATS_version(): version(0), beta(0) {}

  /**
   * Less-than operator.
   *
   * @param[in] in MATS_version to compare.
   *
   * @return Returns true if the MATS_version is less than the compared version.
   */
  bool operator<(const MATS_version& in) const {
    if (version == in.version) {return (beta < in.beta);}
    return (version < in.version);
  }

  /**
   * Greater-than operator.
   *
   * @param[in] in MATS_version to compare.
   *
   * @return Returns true if the MATS_version is greater than the compared
   * version.
   */
  bool operator>(const MATS_version& in) const {
    if (version == in.version) {return (beta > in.beta);}
    return (version > in.version);
  }

  unsigned int version; /**< Major, minor, revision (XXX.XXX.XXX) */
  unsigned int beta; /**< Beta, alpha (bXXXaXXX) */
};


/**
 * Parse a version number from a string to a MATS_version.
 *
 * @param[in] verStr The version string.
 *
 * @return Returns the MATS_version corresponding to the string.
 */
MATS_LIB MATS_version
parse_mats_version(const char* verStr);


/**
 * Build a version string from a MATS_version.
 *
 * @param[in] ver The MATS_version to build into a string.
 *
 * @return Returns the string corresponding to the MATS_version.
 */
MATS_LIB std::string
build_mats_version(const MATS_version& ver);


/**
 * Compare %MATS version numbers.
 *
 * @param[in] ver1 Version number to check.
 * @param[in] ver2 (Optional) Version number to check against. If not supplied,
 * the current %MATS library version will be used.
 *
 * @return Returns -1 if the major version is different. Returns 1 if the minor
 * version is different. Returns 0 if major and minor versions match.
 */
MATS_LIB int
mats_check_version(const char* ver1, const char* ver2 = NULL);


/**
 * Get the version of the MATS_core library.
 *
 * @return Returns the version of the MATS_core library.
 */
MATS_LIB const char*
get_mats_version();


/**
 * Returns number of threads %MATS was built to use.
 */
MATS_LIB size_t
mats_num_threads();


/**
 * Overrides the number of threads to used. Value can only range from 1 to the
 * number of threads %MATS was build to use.
 *
 * Returns 0 on success.
 */
MATS_LIB int
mats_set_num_threads(size_t nt);


/**
 * Returns a string of %MATS compile flags (in particular, macro definitions).
 * These may be used when compiling packages for %MATS.
 */
MATS_LIB std::string mats_compile_flags();


/**
 * Sleep for the specified amount of time.
 *
 * @param[in] t_ms Time to sleep, in milliseconds.
 */
MATS_LIB void
sleep(size_t t_ms);


/**
 * Compare two numbers, which may be of different types.
 *
 * @param[in] a First number to compare.
 * @param[in] b Second number to compare.
 *
 * @return Returns true if @p a > @p b; false otherwise.
 */
template<class DT1, class DT2> MATS_LIB bool
greater(DT1 a, DT2 b);


/**
 * Compare two numbers, which may be of different types.
 *
 * @param[in] a First number to compare.
 * @param[in] b Second number to compare.
 *
 * @return Returns true if @p a < @p b; false otherwise.
 */
template<class DT1, class DT2> MATS_LIB bool
less(DT1 a, DT2 b);

}  // namespace mats

#endif  // SRC_MATS_PLATFORM_H_
