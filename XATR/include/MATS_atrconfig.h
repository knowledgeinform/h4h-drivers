/**
 * @file
 * @brief File contains the MATS_atrconfig class used for saving and loading
 * a processing stream configuration.
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
#ifndef SRC_MATS_ATRCONFIG_H_
#define SRC_MATS_ATRCONFIG_H_

#include <string>
#include <vector>
#include <map>

#include "MATS_platform.h"
#include "MATS_struct.h"
#include "MATS_cfg.h"


namespace mats {


/**
 * This structure is used by the MATS_C class for loading modules using their
 * appropriate interfaces.  This structure is obtained using a MATS_atrconfig
 * class.
 */
struct MATS_LIB MATS_module_description {
  std::string name;  /**< the module name */
  /**
   * the MATS_interface derived class needed to load the module, e.g.,
   * "MATS_C", "MATS_MCR", or "MATS_Python"
   */
  std::string interfaceName;
  std::string version;  /**< the module version */
};


/**
 * %MATS ATR Configuration
 *
 * This class handles an atrconfig file and processing stream configuration.
 * A related class is MATS_cfg, which handles sensor config files.
 */
class MATS_LIB MATS_atrconfig {
 public:
  /**
   * Construct a MATS_atrconfig using the default config directory.
   */
  MATS_atrconfig();

  /**
   * Construct a MATS_atrconfig, specifying which path to search for
   * atrconfig files.
   *
   * @param[in] cfgDir The config directory path.
   */
  MATS_atrconfig(const std::string& cfgDir);

  /**
   * Returns the %MATS version string.
   */
  const char* version() const;

  /**
   * Set the %MATS version string.
   *
   * @param[in] ver %MATS version string.
   */
  void setVersion(const char* ver);

  /**
   * Set the %MATS version string.
   *
   * @param[in] ver %MATS version string.
   */
  void setVersion(const std::string& ver);

  /**
   * Returns the note (general description).
   */
  const char* note() const;

  /**
   * Set the note.
   *
   * @param[in] note Note or general description.
   */
  void setNote(const char* note);

  /**
   * Set the note.
   *
   * @param[in] note Note or general description.
   */
  void setNote(const std::string& note);

  /**
   * Returns the creation date/time of the configuration.
   * Time is in seconds, UTC referenced to the 1970 epoch.
   */
  double time() const;

  /**
   * Set the creation date/time of the configuration.
   *
   * @param[in] time Time in seconds, UTC referenced to the 1970 epoch.
   */
  void setTime(double time);

  /**
   * Returns the sensor name associated with the configuration.
   */
  const char* sensor() const;

  /**
   * Set the sensor name associated with the configuration.
   *
   * @param[in] sensor Name of the sensor.
   */
  void setSensor(const char* sensor);

  /**
   * Set the sensor name associated with the configuration.
   *
   * @param[in] sensor Name of the sensor.
   */
  void setSensor(const std::string& sensor);

  /**
   * Returns the interface name for the processing stream.
   */
  const char* stream() const;

  /**
   * Set the interface name for the processing stream.
   *
   * @param[in] stream Interface name, e.g., "MATS_C" or "MATS_MCR".
   * @param[in] streamver Interface module version.
   */
  void setStream(const char* stream, const char* streamver);

  /**
   * Set the interface name for the processing stream.
   *
   * @param[in] stream Interface name, e.g., "MATS_C" or "MATS_MCR".
   * @param[in] streamver Interface module version.
   */
  void setStream(const std::string& stream, const std::string& streamver);

  /**
   * Returns the name of the detector module.
   */
  const char* detector() const;

  /**
   * Set the name, interface, and configuration of the detector module.  If
   * there is an existing detector feature normalization vector, this method
   * will remove it and reset the detector feature length to 0.
   *
   * @param[in] det Detector module name.
   * @param[in] detlang Detector module interface, e.g., "MATS_C" or
   * "MATS_MCR".
   * @param[in] detver Detector module version.
   * @param[in] cfg (Optional) Configuration for the detector.
   */
  void setDetector(const char* det, const char* detlang, const char* detver,
      const mats::MATS_struct& cfg = mats::MATS_struct());

