/**
 * @file
 * @brief File contains classes and functions for package management, as well
 * as several module base classes.
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
#ifndef SRC_MATS_MANAGER_H_
#define SRC_MATS_MANAGER_H_

#include <string>
#include <vector>
#include <list>
#include <set>

#include "MATS_input.h"
#include "MATS_contact.h"
#include "MATS_ecdata.h"
#include "MATS_groundtruth.h"
#include "MATS_atrconfig.h"
#include "MATS_cfg.h"


/**
 * This function type is used when developing a new MATS_interface derived
 * class.
 * An interface's function for unloading a library should have the following
 * type, where the void* is a library handle.
 */
typedef void unloadLibFn(void*);


namespace mats {

class MATS_interface;


/**
 * Module type.
 */
enum MATS_module_type {
  matsUNKNOWN_MOD_TYPE,
  matsDETECTOR,
  matsFEATURE,
  matsCLASSIFIER,
  matsREADER,
  matsINTERFACE,
  matsNORMALIZER,
  matsSENSOR,
  matsGRAPHICSDISPLAY,
  matsGRAPHICSEXPORTER,
  matsSEGMENTER,
  matsWRITER,
  matsGTREADER,
  matsEXTENSION
};


/**
 * Module Description Structure
 */
struct MATS_about {
  MATS_about(): type(matsUNKNOWN_MOD_TYPE) {}

  /**
   * Clear contents.
   */
  void clear() {
    type = matsUNKNOWN_MOD_TYPE;
    name.clear();
    description.clear();
    tag.clear();
    engine.clear();
    package.clear();
    version.clear();
    developer.clear();
    return;
  }

  MATS_module_type type;  /**< module type */
  std::string name;  /**< module name */
  std::string description;  /**< module description */
  std::string tag;  /**< module tag */
  std::string engine;  /**< language/engine the module uses */
  std::string package;  /**< name of package containing module */
  std::string version;  /**< package version */
  std::string developer;  /**< package developer */
};


/**
 * Module Wrapper Class
 *
 * This class encapsulates information about a specific module, for use by
 * the package manager.  This includes information such as the name, type,
 * and engine of the module, how to load the module and its package, and its
 * create and destroy functions.
 */
class MATS_LIB MATS_module {
  friend class MATS_interface;
 public:
  /**
   * Construct a MATS_module with empty parameters.
   */
  MATS_module();

  /**
   * Construct a MATS_module.
   *
   * @param[in] name The module name.
   * @param[in] type The module type.
   * @param[in] engine The module's engine.  This is not the interface name,
   * but is the name of the folder containing the interface's packages.  For
   * example, the interface "MATS_Python" has engine name "Python", and the
   * interface "MATS_C" has engine name "CPP".
   * @param[in] create The function that dynamically creates new instances of
   * this module.
   * @param[in] destroy The function that destroys instances of this module.
   */
  MATS_module(const char* name, MATS_module_type type, const char* engine,
      void* (*create)(const char*), void (*destroy)(void*));

  /**
   * Set the module's information.
   *
   * @param[in] name The module name.
   * @param[in] type The module type.
   * @param[in] engine The module's engine.  This is not the interface name,
   * but is the name of the folder containing the interface's packages.  For
   * example, the interface "MATS_Python" has engine name "Python", and the
   * interface "MATS_C" has engine name "CPP".
   * @param[in] create The function that dynamically creates new instances of
   * this module.
   * @param[in] destroy The function that destroys instances of this module.
   *
   * @return Returns 0 on success.
   */
  int set(const char* name, MATS_module_type type, const char* engine,
      void* (*create)(const char*), void (*destroy)(void*));

  /**
   * Set the module's package name and path.  This method is used by an
   * interface to set this additional information upon discovering an
   * available module.
   *
   * @param[in] name The name of the package containing the module.
   * @param[in] fullpath The string used for loading the package, e.g., the
   * full path to the package.  This depends on the specific interface.
   *
   * @return Returns 0 on success.
   */
  int setPackage(const char* name, const char* fullpath);

