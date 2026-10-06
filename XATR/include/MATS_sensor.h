/**
 * @file
 * @brief File contains the MATS_sensor class for configuring sensors, and
 * the MATS sensor manager.
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
#ifndef SRC_MATS_SENSOR_H_
#define SRC_MATS_SENSOR_H_

#include <string>
#include <vector>
#include <map>

#include "MATS_platform.h"
#include "MATS_data.h"
#include "MATS_input.h"
#include "MATS_contact.h"
#include "MATS_ecdata.h"


namespace mats {

class MATS_sensor;


/**
 * Sensor description
 */
struct MATS_data_description {
  std::string type; /**< Type of sensor (SONAR|RADAR|MAG) */
  std::string direction; /**< Direction of sensor (SIDELOOK|FORWARD|BOTTOM)*/
  MATS_precision precision; /**< Expected data precision */
  std::string processing; /**< ATR processing type (BLOCK|STREAM) */
  std::vector<double> res; /**< Expected resolution of each dimension */
};


/**
 * This function type is used when creating a MATS_sensor.  The function for
 * filling in the sweetspot of a MATS_input should have this type.
 */
typedef int (*func_sweetspot)(mats::MATS_input_base&, const mats::MATS_sensor*);


/**
 * Default sweetspot calculation function. Uses entire data.
 *
 * @param[in,out] input An input to have its sweetspot field set.
 *
 * @return Returns 0 on success.
 */
int
default_sweetspot(mats::MATS_input_base& input, const mats::MATS_sensor*);


/**
 * This function type is used when creating a MATS_sensor.  The function for
 * recentering a contact should have this type.
 */
typedef void (*func_recenter)(const mats::MATS_input&, size_t&, size_t&,
    const mats::MATS_sensor*);


/**
 * Default contact recentering function. Leaves x and y unchanged.
 *
 * @param[in] input The input corresponding to the (x,y) coordinates.
 * @param[in,out] x Contact cross-track index.
 * @param[in,out] y Contact along-track index.
 */
void
default_recenter(const mats::MATS_input& input, size_t& x, size_t& y,
    const mats::MATS_sensor*);


/**
 * This function type is used when creating a MATS_sensor.  The function for
 * generating contact snippets should have this type.
 */
typedef int (*func_snipgen)(const mats::MATS_input_base& input,
    const mats::MATS_contact& con, mats::MATS_ecdata& ecd,
    const mats::MATS_sensor*);


/**
 * Default snippet generating function.
 *
 * Based on the (x,y) position of a contact, add a snippet to ecdata for each
 * band.  The (x,y) position applies to the reference band of input.
 *
 * For snippet size, the function will use the snippet size from the
 * existing sensor module, if found.  Otherwise, it will use the default
 * snippet size of 31 X 331.
 *
 * @param[in] input Input structure associated with contacts.
 * @param[in] con Contact structure containing (x,y) position.
 * @param[in,out] ecd Ecdata structure, updated with snippet(s).
 *
 * @return Returns 0 on success.
 */
int
default_snipgen(const mats::MATS_input_base& input,
    const mats::MATS_contact& con, mats::MATS_ecdata& ecd,
    const mats::MATS_sensor*);


/**
 * MATS_sensor describes the information that a sensor should provide (e.g.,
 * data band names) and defines ATR sensor specific settings (e.g., snippet
 * size).
 */
class MATS_LIB MATS_sensor {
 public:
  MATS_sensor();

  /**
   * Returns name of sensor.
   */
  const char* name() const;

  /**
   * Returns version string of sensor.
   */
  const char* version() const;

  /**
   * Returns description of sensor.
   */
  const char* description() const;

  /**
   * Returns true if sensor has navigation data.
   */
  bool hasNav() const;

  /**
   * Returns the name of the reference dataset.
   */
  const std::string& refName() const;

  /**
   * Returns the names of data for the sensor.
   */
  std::vector<std::string> dataNames() const;

