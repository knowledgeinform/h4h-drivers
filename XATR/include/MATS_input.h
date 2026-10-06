/**
 * @file
 * @brief File contains the MATS_input classes used for holding sensor and
 * navigation data.
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
#ifndef SRC_MATS_INPUT_H_
#define SRC_MATS_INPUT_H_

#include <string>
#include <vector>
#include <map>

#include "MATS_data.h"

namespace mats {


class MATS_input;
class MATS_input_chunk;  // MATS_input_chunk is tightly coupled to MATS_input


/**
 * MATS_input_base is the abstract base class for image data, vehicle data, etc.
 *
 * Each MATS_input_base (whether a full MATS_input or a MATS_input_chunk)
 * may contain multiple datasets that cover the same along-track section and
 * originate from the same side of the vehicle.  For example, the input may
 * contain both HF (high-frequency) and BB (broad-band) data from the port side
 * of the vehicle.  The different datasets generally cover the same bottom
 * area, although some datasets may have a farther range than others.
 *
 * The cross-track axis of each dataset is assumed to originate at the vehicle
 * itself, with no offset for the water column.  The sweetspot member is used
 * to specify the cross-track region containing good data.
 */
class MATS_LIB MATS_input_base {
  friend class MATS_input;
 public:
  /**
   * Initialize empty MATS_input_base structure.
   */
  MATS_input_base();

  /**
   * MATS_input_base destructor
   */
  virtual ~MATS_input_base() {}

  /**
   * Returns true if the instance is a MATS_input_chunk; returns false if it is
   * a MATS_input.
   */
  virtual bool isChunk() const = 0;

  /**
   * Starting and end cross-track indices for suggested ATR processing.
   * These indices correspond to the cross-track axis of the reference
   * dataset.
   */
  size_t sweetspot[2];

  /**
   * Writes summary of this input to stdout.
   * This function only works if the MATS_DEBUG flag is set.
   */
  void display() const;

  /**
   * Returns the names of all the datasets in this input.
   */
  std::vector<std::string> dataNames() const;

  /**
   * Returns the name of the reference dataset.
   */
  const std::string& refName() const;

  /**
   * Returns a pointer to the specified dataset.
   *
   * @param[in] band Name of the dataset.
   */
  MATS_data* data(const char* band);

  /**
   * Returns a pointer to the specified dataset.
   *
   * @param[in] band Name of the dataset.
   */
  const MATS_data* data(const char* band) const;

  /**
   * Returns the length of the navigation data vector.
   */
  size_t navSize() const;

  /**
   * Returns filename of this input.
   */
  virtual const char* filename() const = 0;

  /**
   * Set the filename of this input.
   *
   * @param[in] filename Filename of the input.
   */
  virtual void setFilename(const char* filename) = 0;

  /**
   * Set the filename of this input.
   *
   * @param[in] filename Filename of the input.
   */
  virtual void setFilename(const std::string& filename) = 0;

  /**
   * Returns the name of sensor for collected data.
   */
  virtual const char* sensor() const = 0;

  /**
   * Set the name of the sensor.
   *
   * @param[in] sensor Name of sensor.
   */
  virtual void setSensor(const char* sensor) = 0;

  /**
   * Set the name of the sensor.
   *
   * @param[in] sensor Name of sensor.
   */
  virtual void setSensor(const std::string& sensor) = 0;

  /**
   * Returns the type of target detector is trying to detect.
   */
  virtual const char* targetType() const = 0;

  /**
   * Set the type of target detector is trying to detect.
   *
   * @param[in] targettype Target type.
   */
  virtual void setTargetType(const char* targettype) = 0;

  /**
   * Set the type of target detector is trying to detect.
   *
   * @param[in] targettype Target type.
   */
  virtual void setTargetType(const std::string& targettype) = 0;

  /**
   * Returns the side of vehicle corresponding to the data.
   */
  virtual const char* side() const = 0;

  /**
   * Set the side of vehicle corresponding to the data.
   *
   * @param[in] side Vehicle side string ("PORT"|"STBD")
   */
  virtual void setSide(const char* side) = 0;

  /**
   * Set the side of vehicle corresponding to the data.
   *
   * @param[in] side Vehicle side string ("PORT"|"STBD")
   */
  virtual void setSide(const std::string& side) = 0;