  /**
   * Set the module's full loading string.  This method is used by an interface
   * (if necessary) to set this additional information upon discovering an
   * available module.  The loading string is the input to the module creation
   * function (modCreate).  For example, Python uses a loading string formatted
   * as PACKAGE.MODULE.
   *
   * @param[in] loadstr The full loading string for the module.
   *
   * @return Returns 0 on success.
   */
  int setLoadStr(const char* loadstr);

  /**
   * Set the module's tag.
   *
   * @param[in] tag Tag for the module.
   *
   * @return Returns 0 on success.
   */
  int setTag(const char* tag);

  /**
   * Set the module's package version.
   *
   * @param[in] version Version of the package containing the module.
   *
   * @return Returns 0 on success.
   */
  int setVersion(const char* version);

  /**
   * Set the module's package developer.
   *
   * @param[in] developer Developer of the package containing the module.
   *
   * @return Returns 0 on success.
   */
  int setDeveloper(const char* developer);

  /**
   * Set the module's description.
   *
   * @param[in] description Description of the module.
   *
   * @return Returns 0 on success.
   */
  int setDescription(const char* description);

  /**
   * Return information about this module.
   */
  const MATS_about& about() const;

  /**
   * Returns the module name.
   */
  const char* name() const;

  /**
   * Returns the name of the package containing the module.
   */
  const char* package() const;

  /**
   * Returns the version of the package containing the module.
   */
  const char* version() const;

  /**
   * Returns the full loading string for the module.
   */
  const char* loadStr() const;

  /**
   * Returns the full path to the package (or whatever string is used for
   * loading the package).
   */
  const char* packagePath() const;

  /**
   * Returns the module type.
   */
  MATS_module_type type() const;

  /**
   * Returns the module's engine name.  This is not the interface name,
   * but is the name of the folder containing the interface's packages.  For
   * example, the interface "MATS_Python" has engine name "Python", and the
   * interface "MATS_C" has engine name "CPP".
   */
  const char* engine() const;

  /**
   * Clear the module wrapper.
   */
  void clear();

  ~MATS_module();

 private:
  MATS_about info_;  /**< information about the module */
  std::string modPackagePath_;  /**< full loading string for the package */
  std::string modLoad_;  /**< full loading string for the module */
  void* (*modCreate_)(const char*);  /**< function to create a module instance */
  void (*modDestroy_)(void*);  /**< function to destroy a module instance */
};


/**
 * Module Abstract Base Class
 *
 * This is a base class for several module types.  Base classes for specific
 * module types (e.g., MATS_reader, MATS_detector, MATS_classifier) are derived
 * from this base class.
 */
class MATS_LIB MATS_module_base {
 public:
  MATS_module_base();
  virtual ~MATS_module_base() {}

  /**
   * Configure the module.
   *
   * @param[in] cfg Module configuration to load.
   *
   * @return Returns 0 on success.
   */
  int configure(const MATS_struct& cfg);

 protected:
  /**
   * Check whether module has been successfully configured.
   *
   * @return Returns true if module is configured; false otherwise.
   */
  bool isConfigured() const;

 private:
  bool configured_;  /**< whether the module is configured */

  /**
   * Method Implementations
   */
  virtual int configure_(const MATS_struct& cfg) = 0;
};


/**
 * Package Management
 *
 * A structure used to keep track of the handle and unloading function of
 * a package library.
 */
struct PkgLib {
  std::string name;  /**< Name of the package library. */
  std::string loadStr;  /**< Full loading string of the package library. */
  void* handle;  /**< Package library handle (used for unloading). */
  unloadLibFn* unloadLibrary;  /**< Function to unload the package library. */
};


/**
 * Interface / Processor Module Abstract Base Class
 *
 * This class serves as an interface for using a particular language or engine
 * for data processing.  It has two independent areas of functionality:
 *
 * 1.  Package Management:  The interface can load, create, and manage modules
 * for the engine, such as detector and classifier modules, that can be used
 * as parts of an overall C++ processing stream.
 *
 * 2.  Processing Stream:  The interface can use the engine to run the
 * processing stream itself.
 *
 * A derived MATS_interface class is itself a C++ module that can be loaded by
 * the MATS_C interface (defined in MATS.h).
 */
class MATS_LIB MATS_interface {
 public:
  /**
   * Construct a MATS_interface.
   */
  MATS_interface();

