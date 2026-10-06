/**
 * @file
 * @brief File contains the MATS_ecdata structures used for MATS and MATS ATR
 * module communication.
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
#ifndef SRC_MATS_ECDATA_H_
#define SRC_MATS_ECDATA_H_

#include <vector>
#include <string>
#include <map>

#include "MATS_platform.h"
#include "MATS_input.h"


namespace mats {

class MATS_ecdata;

/**
 * A vector of MATS_ecdata structures.
 */
typedef std::vector<MATS_ecdata> MATS_ecdata_list;


/** Image sizes */
struct numSamps {
  size_t anum;  /**< Number of samples in the along-track direction */
  size_t cnum;  /**< Number of samples in the cross-track direction */
};


/**
 * Base Extra contact data container. Used internally to store MATS_ecdata
 * information. This class is not intended to be used outside of MATS_ecdata.
 */
class MATS_LIB MATS_ecdata_base {
 public:
  size_t id; /**< Contact ID */
  float detscore; /**< Detection score */

  /* Lat/long position */
  double lat; /**< Contact latitude position (deg) */
  double lon; /**< Contact longitude position (deg) */
  double heading; /**< Vehicle heading at contact position (deg). */
  double time; /**< Vehicle UTC timestamp at contact position. */
  float alt; /**< Vehicle altitude at contact position (m). */

  std::map<std::string, MATS_data> snippet; /**< Image snippets */
  std::string uuid; /**< Contact UUID string */
  std::string sensor; /**< sensor ID string */

  std::map<std::string, numSamps> origN; /**< Original (full) image sizes */

  /* Grouping info (from contact correlation) */
  size_t groupnum; /**< Contact group number */
  float groupconf; /**< Contact group confidence */
  double grouplat; /**< Contact group latitude */
  double grouplon; /**< Contact group longitude */
  float groupcovmat[4]; /**< Contact group covariance matrix 2x2 (float32) */

 private:
  friend class MATS_ecdata;
  unsigned count_;
  MATS_ecdata_base();  // Prevent users from directly using
};


/**
 * Extra contact data
 */
class MATS_LIB MATS_ecdata {
  friend MATS_LIB void
  mats_ecdata_swap(mats::MATS_ecdata& a, mats::MATS_ecdata& b);

 public:
  /**
   * Construct an empty MATS_ecdata.
   */
  MATS_ecdata();

  /**
   * Construct a copy of an existing MATS_ecdata.
   *
   * @param[in] ecd MATS_ecdata to be copied.
   */
  MATS_ecdata(const MATS_ecdata& ecd);

  /**
   * Returns contact ID.
   */
  size_t id() const;

  /**
   * Set contact ID.
   *
   * @param[in] id ID of contact.
   */
  void setID(size_t id);

  /**
   * Returns the UUID of the contact.
   */
  const char* uuid() const;

  /**
   * Set the UUID of the contact.
   *
   * @param[in] uuid UUID string.
   */
  void setUUID(const char* uuid);

  /**
   * Set the UUID of the contact.
   *
   * @param[in] uuid UUID string.
   */
  void setUUID(const std::string& uuid);

  /**
   * Returns the sensor that collected the contact information.
   */
  const char* sensor() const;

  /**
   * Set the sensor that collected the contact information.
   *
   * @param[in] sensor Sensor ID string.
   */
  void setSensor(const char* sensor);

  /**
   * Set the sensor that collected the contact information.
   *
   * @param[in] sensor Sensor ID string.
   */
  void setSensor(const std::string& sensor);

  /**
   * Returns the contact latitude in degrees.
   */
  double lat() const;

  /**
   * Set the contact latitude location.
   *
   * @param[in] lat Contact latitude in degrees.
   */
  void setLat(double lat);

  /**
   * Returns the contact longitude in degrees.
   */
  double lon() const;

  /**
   * Set the contact longitude location.
   *
   * @param[in] lon Contact longitude in degrees.
   */
  void setLon(double lon);

  /**
   * Returns the vehicle heading in degrees at the
   * time of contact observation.
   */
  double heading() const;

  /**
   * Set the vehicle heading at the time of contact observation.
   *
   * @param[in] heading Vehicle heading in degrees.
   */
  void setHeading(double heading);

  /**
   * Returns the vehicle time at contact observation.
   * Vehicle time is UTC in seconds referenced to the 1970 epoch.
   */
  double time() const;

  /**
   * Set the vehicle time at contact observation.
   *
   * @param[in] time Vehicle time in seconds referenced to the 1970 epoch,
   * UTC.
   */
  void setTime(double time);

  /**
   * Returns the vehicle altitude in meters at time
   * of contact observation.
   */
  float height() const;

  /**
   * Set the vehicle altitude at time of contact observation.
   *
   * @param[in] height Vehicle altitude in meters.
   */
  void setHeight(float height);

  /**
   * Returns the contact detector score (a value between 0 and 1).
   */
  float detscore() const;

  /**
   * Set the contact detector score.
   *
   * @param[in] detscore Contact detector score (between 0 and 1).
   */
  void setDetscore(float detscore);

  /**
   * Returns the contact group number.
   *
   * @remark Used for contact correlation.
   */
  size_t groupnum() const;

  /**
   * Set the contact group number.
   *
   * @param[in] num Contact group number (an integer 0 or higher).
   */
  void setGroupnum(size_t num);

