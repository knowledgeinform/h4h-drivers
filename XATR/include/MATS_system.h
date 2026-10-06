/**
 * @file
 * @brief File contains routines for getting system and process information.
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
#ifndef SRC_MATS_SYSTEM_H_
#define SRC_MATS_SYSTEM_H_

#include <vector>

#include "MATS_platform.h"


namespace mats {

/**
 * Structure describing system memory
 */
struct MATS_LIB MATS_system_memory {
  unsigned long long Total;  /**< Total physical memory available. */

  /**
   * Actual amount of available memory that can be given instantly to processes.
   */
  unsigned long long Available;

  /**
   * Percent usage calculated as (total - available) / total * 100.
   */
  float Percent;

  /**
   * Memory used, calculated differently depending on the platform and designed
   * for informational purposes only.
   */
  unsigned long long Used;

  /**
   * Memory not being used at all (zeroed) that is readily available; note that
   * this does not reflect the actual memory available (use 'available'
   * instead).
   */
  unsigned long long Free;
};


/**
 * Return statistics about system memory usage.
 */
MATS_LIB MATS_system_memory
virtual_memory();


/**
 * Return system swap memory statistics.
 */
MATS_LIB MATS_system_memory
swap_memory();


/**
 * Return the number of logical CPUs in the system.
 */
MATS_LIB int
cpu_count_logical();


/**
 * Returns a vector of the names for the variable fields of the CPU times, which
 * depends on the Linux kernel version.
 */
MATS_LIB std::vector<std::string>
get_cputimes_fields();


/**
 * Return system CPU times on the system per logical CPU.
 */
MATS_LIB std::vector<std::vector<float> >
per_cpu_times();


/**
 * Returns the process ID of the calling process.
 */
MATS_LIB int
get_pid();


/**
 * Gets process executable as an absolute path.
 *
 * @param[in] pid Process ID.
 * @param[out] name Process executable path.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
sys_pid_exe(int pid, std::string& name);

}  // namespace mats

#endif  // SRC_MATS_SYSTEM_H_