  /**
   * MATS_interface destructor.  This frees all the interface's modules from
   * memory and unloads all its packages.
   */
  virtual ~MATS_interface();

  /**
   * Package Management
   *
   * Returns the interface's engine name.  (This is the name of the folder
   * where the interface's packages are stored, not the name of the
   * interface's derived class.)
   */
  const char* engine() const;

  /**
   * Package Management
   *
   * Scan a folder for modules.
   *
   * @param[in]  folderPath Path to folder containing %MATS package libraries.
   *
   * @return Returns 0 on success.
   */
  int scanFolder(const char* folderPath);

  /**
   * Package Management
   *
   * Scan the default folder for modules.  The default folder is the folder
   * with the engine name, which is within the %MATS package directory.
   *
   * @return Returns 0 on success.
   */
  int autoScan();

  /**
   * Package Management
   *
   * Display all available %MATS modules along with their package and type.
   */
  void listModules() const;

  /**
   * Package Management
   *
   * Return all modules of a given type. Returned strings are in the format
   * "<package name>/<module name>".
   *
   * @param[in] modType The MATS_module_type being requested.
   *
   * @return Returns the list of modules.
   */
  std::vector<std::string> getType(MATS_module_type modType) const;

  /**
   * Package Management
   *
   * Return a wrapper for the given module.
   *
   * @param[in] modName The name of the module. Format may be either "<module
   * name>" or "<package name>/<module name>". If no package name specified,
   * the first module found with the given name will be used.
   *
   * @return Returns the module wrapper (MATS_module).
   */
  MATS_module module(const char* modName) const;

  /**
   * Package Management
   *
   * Returns pointer to a dynamically allocated instance of requested
   * module.
   *
   * If an existing reader or interface module is requested, the pointer to
   * the existing module is returned, and no module is dynamically allocated.
   *
   * @param[in] modName The name of the module. Format may be either "<module
   * name>" or "<package name>/<module name>". If no package name specified,
   * the first module found with the given name will be used.
   *
   * @return Returns pointer to new instance of module on success. On failure,
   * returns null pointer.
   *
   * @warning The created module is owned by the interface and should not be
   * deleted.
   */
  template<class DT>
  DT* createModule(const char* modName);

  /**
   * Package Management
   *
   * Free all dynamically allocated detector, feature, classifier, and
   * normalizer modules from memory (reader and interface modules are not
   * cleared).
   *
   * Note that the interface will free all its modules from memory when it is
   * destroyed, so there is no need to call this function at that time.
   * Rather, this function can be used to keep memory uncluttered during a
   * long-running program.
   *
   * @warning Be careful when using this method.  It destroys any existing
   * normalizer, detector, feature, and classifier modules from the interface.
   */
  void clearModules();

  /**
   * Package Management
   *
   * Free a dynamically allocated module from memory.
   *
   * Note that the interface will free all its modules from memory when it is
   * destroyed, so there is no need to call this function at that time.
   * Rather, this function can be used to keep memory uncluttered during a
   * long-running program.
   *
   * @param[in] modPtr Pointer to module.
   */
  void clearModule(void* modPtr);

  /**
   * Package Management
   *
   * Add an item to the blacklist for this interface (or remove it).  To
   * blacklist an entire package, leave the module field blank (or set it to 0
   * or "").  To blacklist a module, both the package and module names must
   * be provided.
   *
   * @param[in] package The name of the package.
   * @param[in] module (Optional) The name of the module.
   * @param[in] rem (Optional) Set to true to remove the item from the
   * blacklist; false to add the item to the blacklist. Defaults to false.
   *
   * @return Returns 0 on success.
   */
  int blacklist(const char* package, const char* module = NULL,
      bool rem = false);

  /**
   * Package Management
   *
   * Display the blacklist contents to stdout.
   */
  void blacklistShow();

  /**
   * Processing Stream
   *
   * Configure the interface's processing stream.
   *
   * @param[in]  config Desired configuration.
   *
   * @return Returns 0 on success.
   */
  int configure(const mats::MATS_atrconfig& config);