  /**
   * Returns the run-time mode:  "A" = ATR only; "P" = performance estimation
   * only; "B" = both.
   */
  virtual const char* mode() const = 0;

  /**
   * Set the run-time mode:  "A" = ATR only; "P" = performance estimation
   * only; "B" = both.
   *
   * @param[in] mode Run-time mode.
   */
  virtual void setMode(const char* mode) = 0;

  /**
   * Set the run-time mode:  "A" = ATR only; "P" = performance estimation
   * only; "B" = both.
   *
   * @param[in] mode Run-time mode.
   */
  virtual void setMode(const std::string& mode) = 0;

  /**
   * Returns the vehicle latitude array (degrees).
   * The indices correspond to the along-track axis of the reference dataset.
   */
  virtual double* getLat() = 0;

  /**
   * Returns the vehicle latitude array (degrees).
   * The indices correspond to the along-track axis of the reference dataset.
   */
  virtual const double* getLat() const = 0;

  /**
   * Returns the vehicle longitude array (degrees).
   * The indices correspond to the along-track axis of the reference dataset.
   */
  virtual double* getLon() = 0;

  /**
   * Returns the vehicle longitude array (degrees).
   * The indices correspond to the along-track axis of the reference dataset.
   */
  virtual const double* getLon() const = 0;

  /**
   * Returns the vehicle heading array (degrees).
   * The indices correspond to the along-track axis of the reference dataset.
   */
  virtual double* getHeading() = 0;

  /**
   * Returns the vehicle heading array (degrees).
   * The indices correspond to the along-track axis of the reference dataset.
   */
  virtual const double* getHeading() const = 0;

  /**
   * Returns the vehicle heading (degrees) at the given index.
   * The index corresponds to the along-track axis of the reference dataset.
   *
   * @param[in] ix Index.
   */
  virtual double heading(size_t ix) const = 0;

  /**
   * Returns the vehicle timestamp array (seconds).
   * The indices correspond to the along-track axis of the reference dataset.
   * Time is referenced to 00:00 hours, Jan 1, 1970 UTC.
   */
  virtual double* getTime() = 0;

  /**
   * Returns the vehicle timestamp array (seconds).
   * The indices correspond to the along-track axis of the reference dataset.
   * Time is referenced to 00:00 hours, Jan 1, 1970 UTC.
   */
  virtual const double* getTime() const = 0;

  /**
   * Returns the vehicle altitude array (meters).
   * The indices correspond to the along-track axis of the reference dataset.
   */
  virtual float* getHeight() = 0;

  /**
   * Returns the vehicle altitude array (meters).
   * The indices correspond to the along-track axis of the reference dataset.
   */
  virtual const float* getHeight() const = 0;

  /**
   * Returns the vehicle depth array (meters).
   * The indices correspond to the along-track axis of the reference dataset.
   */
  virtual float* getDepth() = 0;

  /**
   * Returns the vehicle depth array (meters).
   * The indices correspond to the along-track axis of the reference dataset.
   */
  virtual const float* getDepth() const = 0;

  /**
   * Returns added attributes associated with the input.
   *
   * @return const std::vector<std::string>& Vector of attribute names.
   */
  const std::vector<std::string>& attributes() const;

  /**
   * Returns the size of a recorded input attribute. Returns zero if attributes
   * does not exist.
   *
   * @param attr_name Name of attribute.
   * @return size_t Size of requested attribute.
   */
  size_t attrSize(const char* attr_name) const;

  /**
   * Add attribute associated with the input. Returns zero on success.
   *
   * @param attr_name Name of attribute.
   * @param n Length of attribute.
   * @param attrs Attribute array.
   */
  int addAttr(const char* attr_name, size_t n, const double *attrs);

  /**
   * Returns requested input attribute.
   *
   * @param attr_name Name of attribute.
   * @return std::vector<double> Attribute array.
   */
  std::vector<double> attr(const char* attr_name) const;

  /**
   * Returns requested input attribute.
   *
   * @param attr_name Name of attribute.
   * @return std::vector<double> Attribute array.
   */
  std::vector<double> attr(const std::string& attr_name) const;

 protected:
  size_t nav_len; /**< Length of navigation data. */