  /**
   * Set the name, interface, and configuration of the detector module.  If
   * there is an existing detector feature normalization vector, this method
   * will remove it and reset the detector feature length to 0.
   *
   * @param[in] det Detector module name.
   * @param[in] detlang Detector module interface, e.g., "MATS_C" or
   * "MATS_MCR".
   * @param[in] detver Detector module version.
   * @param[in] cfg (Optional) Configuration for the detector.
   */
  void setDetector(const std::string& det, const std::string& detlang,
      const std::string& detver,
      const mats::MATS_struct& cfg = mats::MATS_struct());

  /**
   * Returns the length of the detector module's feature vector.
   * (Not all detectors produce features, in which case this is 0.)
   */
  size_t detFeatLen() const;

  /**
   * If the detector module produces features, set the detector module's
   * feature normalization vector.
   *
   * If the length of the detector module's feature vector is len, then the
   * length of this normalization vector should be 2*len.  There are two
   * entries for each feature:  norm[2*n] is the mean of the feature, and
   * norm[2*n+1] is the standard deviation of the feature, where n is the
   * feature index.  For no normalization, set norm[2*n] = 0 and
   * norm[2*n+1] = 1.
   *
   * @param[in] norm Feature normalization vector.
   *
   * @return Returns 0 on success.
   */
  int setDetFeatNorm(const std::vector<double>& norm);

  /**
   * Returns the name of the classifier module.
   */
  const char* classifier() const;

  /**
   * Set the name, interface, and configuration of the classifier module.
   *
   * @param[in] cls Classifier module name.
   * @param[in] clslang Classifier module interface, e.g., "MATS_C" or
   * "MATS_MCR".
   * @param[in] clsver Classifier module version.
   * @param[in] cfg (Optional) Configuration for the classifier.
   */
  void setClassifier(const char* cls, const char* clslang, const char* clsver,
      const mats::MATS_struct& cfg = mats::MATS_struct());

  /**
   * Set the name, interface, and configuration of the classifier module.
   *
   * @param[in] cls Classifier module name.
   * @param[in] clslang Classifier module interface, e.g., "MATS_C" or
   * "MATS_MCR".
   * @param[in] clsver Classifier module version.
   * @param[in] cfg (Optional) Configuration for the classifier.
   */
  void setClassifier(const std::string& cls, const std::string& clslang,
      const std::string& clsver,
      const mats::MATS_struct& cfg = mats::MATS_struct());

  /**
   * Returns the name of the normalizer module.
   */
  const char* normalizer() const;

  /**
   * Set the name, interface, and configuration of the normalizer module.
   *
   * @param[in] norm Normalizer module name.
   * @param[in] normlang Normalizer module interface, e.g., "MATS_C" or
   * "MATS_MCR".
   * @param[in] normver Normalizer module version.
   * @param[in] cfg (Optional) Configuration for the normalizer.
   */
  void setNormalizer(const char* norm, const char* normlang,
      const char* normver, const mats::MATS_struct& cfg = mats::MATS_struct());

  /**
   * Set the name, interface, and configuration of the normalizer module.
   *
   * @param[in] norm Normalizer module name.
   * @param[in] normlang Normalizer module interface, e.g., "MATS_C" or
   * "MATS_MCR".
   * @param[in] normver Normalizer module version.
   * @param[in] cfg (Optional) Configuration for the normalizer.
   */
  void setNormalizer(const std::string& norm, const std::string& normlang,
      const std::string& normver,
      const mats::MATS_struct& cfg = mats::MATS_struct());

  /**
   * Returns the name of the segmenter module.
   */
  const char* segmenter() const;

  /**
   * Set the name, interface, and configuration of the segmenter module.
   *
   * @param[in] seg Segmenter module name.
   * @param[in] seglang Segmenter module interface, e.g., "MATS_C" or
   * "MATS_MCR".
   * @param[in] segver Segmenter module version.
   * @param[in] cfg (Optional) Configuration for the segmenter.
   */
  void setSegmenter(
      const char* seg,
      const char* seglang,
      const char* segver,
      const mats::MATS_struct& cfg = mats::MATS_struct());