  /**
   * Processing Stream
   *
   * Use the interface to run a complete processing stream on input data.
   * Before calling this function, the interface should be configured using
   * configure().
   *
   * @param[in] input Input structure containing data to be processed.
   * @param[out] contacts The contacts found during processing.
   * @param[out] ecdata Extra contact data.
   *
   * @return Returns 0 on success.
   */
  int process(MATS_input& input, MATS_contact_list& contacts,
      MATS_ecdata_list& ecdata);

  /**
   * Processing Stream
   *
   * Retrain a configuration using the given archive list.
   *
   * @param[in] arcList List of archives to be used for retraining.
   * @param[in] cfg Configuration to be retrained.
   * @param[out] outCfg Retrained configuration.
   *
   * @return Returns 0 on success.
   */
  int retrain(const std::vector<std::string>& arcList,
      const mats::ATR_Configuration& cfg, mats::ATR_Configuration* outCfg);

 protected:
  /**
   * Package Management
   *
   * Checks whether a module is ready to create.
   *
   * @param[in] modName The name of the module. Format may be either "<module
   * name>" or "<package name>/<module name>". If no package name specified,
   * the first module found with the given name will be used.
   *
   * @return Returns true if the module is ready, false otherwise.
   */
  bool isReady(const char* modName) const;

  /**
   * Package Management
   *
   * Searches for a module and returns its package.
   *
   * @param[in] modName The name of the module. Format may be either "<module
   * name>" or "<package name>/<module name>". If no package name specified,
   * the first module found with the given name will be used.
   *
   * @return Returns the full loading string (a.k.a. the package path) of the
   * package containing the module. Returns "" if not found.
   */
  std::string findModule(const char* modName) const;

  /**
   * Package Management
   *
   * Load a package.
   *
   * @param[in]  loadStr Whatever string the specific implementation uses
   * for loading packages, e.g., the package name, the full path to the
   * package, or the package directory name.
   *
   * @return Returns 0 on success.
   */
  int loadPackage(const char* loadStr);

  /**
   * Package Management
   *
   * Unload a package.
   *
   * @param[in]  packageName Name of package to unload.
   *
   * @return Returns 0 on success.
   *
   * @warning Be careful when using this method.  It destroys any existing
   * modules from the package being unloaded.
   */
  int unloadPackage(const char* packageName);

  /**
   * Package Management
   *
   * Destroy all modules with the given name.
   *
   * @param[in] modName The name of the module. Format may be either "<module
   * name>" or "<package name>/<module name>". If no package name specified,
   * the first module found with the given name will be used.
   *
   * @return Returns 0 on success.
   *
   * @warning Be careful when using this method.  It destroys any existing
   * modules with the given name.
   */
  int destroyModule(const char* modName);

  /**
   * Processing Stream
   *
   * Get the current configuration of the processing stream.
   *
   * @return Returns a reference to the current configuration of the processing
   * stream.
   */
  const MATS_atrconfig& atrConfig() const;

  /**
   * Processing Stream
   *
   * Get the total length of the feature vector for the current configuration.
   *
   * @return The total length of the feature vector.
   */
  size_t totalFeatLen() const;

  /**
   * Set the engine name for this interface. (This is the name of the folder
   * where the interface's packages are stored, not the name of the
   * interface's derived class.) Use this method in the constructor of the
   * derived interface class.
   *
   * @param[in] engine The engine name.
   */
  void setEngine(const char* engine);

 private:
  /**
   * Package Management
   *
   * Implementation-Specific Method:
   * Scan a folder for modules.
   *
   * Notes:
   *
   * This method should make use of the MATS_module::setPackage() method to
   * attach the package name and path to each module.  It should also make use
   * of the MATS_module::setLoadStr() method to record the full loading string
   * for the module to be input to the modCreate function (for example, the
   * loading string for a Python module will be formatted as PACKAGE.MODULE).
   *
   * @param[in]  folderPath Path to folder containing MATS package libraries.
   * @param[out] modules List of available modules.
   *
   * @return Returns 0 on success.
   *
   * @warning If this method loads libraries into memory, it should also free
   * them before returning.
   */
  virtual int scanFolder_(const char* folderPath,
      std::list<MATS_module>& modules) = 0;