  /**
   * Returns data description for requested sensor data.
   *
   * @param[in] name Name of sensor data.
   *
   * @return Returns pointer to data description if found. If not found,
   * returns a null pointer.
   */
  const mats::MATS_data_description* data(const char* name) const;

  /**
   * Returns sensor's requested snippet size in dimensions (along-track pixels,
   * cross-track pixels). Snippet size applies to the reference band.
   */
  std::vector<size_t> snippetSize() const;

  /**
   * Returns acceptable distance a contact is allowed to be from a groundtruth
   * location and still be associated with the groundtruth location (meters).
   * This value is used by groundtruthing functions that associate a
   * groundtruth with contacts.
   */
  double gtDistThresh() const;

  /**
   * Finds ideal sensor data region for ATR processing and sets the input
   * sweetspot field accordingly.
   *
   * @param[in,out] input An input or chunk to have its sweetspot field set.
   *
   * @return Returns 0 on success.
   */
  int sweetspot(mats::MATS_input_base& input) const;

  /**
   * Recenters contact according to sensor parameters.
   *
   * @param[in] input Full input.
   * @param[in,out] x Contact cross-track index.
   * @param[in,out] y Contact along-track index.
   */
  void roi_recenter(const mats::MATS_input& input, size_t& x, size_t& y) const;

  /**
   * Finds ideal sensor data region for ATR processing and sets the input
   * sweetspot field accordingly.
   *
   * @param[in,out] input An input or chunk to have its sweetspot field set.
   *
   * @return Returns 0 on success.
   */
  int snippetGenerator(const mats::MATS_input_base& input,
    const mats::MATS_contact& con, mats::MATS_ecdata& ecd) const;

  /**
   * Compares sensor name to string.
   *
   * @param[in] name String to be compared to sensor name.
   *
   * @return Returns 0 if the names match.
   */
  int compare(const char* name) const;

  /**
   * Assignment operator for MATS_sensor.
   *
   * @param[in] insensor Sensor to be copied.
   */
  MATS_sensor& operator=(const MATS_sensor& insensor);

 protected:
  /**
   * Sets name of sensor.
   *
   * Use this method in the constructor of the derived class.
   *
   * @param[in] nm Sensor name.
   *
   * @return Returns 0 on success.
   */
  int setName(const char* nm);

  /**
   * Sets version string of sensor.
   *
   * Use this method in the constructor of the derived class.
   *
   * @param[in] ver Version string.
   *
   * @return Returns 0 on success.
   */
  int setVersion(const char* ver);

  /**
   * Sets description of sensor.
   *
   * Use this method in the constructor of the derived class.
   *
   * @param[in] desc Description of sensor.
   *
   * @return Returns 0 on success.
   */
  int setDescription(const char* desc);

  /**
   * Sets hasNav value for sensor.
   *
   * Use this method in the constructor of the derived class.
   *
   * @param[in] hasNav Whether to expect navigation data for this sensor.
   *
   * @return Returns 0 on success.
   */
  int setHasNav(bool hasNav);

  /**
   * Adds a description of data for sensor.
   *
   * Use this method in the constructor of the derived class.
   *
   * @param[in] nm Name of data for sensor.
   * @param[in] desc Data description.
   *
   * @return Returns 0 on success.
   */
  int addData(const char* nm, const MATS_data_description& desc);

  /**
   * Sets sensor's snippet size in dimensions (along-track pixels,
   * cross-track pixels). Snippet size applies to the reference band.
   *
   * Use this method in the constructor of the derived class.
   *
   * @param[in] sz Size vector for sensor snippets.
   *
   * @return Returns 0 on success.
   */
  int setSnippetSize(const std::vector<size_t>& sz);

  /**
   * Sets acceptable distance a contact is allowed to be from a groundtruth
   * location and still be associated with the groundtruth location (meters).
   *
   * Use this method in the constructor of the derived class.
   *
   * @param[in] dist Acceptable groundtruth distance in meters.
   *
   * @return Returns 0 on success.
   */
  int setGtDistThresh(double dist);