  /**
   * Set the name, interface, and configuration of the segmenter module.
   *
   * @param[in] seg Segmenter module name.
   * @param[in] seglang Segmenter module interface, e.g., "MATS_C" or
   * "MATS_MCR".
   * @param[in] segver Segmenter module version.
   * @param[in] cfg (Optional) Configuration for the segmenter.
   */
  void setSegmenter(
      const std::string& seg,
      const std::string& seglang,
      const std::string& segver,
      const mats::MATS_struct& cfg = mats::MATS_struct());

  /**
   * Returns the name of a feature module.
   *
   * @param[in] ix Index of the feature module (0-based).
   *
   * @return Returns the name of the feature at the given index. If the index
   * is out of bounds, returns NULL.
   */
  const char* feature(size_t ix) const;

  /**
   * Add a feature module to the configuration.
   *
   * @param[in] name Feature module name.
   * @param[in] lang Feature module interface, e.g., "MATS_C" or "MATS_MCR".
   * @param[in] ver Feature module version.
   * @param[in] norm Normalization parameters for the feature module.  If the
   * length of the feature vector is len, then the length of this norm vector
   * should be 2*len.  There are two entries for each feature in the module:
   * norm[2*n] is the mean of the feature, and norm[2*n+1] is the standard
   * deviation of the feature, where n is the feature index.  For no
   * normalization, set norm[2*n] = 0 and norm[2*n+1] = 1.
   * @param[in] cfg Feature module configuration.
   *
   * @return Returns 0 on success.
   */
  int addFeature(const char* name, const char* lang, const char* ver,
      const std::vector<double>& norm, const mats::MATS_struct& cfg);

  /**
   * Returns the normalization parameters of all feature modules, including
   * any features from the detector.  There are
   * two entries for each feature:  the mean of the feature, and the
   * standard deviation of the feature.  The array contains these parameters
   * in this order:  mean of feature 0, std dev of feature 0, mean of feature 1,
   * std dev of feature 1, ...  Note that each feature module may contain
   * multiple features.
   */
  const double* featNorm() const;

  /**
   * Returns the length of a feature module's feature vector.
   *
   * @param[in] ix Index of the feature module (0-based).
   *
   * @return Returns the length of the feature vector at the given index.
   * If the index is out of bounds, returns 0.
   */
  size_t featLen(size_t ix) const;

  /**
   * Gets the configuration of a feature module.
   *
   * @param[in] ix Index of the feature module (0-based).
   *
   * @return Returns a pointer to the feature configuration at the given index.
   * If the index is out of bounds, returns NULL.
   */
  const MATS_struct* featCfg(size_t ix) const;

  /**
   * Returns the description of the interface (stream) module.
   */
  MATS_module_description streamModule() const;

  /**
   * Returns the description (name and interface name) of the normalizer
   * module.
   */
  MATS_module_description normModule() const;

  /**
   * Returns the description (name and interface name) of the segmenter
   * module.
   */
  MATS_module_description segModule() const;

  /**
   * Returns the description (name and interface name) of the detector
   * module.
   */
  MATS_module_description detModule() const;

  /**
   * Returns the descriptions (names and interface names) of the feature
   * modules.
   */
  std::vector<MATS_module_description> featModules() const;

  /**
   * Returns the description (name and interface name) of the classifier
   * module.
   */
  MATS_module_description clsModule() const;

  /**
   * Returns a constant reference to the configuration of the classifier
   * module.
   */
  const MATS_struct& clsCfg() const;

  /**
   * Returns a constant reference to the configuration of the detector
   * module.
   */
  const MATS_struct& detCfg() const;

  /**
   * Returns a constant reference to the configuration of the normalizer
   * module.
   */
  const MATS_struct& normCfg() const;

  /**
   * Returns a constant reference to the configuration of the segmenter
   * module.
   */
  const MATS_struct& segCfg() const;

  /**
   * Returns contact loading information for a configuration. (This
   * information is usually used for training.)
   */
  MATS_struct clinfo() const;

  /**
   * Set contact loading information for the configuration.
   *
   * @parm[in] clinfo Contact loading information for configuration.
   *
   * @return Returns 0 on success.
   */
  int setClinfo(const mats::MATS_struct &clinfo);