  /**
   * Package Management
   *
   * Implementation-Specific Method:
   * Load a package.
   *
   * Notes:
   *
   * It is assumed that this method loads the library into memory.  The memory
   * will be automatically freed by the MATS_interface.  However, if the
   * return value is non-zero, the library must be freed before returning.
   *
   * The 'loadedPkg' output should be populated with the appropriate fields:
   * 'name', 'handle', and 'unloadLibrary'.
   *
   * This method should make use of the MATS_module::setPackage() method to
   * attach the package name and path to each module.  It should also make use
   * of the MATS_module::setLoadStr() method to record the full loading string
   * for the module to be input to the modCreate function (for example, the
   * loading string for a Python module will be formatted as PACKAGE.MODULE).
   *
   * @param[in]  loadStr Whatever string the specific implementation uses
   * for loading packages, e.g., the package name, the full path to the
   * package, or the package directory name.
   * @param[out] loadedPkg Info about the package that was loaded.
   * @param[out] modules A list of modules contained in the package.
   *
   * @return Returns 0 on success.
   */
  virtual int loadPackage_(const char* loadStr, PkgLib& loadedPkg,
      std::list<MATS_module>& modules) = 0;

  /**
   * Package Management
   *
   * A structure used to keep track of the pointers to dynamically-allocated
   * instances of modules, along with their module wrappers.  This
   * information is used for destroying modules.
   */
  struct loadedMod {
      const MATS_module* modHandle;
      void* modPointer;
  };

  /**
   * Locate module in list by either "<module name>" or
   * "<package name>/<module name>". Returns pointer to first matching module.
   * Returns null pointer if none found.
   */
  const MATS_module*
  locateMod(const char* modName, const std::list<MATS_module>& modList) const;

  loadedMod*
  locateMod(const char* modName, std::list<loadedMod>& modList);

  /** Package Management */
  std::list<MATS_module> availModules_;  /**< available modules */
  std::list<MATS_module> readyModules_;  /**< modules ready to be created */
  std::list<loadedMod> createdModules_;  /**< created instances of modules */
  std::list<PkgLib> createdLibraries_;  /**< loaded package libraries */

  /**
   * Processing Stream
   *
   * Implementation-Specific Method:
   * Configure the interface's processing stream.
   *
   * (This method typically creates and stores an interface-specific
   * configuration in the derived class.)
   *
   * @param[in] cfg The configuration for the processing stream.
   *
   * @return Returns 0 on success.
   */
  virtual int configure_(const MATS_atrconfig& cfg) = 0;

  /**
   * Processing Stream
   *
   * Implementation-Specific Method:
   * Use the interface to run a complete processing stream on input data.
   * Before calling this function, the processing stream should be configured
   * using configure().
   *
   * (This method should do the following:
   * -  Convert the input structure into an interface-specific input.
   * -  Call the interface's appropriate processing function, making use of
   *    the interface-specific input and configuration.
   * -  Convert the output of the function into MATS_contact and MATS_ecdata
   *    structures.
   * )
   *
   * @param[in] input Input structure containing data to be processed.
   * @param[out] contacts The contacts found during processing.
   * @param[out] ecdata Extra contact data.
   *
   * @return Returns 0 on success.
   */
  virtual int process_(MATS_input& input, MATS_contact_list& contacts,
      MATS_ecdata_list& ecdata) = 0;

  /**
   * Processing Stream
   *
   * Implementation-Specific Method:
   * Retrain a configuration using the given archive list.
   *
   * @param[in] arcList List of archives to be used for retraining.
   * @param[in] cfg Configuration to be retrained.
   * @param[out] outCfg Retrained configuration.
   *
   * @return Returns 0 on success.
   */
  virtual int retrain_(
      const std::vector<std::string>& arcList,
      const mats::ATR_Configuration& cfg,
      mats::ATR_Configuration* outCfg);

