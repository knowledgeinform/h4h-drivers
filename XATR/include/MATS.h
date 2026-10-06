/**
 * @file
 * @brief File contains high-level classes and routines for running MATS ATR,
 * creating packages, and writing output to file.
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
#ifndef SRC_MATS_H_
#define SRC_MATS_H_

#include "MATS_core.h"
#include "MATS_manager.h"
#include "MATS_graphics.h"
#include "MATS_sensor.h"
#include "MATS_archive.h"
#include "MATS_groundtruth.h"


namespace mats {
class MATS_package;
class MATS_C;
}


/**
 * This function type is used when developing a package library of C++ modules.
 *
 * A library's function for creating and filling in the MATS_package should have
 * this type.  This function should be named "loadPackage" in the library.
 */
typedef mats::MATS_package* createPkgFn();

/**
 * This function type is used when developing a package library of C++ modules.
 *
 * A library's function for destroying the MATS_package should have this
 * type.  This function should be named "freePackage" in the library.
 */
typedef void destroyPkgFn(mats::MATS_package*);


/**
 * Template for generic module create function. The input parameter @p loadstr
 * is only used by wrappers for non-C++ modules.  For C++ modules, the
 * constructor should take this as an input parameter, but it should not be
 * used.
 */
template <class DT> void* modCreateFcn(const char* loadstr) {
  DT *mod_create_fcn = new DT(loadstr);
  if (!mod_create_fcn) {
    std::stringstream msg;
    msg << "Module creation failure (" << loadstr << ")";
    mats_log(MATS_ERROR, msg.str().c_str());
    return 0;
  }
  return static_cast<void *>(mod_create_fcn);
}


/**
 * Template for generic module destroy function.
 */
template <class DT> void modDestroyFcn(void* ptr) {
  delete (DT*) ptr;
  return;
}


namespace mats {

/**
 * Initialize %MATS_C.
 *
 * This function ensures that existing C++ sensor and graphics modules are
 * detected.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int mats_initialize();


/**
 * Obtain lock for dynamic loading.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int mats_lock_dl();


/**
 * Release lock for dynamic loading.
 *
 * @return Return 0 on success.
 */
MATS_LIB int mats_unlock_dl();


/**
 * %MATS Package Class
 *
 * This class holds a set of module wrappers (MATS_module) that describe the
 * modules contained within the package and provide functions for dynamically
 * creating and destroying the modules.  It is used when developing C++
 * packages.
 */
class MATS_LIB MATS_package {
  friend class MATS_C;

 public:
  /**
   * Construct a MATS_package.
   *
   * @param[in] n Memory for this many modules will be reserved.
   * @param[in] version (Optional) The package version.
   * @param[in] developer (Optional) The package developer.
   */
  MATS_package(size_t n, const char* version = NULL,
      const char* developer = NULL);

  /**
   * Add a MATS_module (module wrapper) to the package. When calling this
   * method, it must be templated to the derived module class.
   *
   * @param[in] name The module name.
   * @param[in] description (Optional) The module description.
   *
   * @return Returns 0 on success.
   */
  template <class MODNAME> int
  add(const char* name, const char* description = NULL) {
    return this->add_(name, (MODNAME*) 0, &modCreateFcn<MODNAME>,
        &modDestroyFcn<MODNAME>, description);
  }

  /**
   * Displays the modules contained in the package.
   * This function only works if the MATS_DEBUG flag is set.
   */
  void show() const;

  /**
   * Returns requested module.
   */
  MATS_module module(size_t k) const;

  /**
   * Returns the number of modules in package.
   */
  size_t size() const;