  /**
   * Loads an atrconfig file and does some consistency checks.
   *
   * @param[in] filename This may be either the full path and filename of an
   * atrconfig file, or just the UUID (without a file extension).  If just a
   * UUID is supplied, the config directory will be searched for the atrconfig
   * file by that name.
   *
   * @return Returns 0 on success.
   */
  int load(const std::string& filename);

  /**
   * The atrconfig is saved using whatever filename has already been set.
   *
   * @return Returns 0 on success.
   */
  int save();

  /**
   * Displays the contents of the configuration.
   */
  void display() const;

  /**
   * Checks whether the MATS_atrconfig is complete (contains all the necessary
   * information for configuring the processing stream).
   *
   * Some fields will be filled automatically if they are empty.  In this case,
   * the method will still return 0, but will issue a warning.
   *
   * @param[out] featLen (Optional) Pointer to the total feature vector length,
   * including any detector features.
   *
   * @return Returns 0 on success.
   */
  int check(size_t* featLen = NULL);

  /**
   * Finds the total feature vector length, including any detector features.
   *
   * @return Returns the total feature vector length.
   *
   * @warning This method does not check the atrconfig for consistency. The
   * return value may not correspond to the feature normalization vector size.
   */
  size_t totalFeatLen();

  /**
   * Returns the config directory used for loading atrconfig files.
   */
  const char* configDirectory() const;

  /**
   * Set the config directory used for loading atrconfig files.
   *
   * @param[in] cfgDir Config directory path.
   */
  void setConfigDirectory(const char* cfgDir);

  /**
   * Set the config directory used for loading atrconfig files.
   *
   * @param[in] cfgDir Config directory path.
   */
  void setConfigDirectory(const std::string& cfgDir);

  /**
   * Returns the current filename being used (full path).
   */
  const char* filename() const;

  /**
   * Set the filename to use.
   *
   * @param[in] filename Filename (either full path or basename only).
   */
  void setFilename(const char* filename);

  /**
   * Set the filename to use.
   *
   * @param[in] filename Filename (either full path or basename only).
   */
  void setFilename(const std::string& filename);

  /**
   * MATS_atrconfig destructor.
   */
  ~MATS_atrconfig();

 private:
  /**
   * Clears the configuration.
   */
  void clear();

  std::string cfgDir_;
  std::string fn_;

  std::string ver_;
  std::string note_;
  double time_;
  std::string sensor_;

  std::string stream_;
  std::string streamver_;

  std::string det_;
  std::string detlang_;
  std::string detver_;
  MATS_struct detcfg_;
  size_t detlen_;

  std::string cls_;
  std::string clslang_;
  std::string clsver_;
  MATS_struct clscfg_;

  std::string normalizer_;
  std::string normlang_;
  std::string normver_;
  MATS_struct normcfg_;

  std::string segmenter_;
  std::string seglang_;
  std::string segver_;
  MATS_struct segcfg_;

  std::vector<std::string> feat_;
  std::vector<std::string> featlang_;
  std::vector<std::string> featver_;
  std::vector<MATS_struct> featcfg_;
  std::vector<size_t> featlen_;
  std::vector<double> featnorm_;
};


/**
 * %MATS ATR Configuration - dconfig
 *
 * This class handles a dconfig file and detector configuration.
 */
class MATS_LIB MATS_dconfig {
 public:
  /**
   * Construct a MATS_dconfig using the default config directory.
   */
  MATS_dconfig();

  /**
   * Construct a MATS_dconfig, specifying which path to search for
   * dconfig files.
   *
   * @param[in] cfgDir The config directory path.
   */
  MATS_dconfig(const char* cfgDir);

  /**
   * MATS_dconfig destructor.
   */
  ~MATS_dconfig();

  /**
   * Returns the %MATS version string.
   */
  const char* version() const;

  /**
   * Set the %MATS version string.
   *
   * @param[in] ver %MATS version string.
   */
  void setVersion(const char* ver);

  /**
   * Returns the note (general description).
   */
  const char* note() const;

  /**
   * Set the note.
   *
   * @param[in] note Note or general description.
   */
  void setNote(const char* note);