  mats::MATS_atrconfig config_;  /**< current processing configuration */
  bool configured_;  /**< whether the processing stream is configured */
  size_t totalLen_;  /**< total length of feature vector */
  std::string engine_;  /**< the interface's engine name */
};


/**
 * Reader Module Base Class
 *
 * A base class for modules that read data from data files and load it into
 * MATS_input structures.
 */
class MATS_LIB MATS_reader : public MATS_module_base {
 public:
  MATS_reader();

  /**
   * Determines if a file is a valid file for the reader.
   *
   * @param[in] filename Filename of file to check.
   *
   * @return Returns true if valid, false otherwise.
   */
  bool isValid(const char* filename) const;

  /**
   * Import data from file to a MATS_input structure.
   *
   * Routine returns an array of MATS_input structures because some files may
   * contain both port and starboard data in the same file. The navigation
   * data in the file is interpolated to correspond with the along-track axis
   * of the reference dataset.
   *
   * @param[in] filepath Full path location of file to load.
   * @param[out] input Vector of loaded MATS_input structures from file.
   *
   * @return Returns 0 on success.
   */
  int read(const char* filepath, std::vector<MATS_input>& input) const;

  /**
   * Scans a folder for valid files for reader and creates a file list.
   *
   * @param[in]  folder Folder to scan for files.
   * @param[out] files  Generated file list from folder.
   *
   * @return Returns 0 on success.
   */
  int scan(const char* folder, std::vector<std::string>& files) const;

  /**
   * Return the file type (extension) that can be read by this reader (not
   * including the "."), in all lower-case.
   */
  const char* fileType() const;

 protected:
  /**
   * Set the data file type (file extension) read by this module. Use this
   * method in the constructor of the derived reader class.
   *
   * The file extension will be transformed to all lower-case.
   *
   * @param[in] ftype File extension.
   */
  void setFileType(const char* ftype);

 private:
  /**
   * Method Implementations
   */
  virtual bool isValid_(const char* filename) const = 0;
  virtual int read_(const char* filepath,
      std::vector<MATS_input>& input) const = 0;
  virtual int scan_(const char* folder,
      std::vector<std::string>& files) const = 0;

  std::string fileType_;  /**< File extension supported by this reader */
};


/**
 * GT Reader Module Base Class
 *
 * A base class for modules that read ground truth data files and load it into
 * MATS_groundtruth structures.
 */
class MATS_LIB MATS_gt_reader : public MATS_module_base {
 public:
  MATS_gt_reader();

  /**
   * Determines if a file is a valid ground truth file for the reader.
   *
   * @param[in] filename Filename of file to check.
   *
   * @return Returns true if valid, false otherwise.
   */
  bool isValid(const char* filename) const;

  /**
   * Import data from file to a MATS_groundtruth structure.
   *
   * @param[in] filepath Full path location of file to load.
   * @param[out] gtd Vector of loaded MATS_groundtruth structures from file.
   *
   * @return Returns 0 on success.
   */
  int read(const char* filepath, std::vector<MATS_groundtruth>& gtd) const;

  /**
   * Return the file type (extension) that can be read by this reader (not
   * including the "."), in all lower-case.
   */
  const char* fileType() const;

 protected:
  /**
   * Set the data file type (file extension) read by this module. Use this
   * method in the constructor of the derived reader class.
   *
   * The file extension will be transformed to all lower-case.
   *
   * @param[in] ftype File extension.
   */
  void setFileType(const char* ftype);

 private:
  /**
   * Method Implementations
   */
  virtual bool isValid_(const char* filename) const = 0;
  virtual int read_(const char* filepath,
      std::vector<MATS_groundtruth>& input) const = 0;

  std::string fileType_;  /**< File extension supported by this reader */
};


/**
 * Writer Module Base Class
 *
 * A base class for modules that writes common data structures out in different
 * formates.
 */
class MATS_LIB MATS_writer : public MATS_module_base {
 public:
  MATS_writer();

  /**
   * Writes MATS_input structure.
   *
   * @param[in] filename Name of output file.
   * @param[out] input MATS_input structures to be written.
   *
   * @return Returns 0 on success.
   */
  int write(const char* filename, const MATS_input_base& input) const;