 private:
  /**
   * Template type deduction does not consider implicit conversion, but
   * overload resolution does. Therefore, an overload is provided for each
   * module base type. This allows us to determine the module base type
   * programmatically.
   */
  int add_(const char* name, MATS_detector* modPtr,
      void* (*create)(const char*), void (*destroy)(void*),
      const char* description);
  int add_(const char* name, MATS_feature* modPtr,
      void* (*create)(const char*), void (*destroy)(void*),
      const char* description);
  int add_(const char* name, MATS_classifier* modPtr,
      void* (*create)(const char*), void (*destroy)(void*),
      const char* description);
  int add_(const char* name, MATS_normalizer* modPtr,
      void* (*create)(const char*), void (*destroy)(void*),
      const char* description);
  int add_(const char* name, MATS_reader* modPtr,
      void* (*create)(const char*), void (*destroy)(void*),
      const char* description);
  int add_(const char* name, MATS_gt_reader* modPtr,
      void* (*create)(const char*), void (*destroy)(void*),
      const char* description);
  int add_(const char* name, MATS_writer* modPtr,
      void* (*create)(const char*), void (*destroy)(void*),
      const char* description);
  int add_(const char* name, MATS_interface* modPtr,
      void* (*create)(const char*), void (*destroy)(void*),
      const char* description);
  int add_(const char* name, MATS_sensor* modPtr,
      void* (*create)(const char*), void (*destroy)(void*),
      const char* description);
  int add_(const char* name, MATS_graphics_display* modPtr,
      void* (*create)(const char*), void (*destroy)(void*),
      const char* description);
  int add_(const char* name, MATS_graphics_exporter* modPtr,
      void* (*create)(const char*), void (*destroy)(void*),
      const char* description);
  int add_(const char* name, MATS_segmenter* modPtr,
      void* (*create)(const char*), void (*destroy)(void*),
      const char* description);
  int add_(const char* name, MATS_extension* modPtr,
      void* (*create)(const char*), void (*destroy)(void*),
      const char* description);

  /**
   * A templated subroutine is used by the add_() method to reduce code
   * repetition.
   */
  template <class DT> int add_template_(const char* name, DT*,
      void* (*create)(const char*), void (*destroy)(void*),
      const char* description);

  std::vector<MATS_module> modules_;  /**< the package's modules */
  std::string version_;  /**< the package version */
  std::string developer_;  /**< the package developer */
};


/**
 * Threading structure used for parallel chunk processing.
 */
struct MATS_LIB MATS_chunk_job {
  size_t id;  /**< Thread id. */
  size_t start;  /**< Starting chunk index. */
  size_t end;  /**< Ending chunk index. */
  MATS_C* mats;  /**< Main program (Used to call configured modules). */
  MATS_input* input;  /**< Data begin processed. */
  MATS_segment* chunk;  /**< Description of data chunks to be processed. */
  MATS_contact_list con;  /**< Contacts generated by threads processing. */
  MATS_ecdata_list ecd;  /**< Ecdata generated by threads processing. */
};


MATS_LIB int
mats_manager_load_package(const char* loadStr, mats::PkgLib& loadedPkg,
    std::list<mats::MATS_module>& modules);


MATS_LIB int
mats_manager_folder_scan(const char* folderPath,
    std::list<mats::MATS_module>& modules);


MATS_LIB int
mats_manager_has_scanned();


/**
 * %MATS C++ Interface Derived Class
 *
 * This class is derived from MATS_interface.  It is the platform from which
 * all modules must be loaded and created, including other MATS_interface
 * modules.
 */
class MATS_LIB MATS_C : public MATS_interface {
 public:
  /**
   * Construct a MATS_C. This auto-scans for CPP packages.
   */
  MATS_C();

  /**
   * MATS_C destructor.
   */
  ~MATS_C();

 private:
  /*
   * These are virtual MATS_interface methods, implemented specifically for
   * the C++ interface.
   */
  int scanFolder_(const char* folderPath, std::list<MATS_module>& modules);
  int loadPackage_(const char* loadStr, PkgLib& loadedPkg,
      std::list<MATS_module>& modules);
  int configure_(const MATS_atrconfig& cfg);
  int process_(MATS_input& input, MATS_contact_list& contacts,
      MATS_ecdata_list& ecdata);