  /**
   * Returns the creation date/time of the configuration.
   * Time is in seconds, UTC referenced to the 1970 epoch.
   */
  double time() const;

  /**
   * Set the creation date/time of the configuration.
   *
   * @param[in] time Time in seconds, UTC referenced to the 1970 epoch.
   */
  void setTime(double time);

  /**
   * Returns the sensor name associated with the configuration.
   */
  const char* sensor() const;

  /**
   * Set the sensor name associated with the configuration.
   *
   * @param[in] sensor Name of the sensor.
   */
  void setSensor(const char* sensor);

  /**
   * Returns the name of the detector module.
   */
  const char* detector() const;

  /**
   * Sets the name of the detector module.
   *
   * @param[in] det Name of the detector module.
   */
  void setDetector(const char* det);

  /**
   * Returns the interface of the detector module.
   */
  const char* detLang() const;

  /**
   * Sets the interface of the detector module.
   *
   * @param[in] detlang Name of the detector module's interface.
   */
  void setDetLang(const char* detlang);

  /**
   * Returns the detector version.
   */
  const char* detVer() const;

  /**
   * Sets the detector version.
   *
   * @param[in] detver Detector version.
   */
  void setDetVer(const char* detver);

  /**
   * Returns a constant reference to the detector configuration.
   */
  const MATS_struct& detCfg() const;

  /**
   * Sets the detector configuration.
   *
   * @param[in] detcfg Detector configuration.
   */
  void setDetCfg(const mats::MATS_struct& detcfg);

  /**
   * Returns the name of the normalizer module.
   */
  const char* normalizer() const;

  /**
   * Sets the name of the normalizer module.
   *
   * @param[in] norm Name of the normalizer module.
   */
  void setNormalizer(const char* norm);

  /**
   * Returns the interface of the normalizer module.
   */
  const char* normLang() const;

  /**
   * Sets the interface of the normalizer module.
   *
   * @param[in] normlang Name of the normalizer module's interface.
   */
  void setNormLang(const char* normlang);

  /**
   * Returns the normalizer version.
   */
  const char* normVer() const;

  /**
   * Sets the normalizer version.
   *
   * @param[in] normver Normalizer version.
   */
  void setNormVer(const char* normver);

  /**
   * Returns a constant reference to the normalizer configuration.
   */
  const MATS_struct& normCfg() const;

  /**
   * Sets the normalizer configuration.
   *
   * @param[in] normcfg Normalizer configuration.
   */
  void setNormCfg(const mats::MATS_struct& normcfg);

  /**
   * Returns the config directory used for loading config files.
   */
  const char* configDirectory() const;

  /**
   * Set the config directory used for loading config files.
   *
   * @param[in] cfgDir Config directory path.
   */
  void setConfigDirectory(const char* cfgDir);

  /**
   * Returns the current filename being used (full path).
   */
  const char* filename() const;

  /**
   * Set the filename to use.
   *
   * @param[in] filename Filename (either full path or basename only).
   */
  void setFilename(const char* filename);

  /**
   * Loads a dconfig file.
   *
   * @param[in] filename This may be either the full path and filename of a
   * dconfig file, or just the UUID (without a file extension).  If just a
   * UUID is supplied, the config directory will be searched for the dconfig
   * file by that name.
   *
   * @return Returns 0 on success.
   */
  int load(const char* filename);

  /**
   * The dconfig is saved using whatever filename has already been set.
   *
   * @return Returns 0 on success.
   */
  int save();

  /**
   * Displays the contents of the configuration.
   */
  void display() const;

 private:
  /**
   * Clears the configuration.
   */
  void clear();

  std::string cfgDir_;
  std::string fn_;

  std::string ver_;
  std::string note_;
  double time_;
  std::string sensor_;

  std::string det_;
  std::string detlang_;
  std::string detver_;
  MATS_struct detcfg_;

  std::string normalizer_;
  std::string normlang_;
  std::string normver_;
  MATS_struct normcfg_;
};


/**
 * %MATS ATR Configuration - cconfig
 *
 * This class handles a cconfig file and feature/classifier configuration.
 */
class MATS_LIB MATS_cconfig {
 public:
  /**
   * Construct a MATS_cconfig using the default config directory.
   */
  MATS_cconfig();