  /**
   * Writes contact information.
   *
   * @param[in] filename Name of output file.
   * @param[out] con Contact list to be written.
   * @param[out] ecd Extra contact list to be written.
   *
   * @return Returns 0 on success.
   */
  int write(const char* filename, const MATS_contact_list& con,
      const MATS_ecdata_list& ecd) const;

  /**
   * Return the file type (extension) that can be read by this reader (not
   * including the "."), in all lower-case.
   */
  const char* fileType() const;

 protected:
  /**
   * Set the data file type (file extension) written by this module. Use this
   * method in the constructor of the derived writer class.
   *
   * The file extension will be transformed to all lower-case.
   *
   * @param[in] ftype File extension.
   */
  void setFileType(const char* ftype);

 private:
  /**
   * Method Implementations
   */
  virtual int write_(const char* filename,
      const MATS_input_base& input) const = 0;
  virtual int write_(const char* filename, const MATS_contact_list& con,
      const MATS_ecdata_list& ecd) const = 0;

  std::string fileType_;  /**< File extension supported by this reader */
};


/**
 * Detector Module Base Class
 *
 * A base class for modules that detect regions of interest in sensor data
 * and output them in MATS_contact and MATS_ecdata structures.
 */
class MATS_LIB MATS_detector : public MATS_module_base {
 public:
  MATS_detector();

  /**
   * Detect contacts in the given input.
   *
   * This method should fill in the following contact/ecdata fields:
   *     @li MATS_contact::x
   *     @li MATS_contact::y
   *     @li MATS_ecdata::detscore
   *
   * In addition, it may use MATS_contact::addFeature() to add a feature
   * name and vector to the contacts.
   *
   * Also, this method should ensure that each contact has a distinct UUID.
   * (It is not necessary to do this for the ecdata, as the contact's UUID
   * will be copied to the ecdata in the processing stream.)
   *
   * @param[in] input Input or chunk containing data.
   * @param[out] contacts List of contacts detected.
   * @param[out] ecdata Extra contact data.
   *
   * @return Returns 0 on success.
   */
  int detect(const MATS_input_base& input, MATS_contact_list& contacts,
      MATS_ecdata_list& ecdata);

  /**
   * Train the detector.
   *
   * @param[in] datafiles List of data files to use for training.
   * @param[in] reader MATS_reader for reading the data files.
   * @param[in] gt Ground-truth vector corresponding to data files.
   * @param[in] inStruct Parameters for training.
   * @param[out] outStruct A MATS_struct that can be used as a detector
   * configuration.
   *
   * @return Returns 0 on success.
   */
  int train(const std::vector<std::string>& datafiles,
      MATS_reader* reader, const std::vector<MATS_groundtruth>& gt,
      const MATS_struct& inStruct, MATS_struct& outStruct) const;

 private:
  /**
   * Method Implementations
   */
  virtual int detect_(const MATS_input_base& input, MATS_contact_list& contacts,
      MATS_ecdata_list& ecdata) = 0;
  virtual int train_(const std::vector<std::string>& datafiles,
      MATS_reader* reader, const std::vector<MATS_groundtruth>& gt,
      const MATS_struct& inStruct, MATS_struct& outStruct) const;
};


/**
 * Feature Module Base Class
 *
 * A base class for modules that quantify contact information into a
 * measurement or a series of measurements.
 */
class MATS_LIB MATS_feature : public MATS_module_base {
 public:
  MATS_feature();

  /**
   * Calculate feature vector for each contact.  If it
   * fails, it will add a feature vector containing all 0's to the contacts.
   *
   * This method should use MATS_contact::addFeature() to add a feature
   * name and vector to the contacts.
   *
   * @param[in,out] contacts List of contacts.
   * @param[in] ecdata Extra contact data.
   *
   * @return Returns 0 on success.
   */
  int feature(MATS_contact_list& contacts, const MATS_ecdata_list& ecdata);

  /**
   * Train the feature module.
   *
   * @note This method is not available yet.
   *
   * @return Returns 0 on success.
   */
  int train();