  /*
   * Sensor data
   */
  std::map<std::string, MATS_data> data_; /**< Sensor datasets, mapped by name. */
  std::string refName_; /**< Name of the reference dataset. */

  /*
   * Input attributes
   */
  std::vector<std::string> attr_name_; /**< Attribute names */
  std::vector<size_t> attr_size_; /**< Size of attributes */
  std::vector<double> attr_; /**< Attributes */
};


/**
 * MATS_input is an input containing the full along-track dataset.
 *
 * This is the input class that must be used when reading data from a file and
 * loading into an input.  Unlike MATS_input_chunk, MATS_input has methods for
 * adding sensor datasets and allocating navigation data.
 *
 * Each MATS_input
 * may contain multiple datasets that cover the same along-track section and
 * originate from the same side of the vehicle.  For example, the input may
 * contain both HF (high-frequency) and BB (broad-band) data from the port side
 * of the vehicle.  The different datasets generally cover the same bottom
 * area, although some datasets may have a farther range than others.
 *
 * The cross-track axis of each dataset is assumed to originate at the vehicle
 * itself, with no offset for the water column.  The sweetspot member is used
 * to specify the cross-track region containing good data.
 */
class MATS_LIB MATS_input : public MATS_input_base {
  friend class MATS_input_chunk;
  friend class MATS_reader;
 public:
  /**
   * Construct an empty MATS_input.
   */
  MATS_input();

  /**
   * MATS_input destructor.
   */
  ~MATS_input();

  /**
   * Construct a MATS_input copy of an existing MATS_input_base (may be either
   * a full input or a chunk).
   *
   * @param[in] indata MATS_input_base to be copied.
   */
  explicit MATS_input(const MATS_input_base& indata);

  /**
   * Assignment operator for MATS_input.
   *
   * @param[in] indata MATS_input value to assign.
   */
  MATS_input& operator=(const MATS_input& indata);

  /**
   * Clear all values.
   */
  void clear();

  /**
   * Add a dataset to the MATS_input.  The first dataset to be added will be
   * recorded as the reference dataset.
   *
   * @param[in] band Name of the dataset.
   */
  void addData(const char* band);

  bool isChunk() const {return false;}

  const char* filename() const;
  void setFilename(const char* filename);
  void setFilename(const std::string& filename);

  const char* sensor() const;
  void setSensor(const char* sensor);
  void setSensor(const std::string& sensor);

  const char* targetType() const;
  void setTargetType(const char* targettype);
  void setTargetType(const std::string& targettype);

  const char* side() const;
  void setSide(const char* side);
  void setSide(const std::string& side);

  const char* mode() const;
  void setMode(const char* mode);
  void setMode(const std::string& mode);

  /**
   * Allocate navigation data arrays. The arrays can only be allocated once.
   *
   * @param[in] num Array length to allocate (all navigation data arrays are
   * the same length).
   *
   * @return Returns 0 on success.
   *
   * @warning The array length should equal the along-track axis length of the
   * reference dataset.  Check this using checkInputNavLen().
   */
  int allocateNav(size_t num);

  double* getLat();
  const double* getLat() const;

  double* getLon();
  const double* getLon() const;

  double* getHeading();
  const double* getHeading() const;
  double heading(size_t ix) const;

  double* getTime();
  const double* getTime() const;

  float* getHeight();
  const float* getHeight() const;

  float* getDepth();
  const float* getDepth() const;

 private:
  std::string sensor_; /**< Sensor ID string */
  std::string fn_; /**< Filename of sensor data */
  std::string targettype_; /**< Type of target detector is trying to detect */
  std::string side_; /**< Side of vehicle corresponding to data */
  std::string mode_; /**< Run-time mode */

  /*
   * Navigation data
   *
   * @warning When the reader loads the nav data, it MUST make sure the nav
   * data points correspond with the along-track pings.  In other words,
   * nav_len must equal anum (for the reference band).  If these are not
   * equal, the reader must interpolate the nav data accordingly.
   */
  double* lat_; /**< vehicle latitude in degrees */
  double* lon_; /**< vehicle longitude in degrees */
  double* heading_; /**< vehicle heading in degrees */
  double* time_; /**< timestamp in seconds */
  float* height_; /**< vehicle altitude above bottom in meters */
  float* depth_; /**< vehicle depth in meters */