  /**
   * Construct a MATS_cconfig, specifying which path to search for
   * cconfig files.
   *
   * @param[in] cfgDir The config directory path.
   */
  MATS_cconfig(const char* cfgDir);

  /**
   * MATS_cconfig destructor.
   */
  ~MATS_cconfig();

  /**
   * Returns the %MATS version string.
   */
  const char* version() const;

  /**
   * Set the %MATS version string.
   *
   * @param[in] ver %MATS version string.
   */
  void setVersion(const char* ver);

  /**
   * Returns the note (general description).
   */
  const char* note() const;

  /**
   * Set the note.
   *
   * @param[in] note Note or general description.
   */
  void setNote(const char* note);

  /**
   * Returns the creation date/time of the configuration.
   * Time is in seconds, UTC referenced to the 1970 epoch.
   */
  double time() const;

  /**
   * Set the creation date/time of the configuration.
   *
   * @param[in] time Time in seconds, UTC referenced to the 1970 epoch.
   */
  void setTime(double time);

  /**
   * Returns the sensor name associated with the configuration.
   */
  const char* sensor() const;

  /**
   * Set the sensor name associated with the configuration.
   *
   * @param[in] sensor Name of the sensor.
   */
  void setSensor(const char* sensor);

  /**
   * Returns the name of the detector module.
   */
  const char* detector() const;

  /**
   * Sets the name of the detector module.
   *
   * @param[in] det Name of the detector module.
   */
  void setDetector(const char* det);

  /**
   * Returns the length of the detector module's feature vector.
   * (Not all detectors produce features, in which case this is 0.)
   */
  size_t detFeatLen() const;

  /**
   * If the detector module produces features, set the detector module's
   * feature normalization vector.
   *
   * If the length of the detector module's feature vector is len, then the
   * length of this normalization vector should be 2*len.  There are two
   * entries for each feature:  norm[2*n] is the mean of the feature, and
   * norm[2*n+1] is the standard deviation of the feature, where n is the
   * feature index.  For no normalization, set norm[2*n] = 0 and
   * norm[2*n+1] = 1.
   *
   * @param[in] norm Feature normalization vector.
   *
   * @return Returns 0 on success.
   */
  int setDetFeatNorm(const std::vector<double>& norm);

  /**
   * Returns a constant reference to the names of the feature modules.
   */
  const std::vector<std::string>& features() const;

  /**
   * Returns a constant reference to the interface names of the feature modules.
   */
  const std::vector<std::string>& featLangs() const;

  /**
   * Returns a constant reference to the versions of the feature modules.
   */
  const std::vector<std::string>& featVers() const;

  /**
   * Returns a constant reference to the configurations of the feature modules.
   */
  const std::vector<MATS_struct>& featCfgs() const;

  /**
   * Returns a constant reference to the vector lengths of the feature modules.
   */
  const std::vector<size_t>& featLens() const;

  /**
   * Returns a constant reference to the normalization parameters of all
   * feature modules, including
   * any features from the detector.  There are
   * two entries for each feature:  the mean of the feature, and the
   * standard deviation of the feature.  The vector contains these parameters
   * in this order:  mean of feature 0, std dev of feature 0, mean of feature 1,
   * std dev of feature 1, ...  Note that each feature module may contain
   * multiple features.
   */
  const std::vector<double>& featNorm() const;

  /**
   * Add a feature module to the configuration.
   *
   * @param[in] name Feature module name.
   * @param[in] lang Feature module interface, e.g., "MATS_C" or "MATS_MCR".
   * @param[in] ver Feature module version.
   * @param[in] norm Normalization parameters for the feature module.  If the
   * length of the feature vector is len, then the length of this norm vector
   * should be 2*len.  There are two entries for each feature in the module:
   * norm[2*n] is the mean of the feature, and norm[2*n+1] is the standard
   * deviation of the feature, where n is the feature index.  For no
   * normalization, set norm[2*n] = 0 and norm[2*n+1] = 1.
   * @param[in] cfg Feature module configuration.
   *
   * @return Returns 0 on success.
   */
  int addFeature(const char* name, const char* lang, const char* ver,
      const std::vector<double>& norm, const mats::MATS_struct& cfg);