  /**
   * Returns the contact group confidence, which is
   * the confidence that the contact belongs to its assigned group (a value
   * between 0 and 1).
   *
   * @remark Used for contact correlation.
   */
  float groupconf() const;

  /**
   * Set the contact group confidence, which is the confidence that the
   * contact belongs to its assigned group.
   *
   * @param[in] num Contact group confidence (between 0 and 1).
   */
  void setGroupconf(float num);

  /**
   * Returns the contact group latitude in degrees.
   *
   * @remark Used for contact correlation.
   */
  double grouplat() const;

  /**
   * Set the contact group latitude location.
   *
   * @param[in] lat Contact group latitude in degrees.
   */
  void setGrouplat(double lat);

  /**
   * Returns the contact group longitude in degrees.
   *
   * @remark Used for contact correlation.
   */
  double grouplon() const;

  /**
   * Set the contact group longitude location.
   *
   * @param[in] lon Contact group longitude in degrees.
   */
  void setGrouplon(double lon);

  /**
   * Returns the contact group lat/long covariance matrix.  This is a 2x2
   * matrix.
   *
   * @remark Used for contact correlation.
   */
  const float* groupcovmat() const;

  /**
   * Set the contact group lat/long covariance matrix.
   *
   * @param[in] cov Contact group lat/long covariance matrix (2x2).
   */
  void setGroupcovmat(const float* cov);

  /**
   * Returns the size of an original data structure from input.
   *
   * @param[in] band The dataset/frequency band of interest.
   * @param[out] anum Pointer to the along-track dimension size.
   * @param[out] cnum Pointer to the cross-track dimension size.
   */
  void getSize(const char* band, size_t* anum, size_t* cnum) const;

  /**
   * Set the size of an original data structure from input.
   *
   * @param[in] band The dataset/frequency band of interest.
   * @param[in] anum Along-track dimension size.
   * @param[in] cnum Cross-track dimension size.
   */
  void setSize(const char* band, size_t anum, size_t cnum);

  /**
   * Writes summary of MATS_ecdata to stdout.
   * This function only works if the MATS_DEBUG flag is set.
   */
  void display() const;

  /**
   * Returns the names of the snippet datasets/frequency bands.
   */
  std::vector<std::string> snippetNames() const;

  /**
   * Returns a pointer to a snippet.  If a snippet from the requested band does
   * not exist, returns a null pointer.
   *
   * @param[in] band The dataset/frequency band of interest.
   */
  MATS_data* snippet(const char* band);

  /**
   * Returns a pointer to a snippet.  If a snippet from the requested band does
   * not exist, returns a null pointer.
   *
   * @param[in] band The dataset/frequency band of interest.
   */
  const MATS_data* snippet(const char* band) const;

  /**
   * Set or replace a snippet for a particular dataset.
   *
   * @param[in] band The dataset/frequency band of interest.
   * @param[in] snippet The snippet.
   */
  void setSnippet(const char* band, const MATS_data& snippet);

  /**
   * Use a MATS_input to load appropriate member data such as the original
   * data sizes and the sensor name.
   *
   * @param[in] input The MATS_input that the contact originated from.
   *
   * @return Returns 0 on success.
   */
  int loadInput(const MATS_input& input);

  /**
   * MATS_ecdata destructor
   */
  ~MATS_ecdata();

  /**
   * Copy an existing MATS_ecdata.
   *
   * @param[in] ecd MATS_ecdata to be copied.
   */
  void copy(const MATS_ecdata& ecd);

  /**
   * Assignment operator for MATS_ecdata.
   *
   * @param[in] ecd MATS_ecdata value to assign.
   */
  MATS_ecdata& operator=(const MATS_ecdata& ecd);

 private:
  MATS_ecdata_base* p_;
};


/**
 * Shallow copy of MATS Ecdata (uses assignment operator). This method is used
 * to support other language integration.
 *
 * @param[in] from MATS_ecdata to be copied.
 * @param[in] to Pointer to MATS_ecdata to be copied to.
 */
MATS_LIB void
mats_ecdata_shallow_copy(const MATS_ecdata &from, MATS_ecdata *to);


/**
 * Move @p source MATS_ecdata vector to the end of @p dest MATS_ecdata vector.
 *
 * @param[in,out] dest Destination MATS_ecdata vector.
 * @param[in,out] source Source MATS_ecdata vector (will be cleared upon
 * successful completion).
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
mats_ecdata_list_append(MATS_ecdata_list& dest, MATS_ecdata_list& source);


/**
 * Saves a MATS_ecdata_list in an HDF5 file under the group name "ecdata".
 *
 * @param[in] filename File to write ecdata list to.
 * @param[in] ecdata List of ecdata.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
mats_ecdata_save(const char* filename, const MATS_ecdata_list& ecdata);


/**
 * Loads ecdata from an HDF5 file, from the group name "ecdata".  A subset
 * of the contacts may be selected for loading.
 *
 * @param[in] filename File to read ecdata list from.
 * @param[in] indexVec Indices of the contacts to be loaded.  If empty, all
 * contacts will be loaded.
 * @param[out] ecdata List of ecdata.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
mats_ecdata_load(const char* filename, const std::vector<size_t>& indexVec,
    MATS_ecdata_list* ecdata);


/**
 * Exchange the values of two MATS_ecdata objects.
 */
MATS_LIB void
mats_ecdata_swap(mats::MATS_ecdata& a, mats::MATS_ecdata& b);

}  // namespace mats

#endif  // SRC_MATS_ECDATA_H_