  void init(); /* Set all members to initial values. */
  void clearNav(); /* If nav data is allocated, free it. */
  /* Copy values from any MATS_input_base. */
  MATS_input& baseToInput(const MATS_input_base& indata);
};


/**
 * MATS_input_chunk is a portion of a MATS_input (a section of the full data,
 * divided in the along-track direction).
 *
 * Each MATS_input_chunk
 * may contain multiple datasets that cover the same along-track section and
 * originate from the same side of the vehicle.  For example, the input may
 * contain both HF (high-frequency) and BB (broad-band) data from the port side
 * of the vehicle.  The different datasets generally cover the same bottom
 * area, although some datasets may have a farther range than others.
 *
 * The cross-track axis of each dataset is assumed to originate at the vehicle
 * itself, with no offset for the water column.  The sweetspot member is used
 * to specify the cross-track region containing good data.
 */
class MATS_LIB MATS_input_chunk: public MATS_input_base {
  friend class MATS_input;
 public:
  /**
   * Construct a MATS_input_chunk from a portion of a MATS_input.
   *
   * @param[in] in Full MATS_input to be chunked.
   * @param[in] starts Along-track start index of chunk, with respect to the
   * reference dataset.
   * @param[in] ends Along-track end index of chunk, with respect to the
   * reference dataset.
   */
  MATS_input_chunk(MATS_input& in, size_t starts, size_t ends);

  /**
   * MATS_input_chunk destructor.
   */
  ~MATS_input_chunk();

  /**
   * Construct a copy of an existing MATS_input_chunk.
   *
   * @param[in] indata MATS_input_chunk to be copied.
   */
  MATS_input_chunk(const MATS_input_chunk& indata);

  /**
   * Assignment operator for MATS_input_chunk.
   *
   * @param[in] indata MATS_input_chunk value to assign.
   */
  MATS_input_chunk& operator=(const MATS_input_chunk& indata);

  /**
   * Copy the sensor data from the chunk back to the original MATS_input.
   */
  void apply();

  bool isChunk() const {return true;}

  const char* filename() const;
  void setFilename(const char* filename);
  void setFilename(const std::string& filename);

  const char* sensor() const;
  void setSensor(const char* sensor);
  void setSensor(const std::string& sensor);

  const char* targetType() const;
  void setTargetType(const char* targettype);
  void setTargetType(const std::string& targettype);

  const char* side() const;
  void setSide(const char* side);
  void setSide(const std::string& side);

  const char* mode() const;
  void setMode(const char* mode);
  void setMode(const std::string& mode);

  double* getLat();
  const double* getLat() const;

  double* getLon();
  const double* getLon() const;

  double* getHeading();
  const double* getHeading() const;
  double heading(size_t ix) const;

  double* getTime();
  const double* getTime() const;

  float* getHeight();
  const float* getHeight() const;

  float* getDepth();
  const float* getDepth() const;

 private:
  /**
   * Structure for recording along-track start and stop indices of a chunk
   * within the full input.
   */
  struct endPts {
    size_t start;
    size_t end;
  };

  MATS_input* input_ref; /**< pointer to the full MATS_input */
  std::map<std::string, endPts> endPts_; /**< endpoints of each chunk */
  size_t chunk_start; /**< along-track start index in reference dataset */
};


/**
 * Checks whether the navigation data length of the input matches the
 * along-track axis length of the reference dataset.
 *
 * @param[in] input Input to check.
 *
 * @return Returns true if the nav data and axis length match; false otherwise.
 */
MATS_LIB bool checkInputNavLen(const MATS_input& input);


/**
 * Saves a MATS_input in an HDF5 file, under the group name "input".
 *
 * @param[in] filename File to create.
 * @param[in] input MATS_input to save.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
mats_input_save(const char* filename, const MATS_input& input);


/**
 * Loads a MATS_input from an HDF5 file, from the group name "input".
 *
 * @param[in] filename File to read.
 * @param[out] input The loaded MATS_input.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
mats_input_load(const char* filename, MATS_input* input);

}  // namespace mats

#endif  // SRC_MATS_INPUT_H_