  int retrain_(
    const std::vector<std::string>& arcList,
    const ATR_Configuration& cfg,
    ATR_Configuration* outCfg);

  /*
   * Create the required interface for the given module, then
   * create and configure the module and assign it to the given pointer.
   * However, if the same module is being used, use the existing one instead.
   */
  template<class DT> int assignModule(DT* &pMod,
      mats::MATS_interface* &pInt,
      mats::MATS_module_description& getMod,
      mats::MATS_struct& modCfg);

  /* These methods call the appropriate modules to do each processing step. */
  int detect(const MATS_input_base& input_struct, MATS_contact_list& contacts,
      MATS_ecdata_list& ecdata) const;
  int feature(MATS_contact_list& contacts,
      const MATS_ecdata_list& ecdata) const;
  int classify(MATS_contact_list& contacts, MATS_ecdata_list& ecdata) const;
  int normalize(MATS_input_base& input) const;

  /* Pointers to the configured processing-step modules and interfaces */
  MATS_detector* detector_;
  MATS_interface* detInt_;
  std::vector<MATS_feature*> features_;
  std::vector<MATS_interface*> featInt_;
  MATS_classifier* classifier_;
  MATS_interface* clsInt_;
  MATS_normalizer* normalizer_;
  MATS_interface* normInt_;

  /* useful information */
  bool unitTest_;
  std::string testPath_;

  /* Used in the processing stream. */
  int normalize_images_good_regions(MATS_input& input,
      const std::vector<MATS_region>& bad_regions) const;
  int atr_chunking_wrapper_c(MATS_input& input,
      const std::vector<MATS_region>& bad_regions,
      MATS_contact_list& contacts, MATS_ecdata_list& ecdata);

  /**
   * Threading function used for parallel chunk processing.
   */
  friend void* chunk_processing(void* th);

  /**
   * Indicate if chunking is enable.
   */
  bool chunking_;
};


#ifndef MATS_WINDOWS
MATS_LIB void* chunk_processing(void* th);
#endif


/**
 * %MATS Main Processing Class
 *
 * This is the high-level interface for configuring and running the ATR.
 */
class MATS_LIB MATS : protected MATS_C {
 public:
  /**
   * MATS constructor.
   */
  MATS();

  /**
   * MATS destructor.
   */
  ~MATS();

  /**
   * Set advanced options for processing.
   *
   * @param[in] opt Options structure containing option and value pairs.
   *
   * @return Returns 0 on success.
   */
  int options(const MATS_struct& opt);

  /**
   * Returns the current version of %MATS.
   */
  const char* version() const;

  /**
   * Returns a copy of current ATR configuration.
   *
   * @return ATR current configuration
   */
  mats::ATR_Configuration configuration() const;

  /**
   * Creates and configures a processing stream for the data.  Configuration
   * information is chosen based on the given sensor and configuration UUID.
   *
   * @param[in] sensor Name of the sensor.
   * @param[in] uuid (Optional) UUID of the desired configuration.  If none is
   * provided, the first selected configuration is used instead.
   *
   * @return Returns 0 on success.
   */
  int configure(const char* sensor, const char* uuid = NULL);

  /**
   * Imports data from file into MATS_input structure, runs %MATS ATR
   * on that structure, and produces MATS_contact and MATS_ecdata vectors
   * of results.
   *
   * @param[in] filename Filename of data file.
   * @param[out] contacts Vector of MATS_contact structures.
   * @param[out] ecdata Vector of MATS_ecdata structures.
   * @param[in] uuid (Optional) UUID of configuration to use for processing.
   *
   * @return Returns 0 on success.
   */
  int atr(const char* filename, MATS_contact_list& contacts,
      MATS_ecdata_list& ecdata, const char* uuid = NULL);