 private:
  /**
   * Method Implementations
   */
  virtual int feature_(MATS_contact_list& contacts,
      const MATS_ecdata_list& ecdata) = 0;
  virtual int train_();
};


/**
 * Classifier Module Base Class
 *
 * A base class for modules that use feature information of contacts to
 * discriminate between targets and non-targets.
 */
class MATS_LIB MATS_classifier : public MATS_module_base {
 public:
  MATS_classifier();

  /**
   * Classify contacts.
   *
   * This method should fill in the following contact/ecdata fields:
   *     @li MATS_contact::cls
   *     @li MATS_contact::classconf
   *
   * @param[in,out] contacts List of contacts.
   * @param[in,out] ecdata Extra contact data.
   *
   * @return Returns 0 on success.
   */
  int classify(MATS_contact_list& contacts,
      MATS_ecdata_list& ecdata);

  /**
   * Train the classifier module.
   *
   * @note This method is not available yet.
   *
   * @return Returns 0 on success.
   */
  int train();

 private:
  /**
   * Method Implementations
   */
  virtual int classify_(MATS_contact_list& contacts,
      MATS_ecdata_list& ecdata) = 0;
  virtual int train_();
};


/**
 * Normalizer Module Base Class
 *
 * A base class for modules that standardize sensor data to remove variability
 * and dynamic range changes.
 */
class MATS_LIB MATS_normalizer : public MATS_module_base {
 public:
  MATS_normalizer();

  /**
   * Normalize data in the given input.
   *
   * @param[in,out] input Input or chunk containing data.
   *
   * @return Returns 0 on success.
   */
  int normalize(MATS_input_base& input);

 private:
  virtual int normalize_(MATS_input_base& input) = 0;
};


/**
 * Segmenter Module Base Class
 *
 * A base class for modules that segments an image into a number of regions.
 */
class MATS_LIB MATS_segmenter : public MATS_module_base {
 public:
  MATS_segmenter();

  /**
   * Segment an image into regions.
   *
   * @param[in,out] input Input or chunk containing data.
   *
   * @return Returns 0 on success.
   */
  int segment(MATS_input_base &input);

 private:
  virtual int segment_(MATS_input_base &input) = 0;
};


/**
 * Extension Module Base Class
 *
 * A base class for modules that can be used by modules to extend capabilites.
 * Extension modules get applied to other modules.
 */
class MATS_LIB MATS_extension : public MATS_module_base {
 public:
  MATS_extension();

  /**
   * The name of the module to apply the extension.
   */
  std::string module() const;

  /**
   * Extension identifier string which can be used by a module to identify the
   * extension type.
   */
  std::string identifier() const;
};


/**
 * Get the MATS_module_type corresponding to the module class DT specified for
 * the template.
 *
 * @note The class DT must exactly match the module base class, e.g.,
 * a MATS_detector or MATS_feature.  A derived class will not work.
 *
 * @return Returns the MATS_module_type for the templated module class.
 */
template <class DT> MATS_LIB MATS_module_type mats_module_type();


/**
 * Display information in a MATS_about.
 *
 * @param[in] info MATS_about structure to display.
 */
MATS_LIB void displayMATSabout(const MATS_about& info);


/**
 * Add an item to the blacklist (or remove it).  To blacklist an entire package,
 * leave the module field blank (or set it to 0 or "").  To blacklist a module,
 * both the package and module names must be provided.
 *
 * @param[in] engine The engine that runs the package/module, e.g., "CPP" or
 * "Python".
 * @param[in] package The name of the package.
 * @param[in] module (Optional) The name of the module.
 * @param[in] rem (Optional) Set to true to remove the item from the
 * blacklist; false to add the item to the blacklist. Defaults to false.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int blacklist(const char* engine, const char* package,
    const char* module = NULL, bool rem = false);


/**
 * Display the blacklist contents to stdout.
 *
 * @param[in] engine (Optional) The engine name. (If not provided, the contents
 * of all available blacklist files are displayed.)
 */
MATS_LIB void blacklistShow(const char* engine = NULL);

}  // namespace mats

#endif  // SRC_MATS_MANAGER_H_