  /**
   * Adds sweetspot function to be used for sensor.
   *
   * Use this method in the constructor of the derived class.
   *
   * @param[in] sw Function pointer for sweetspot function.
   *
   * @return Returns 0 on success.
   */
  int addSweetspot(func_sweetspot sw);

  /**
   * Adds recentering function to be used for sensor.
   *
   * Use this method in the constructor of the derived class.
   *
   * @param[in] rc Function pointer for recentering function.
   *
   * @return Returns 0 on success.
   */
  int addRecenter(func_recenter rc);

  /**
   * Adds snippet generator function to be used for sensor.
   *
   * Use this method in the constructor of the derived class.
   *
   * @param[in] sg Function pointer for snippet generator function.
   *
   * @return Returns 0 on success.
   */
  int addSnippetGenerator(func_snipgen sg);

 private:
  std::string name_;
  std::string refName_;
  std::string version_;
  std::string description_;
  std::map<std::string, MATS_data_description> data_;
  std::vector<size_t> snippetSize_;
  double gt_dist_thresh_;
  func_sweetspot sweetspot_;
  func_recenter recenter_;
  func_snipgen snippetgenerator_;
  bool has_nav_;
};


/**
 * Returns a list of known sensors.
 *
 * @return Returns a vector of known sensor string names.
 * @warning To find available sensors, a MATS_C or MATS object must be created
 * first, which will scan for sensor modules.
 */
MATS_LIB std::vector<std::string>
mats_known_sensors();


/**
 * Returns information for requested sensor.
 *
 * @param[in] name Name of sensor.
 *
 * @return Returns a pointer to the requested MATS_sensor if found. If not
 * found, returns a null pointer.
 *
 * @warning To find available sensors, a MATS_C or MATS object must be created
 * first, which will scan for sensor modules.
 */
MATS_LIB const mats::MATS_sensor*
mats_sensor(const char* name);


/**
 * Retrieves information about requested sensor and writes it to given
 * MATS_sensor. Function does nothing if it is unable to find sensor
 * (i.e., sensor is left unmodified).
 *
 * @param[in] name Name of sensor.
 * @param[out] sensor Retrieved sensor information.
 *
 * @return Returns 0 on success.
 *
 * @warning To find available sensors, a MATS_C or MATS object must be created
 * first, which will scan for sensor modules.
 */
MATS_LIB int
mats_sensor(const char* name, MATS_sensor& sensor);


/**
 * Adds new sensor information to known sensors.
 *
 * @param[in] sensor New sensor information.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
mats_sensor_add(const mats::MATS_sensor& sensor);


/**
 * Displays summary of MATS_sensor content to stdout.
 * This function only works if the MATS_DEBUG flag is set.
 *
 * @param[in] sensor Sensor information.
 *
 * @warning To find available sensors, a MATS_C or MATS object must be created
 * first, which will scan for sensor modules.
 */
MATS_LIB void
mats_sensor_display(const mats::MATS_sensor& sensor);


/**
 * MATS_sensor_manager serves as a collector of sensor modules that can be
 * queried for information about a sensor.
 */
class MATS_LIB MATS_sensor_manager {
 public:
  MATS_sensor_manager();

  /**
   * Returns a list of the names of known sensors.
   */
  std::vector<std::string>
  sensors() const;

  /**
   * Returns information for requested sensor.
   *
   * @param[in] name Name of sensor.
   *
   * @return Returns a pointer to the requested MATS_sensor if found. If not
   * found, returns a null pointer.
   */
  const MATS_sensor*
  sensor(const char* name) const;

  /**
   * Adds new sensor information.
   *
   * @param[in] sensor New sensor information.
   *
   * @return Returns 0 on success.
   */
  int
  addSensor(const mats::MATS_sensor& sensor);

 private:
  std::vector<mats::MATS_sensor> sensors_;
};

}  // namespace mats

#endif  // SRC_MATS_SENSOR_H_
