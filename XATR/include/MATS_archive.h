/**
 * @file
 * @brief File contains the MATS data archiving structures and routines.
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
#ifndef SRC_MATS_ARCHIVE_H_
#define SRC_MATS_ARCHIVE_H_

#include "MATS_platform.h"
#include "MATS_input.h"
#include "MATS_contact.h"
#include "MATS_ecdata.h"
#include "MATS_groundtruth.h"
#include "MATS_struct.h"
#include "MATS_cfg.h"


namespace mats {

/**
 * MATS_archive is an interface for %MATS Archive files, which contain raw ATR
 * output from the processing of a file. Archive files do not contain any file
 * sensor data, but contain navigation, time, size, and resolution information.
 * They also contain ATR contact information (before threshold).
 */
class MATS_LIB MATS_archive {
 public:
  MATS_archive();

  /**
   * Loads an archive file.
   *
   * @param[in] filename Filename of archive file to load.
   *
   * @return Returns 0 on success.
   */
  int load(const char* filename);

  /**
   * Sets default search location for archives, which is used by load to allow
   * loading by id instead of file path.
   *
   * @param[in] loc Desired location for searching for archives.
   */
  void location(const char* loc);

  /**
   * Returns full file path to archive.
   */
  const char* path() const;

  /**
   * Returns side of archive.
   */
  const char* side() const;

  /**
   * Returns input data file checksum for archive.
   */
  const char* inputHash() const;

  /**
   * Returns config UUID of archive.
   */
  const char* config() const;

  /**
   * Returns version of archive (%MATS version when archive was created).
   */
  const char* version() const;

  /**
   * Returns contacts contained in archive.
   */
  MATS_contact_list contact() const;

  /**
   * Returns contact data for requested contact from archive.
   *
   */
  MATS_contact contact(const char *) const;

  /**
   * Returns extra contact data contained in archive.
   */
  MATS_ecdata_list ecdata() const;

  /**
   * Returns extra contact data for requested contact from archive.
   *
   */
  MATS_ecdata ecdata(const char *) const;

  /**
   * Returns groundtruth data contained in archive.
   */
  std::vector<MATS_groundtruth> groundtruth() const;

  /**
   * Adds contacts to archive. Contacts can only be added once.
   *
   * @param[in] con List of contacts to be added to archive.
   *
   * @return Returns 0 on success.
   */
  int add(const MATS_contact_list& con);

  /**
   * Updates contact information contained in an archive. This function will not
   * create new contacts in an archive. The updated contacts must have
   * matching UUIDs to the existing contacts.
   *
   * @note See h5_update_mats_contact() for which fields can be updated.
   *
   * @param[in] con List of contacts with updated information that needs to be
   * saved to the archive.
   *
   * @return Returns 0 on success.
   */
  int update(const MATS_contact_list& con);

  /**
   * Adds extra contact data to archive. Extra contact data can only be added
   * once.
   *
   * @param[in] ecd List of extra contact data to be added to archive.
   *
   * @return Returns 0 on success.
   */
  int add(const MATS_ecdata_list& ecd);

  /**
   * Updates ecdata information contained in an archive. This function will not
   * create new ecdata in an archive.
   *
   * @note Currently no ecdata fields are updatable.
   *
   * @param[in] ecd List of ecdata with updated information that needs to be
   * saved to the archive.
   *
   * @return Returns 0 on success.
   */
  int update(const MATS_ecdata_list& ecd);

  /**
   * Adds ground truth information to archive. Only ground truth for
   * corresponding archive input data is added to archive.
   *
   * @param[in] gt Ground truth vector.
   *
   * @return Returns 0 on success.
   */
  int add(const std::vector<MATS_groundtruth>& gt);

  /**
   * Updates groundtruth information contained in an archive.
   *
   * If existing groundtruth is empty, it is filled in with the given
   * groundtruth. If only num and type changes in
   * groundtruth are detected, then the information is updated. Otherwise, old
   * groundtruth is moved to new group 'gt#', where # is the next available
   * number starting with 0, and new groundtruth is added.
   *
   * @param[in] gt Groundtruth data with updates or groundtruth data to replace
   * existing.
   *
   * @return Returns 0 on success.
   */
  int update(const std::vector<MATS_groundtruth>& gt);

  /**
   * Adds or updates ATR processing time value in archive. Processing time is
   * for a single input.
   *
   * @param[in] ts ATR processing time (seconds).
   *
   * @return Returns 0 on success.
   */
  int addTiming(double ts);

  /**
   * Get ATR processing time value from archive. Processing time is for a
   * single input.
   *
   * @param[out] ts ATR processing time (seconds).
   *
   * @return Returns 0 on success.
   */
  int timing(double* ts) const;