  /**
   * Remove a feature module from the configuration.
   *
   * @param[in] ix Index (0-based) of the feature module.
   *
   * @return Returns 0 on success.
   */
  int removeFeature(size_t ix);

  /**
   * Returns the name of the classifier module.
   */
  const char* classifier() const;

  /**
   * Sets the name of the classifier module.
   *
   * @param[in] cls Name of the classifier module.
   */
  void setClassifier(const char* cls);

  /**
   * Returns the interface of the classifier module.
   */
  const char* clsLang() const;

  /**
   * Sets the interface of the classifier module.
   *
   * @param[in] clslang Name of the classifier module's interface.
   */
  void setClsLang(const char* clslang);

  /**
   * Returns the classifier version.
   */
  const char* clsVer() const;

  /**
   * Sets the classifier version.
   *
   * @param[in] clsver Classifier version.
   */
  void setClsVer(const char* clsver);

  /**
   * Returns a constant reference to the classifier configuration.
   */
  const MATS_struct& clsCfg() const;

  /**
   * Sets the classifier configuration.
   *
   * @param[in] clscfg Classifier configuration.
   */
  void setClsCfg(const mats::MATS_struct& clscfg);

  /**
   * Returns a constant reference to the contact loading information.
   */
  const MATS_struct& clinfo() const;

  /**
   * Sets the contact loading information.
   *
   * @param[in] clinfo Contact loading information.
   */
  void setClinfo(const mats::MATS_struct& clinfo);

  /**
   * Returns the threshold of the configuration.
   */
  double threshold() const;

  /**
   * Set the threshold of the configuration.
   *
   * @param[in] thresh Threshold.
   */
  void setThreshold(double thresh);

  /**
   * Returns a constant reference to the ROC curve of the configuration.
   */
  const ATR_ROC& ROC() const;

  /**
   * Set the ROC curve of the configuration.
   *
   * @param[in] roc ROC curve.
   */
  void setROC(const ATR_ROC& roc);

  /**
   * Returns the config directory used for loading config files.
   */
  const char* configDirectory() const;

  /**
   * Set the config directory used for loading config files.
   *
   * @param[in] cfgDir Config directory path.
   */
  void setConfigDirectory(const char* cfgDir);

  /**
   * Returns the current filename being used (full path).
   */
  const char* filename() const;

  /**
   * Set the filename to use.
   *
   * @param[in] filename Filename (either full path or basename only).
   */
  void setFilename(const char* filename);

  /**
   * Loads a cconfig file.
   *
   * @param[in] filename This may be either the full path and filename of a
   * cconfig file, or just the UUID (without a file extension).  If just a
   * UUID is supplied, the config directory will be searched for the cconfig
   * file by that name.
   *
   * @return Returns 0 on success.
   */
  int load(const char* filename);

  /**
   * The cconfig is saved using whatever filename has already been set.
   *
   * @return Returns 0 on success.
   */
  int save();

  /**
   * Displays the contents of the configuration.
   */
  void display() const;

 private:
  /**
   * Clears the configuration.
   */
  void clear();

  std::string cfgDir_;
  std::string fn_;

  std::string ver_;
  std::string note_;
  double time_;
  std::string sensor_;

  std::string det_;
  size_t detlen_;

  std::vector<std::string> feat_;
  std::vector<std::string> featlang_;
  std::vector<std::string> featver_;
  std::vector<MATS_struct> featcfg_;
  std::vector<size_t> featlen_;
  std::vector<double> featnorm_;

  std::string cls_;
  std::string clslang_;
  std::string clsver_;
  MATS_struct clscfg_;

  MATS_struct clinfo_;
  double thresh_;
  mats::ATR_ROC roc_;
};


/**
 * Returns the interface name for the processing stream used by a particular
 * atrconfig, e.g., "MATS_C" or "MATS_MCR".
 *
 * @param[in] filename The full pathname of the atrconfig file.
 *
 * @return Returns the interface name, if found. Otherwise, returns an empty
 * string.
 */
MATS_LIB std::string
mats_atrconfig_stream(const std::string& filename);


}  // namespace mats

#endif  // SRC_MATS_ATRCONFIG_H_