  /**
   * Run %MATS ATR on a specified input structure.
   *
   * @param[in] input The input structure to be processed.
   * @param[out] contacts Vector of MATS_contacts returned by ATR.
   * @param[out] ecdata Vector of MATS_ecdatas returned by ATR.
   *
   * @return Returns 0 on success.
   *
   * @warning The @p input is typically modified during processing.
   */
  int atr(MATS_input& input, MATS_contact_list& contacts,
      MATS_ecdata_list& ecdata);

  /**
   * Add runtime groundtruth information to be applied to generated contacts.
   *
   * @param[in,out] gt Vector of known contact locations (will be cleared upon
   * successful completion).
   */
  void addGroundtruth(std::vector<MATS_groundtruth>& gt);

  /**
   * Enable/Disable result archiving.
   *
   * @param[in] enabled Flag to enable/disable archiving.
   * @param[in] saveLocation File system location to save archives.
   */
  void archive(bool enabled, const char* saveLocation);

  /**
   * Retrains configured ATR with output from archives. Archives should contain
   * groundtruth.
   *
   * @param[in] arcList List of archive IDs to use for retraining.
   * @param[out] outCfg Retrained configuration.
   *
   * @return Returns 0 on success.
   */
  int retrain(const std::vector<std::string>& arcList,
      mats::ATR_Configuration* outCfg);

  /**
   * Returns generated archive list.
   *
   * @note This archive list is obtained from ATR processing and is not
   * related to any archive list used for retraining.
   */
  std::vector<std::string> archiveList();

  /**
   * Returns list of readable data file types.
   */
  std::vector<std::string> valid_file_types();


  /**
   * Returns detected sensor for file.
   */
  std::string
  file_sensor(const char* filename);

 private:
  mats::ATR_Configuration atrconfig_;
  std::string procStream_;
  int writeContacts_;  /**< writeContacts flag, 0 (false) by default */
  bool timing_;  /**< Enable timing flag, 0 (no timing) by default */

  MATS_reader* reader_;
  MATS_interface* processor_;
  std::vector<MATS_groundtruth> gt_;

  MATS_archiver archiver_;
  MATS_archive arc_;
  std::string archive_;
  std::vector<std::string> arcList_;

  bool writeInputs_;
  bool confidenceNormalization_;
  std::string writeInputsPath_;

  const MATS_graphics_exporter* mgx_;
  int bandFlag_;  /**< 0 to image ref band; 1 to image all bands */
  void exportImage_(MATS_input& input, const MATS_contact_list& con,
      const MATS_ecdata_list& ecd);

  /**
   * Confirm that the correct reader is being used.  If not, switch to the
   * correct one and configure it.
   *
   * @param[in] filename Filename with the desired extension.
   *
   * @return Returns 0 on success.  If no reader was found to match the file
   * extension, a warning is issued and a 1 is returned.
   */
  int selectReader_(const char* filename);
};


/**
 * Stores contacts and ecdata in HDF5 files.
 *
 * @param[in] fileNameContacts Filename for contacts HDF5 file.
 * @param[in] filenameEcdata Filename for ecdata HDF5 file.
 * @param[in] contacts List of contacts.
 * @param[in] ecdata List of ecdata.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int write_detections_HDF5(const std::string& fileNameContacts,
    const std::string& filenameEcdata, const MATS_contact_list& contacts,
    const MATS_ecdata_list& ecdata);


/**
 * Write a sequence of %MATS contacts to an XML file.
 *
 * @param[in] conList List of contacts.
 * @param[in] ecList List of ecdata. Entries should correspond to those
 * in @p conList.
 * @param[in] filename Path to file to be written.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
mats_contacts_to_xmlfile(const MATS_contact_list& conList,
    const MATS_ecdata_list& ecList, const char* filename);


/**
 * Return detected sensor name of file.
 *
 * @param[in] filename Path to file.
 *
 * @return Returns empty string on failure.
 */
std::string
detect_file_sensor(const char* filename);
}  // namespace mats

#endif  // SRC_MATS_H_