  /**
   * Returns MATS_struct with archived input information. Archived
   * input information does not contain any sensor data, but contains
   * size and resolution information for sensor data.
   */
  MATS_struct input() const;

  /**
   * Writes summary information for loaded archive to stdout.
   * This function only works if the MATS_DEBUG flag is set.
   */
  void display() const;

 private:
  /**
   * Examine a groundtruth vector. Return only the groundtruths that match the
   * filename and side of the input.
   *
   * @param[in] filename Input filename.
   * @param[in] gt Input groundtruth vector.
   *
   * @return Returns the filtered groundtruth vector.
   */
  std::vector<MATS_groundtruth>
  gtFilter(const char* filename, const std::vector<MATS_groundtruth>& gt);

  std::string filename_;
  std::string location_;
  std::string side_;
  std::string config_;
  std::string hash_;
  std::string version_;
};


/**
 * An archive is a record of the ATR result for a particular input file and
 * configuration. An archiver is a manager of that information. The archiver
 * operates out of a designated file system location (by default this location
 * is the archive folder located in the %MATS working directory). Archives are
 * written to and loaded from this location by default. The archiver also
 * creates a text file at this location for associating a file SHA1 hash with
 * an archive.
 */
class MATS_LIB MATS_archiver {
 public:
  MATS_archiver();

  /**
   * Set advanced options for Archiver.
   *
   * @param[in] opt Options structure containing option and value pairs.
   *
   * @return Returns 0 on success.
   */
  int options(const MATS_struct &opt);

  /**
   * Sets the default location used by the archiver.
   *
   * @param[in] loc Filesystem directory for archives.
   *
   * @return Returns 0 on success.
   */
  int location(const char* loc);

  /**
   * Searches archives for an archive that corresponds to the given input and
   * configuration (and, optionally, version).
   *
   * @param[in] cfg Configuration used to process data.
   * @param[in] input Data processed.
   * @param[in] hash (Optional) SHA1 hash of input data file.
   * @param[in] version (Optional) %MATS version of archive.
   *
   * @return Returns the name of the first matching archive, if it exists.
   * Otherwise, returns an empty string.
   */
  std::string find(const ATR_Configuration& cfg, const MATS_input& input,
      const char* hash = NULL, const char* version = NULL);

  /**
   * Creates an archive for given configuration and input data.
   *
   * If an archive with the same input already exists, the groundtruth will be
   * pulled from the existing archive and added to the new one.
   *
   * If an archive with the same input, config, and version already exists,
   * it will be overwritten.
   *
   * If an archive with the same input and config, but older version, exists,
   * the behavior depends on the @p overwrite flag. If true, a matching archive
   * with older version will be overwritten with the new archive. If false, the
   * older archive will be left in place, and the new archive will be added.
   * This flag is optional and defaults to false.
   *
   * @param[in] cfg Configuration used to process data.
   * @param[in] input Data processed.
   * @param[in] overwrite (Optional) Flag to overwrite older matching archive.
   *
   * @return Returns the name of the new archive on success. Returns an empty
   * string on failure.
   */
  std::string create(const ATR_Configuration& cfg, const MATS_input& input,
      bool overwrite = false);

  /**
   * Imports an archive file (copies archive file to archiver location and adds
   * input/archive association to archive list).
   *
   * @param[in] filename Filename of archive to be imported.
   *
   * @return Returns 0 on success.
   */
  int importArchive(const char* filename);

  /**
   * Returns a list of archive IDs as recorded in the database file.
   */
  std::vector<std::string> arcList();

 private:
  /**
   * Add an entry (hash and UUID) to the database file.  (Only adds the entry if
   * it doesn't already exist.)
   *
   * @param[in] id UUID of the archive.
   * @param[in] hash SHA1 hash of the input data file.
   */
  void dbAdd(const std::string& id, const std::string& hash);

  /**
   * Find all entries in the database file with the given hash.
   *
   * @param[in] inHash SHA1 hash of the input data file.
   *
   * @return Returns a list of the entry UUIDs.
   */
  std::vector<std::string> dbFind(const std::string& inHash);

  /**
   * Given an input and its hash, try to find an existing groundtruth vector
   * for the input using existing archive files.
   *
   * @param[in] data Input data.
   * @param[in] hash SHA1 hash of input data file.
   *
   * @return Returns a groundtruth vector (empty if none found).
   */
  std::vector<MATS_groundtruth>
  gtFind(const MATS_input& data, const std::string& hash);

  std::string location_;
  std::string arcdb_;
  std::string filename_format_;
};

}  // namespace mats

#endif  // SRC_MATS_ARCHIVE_H_
