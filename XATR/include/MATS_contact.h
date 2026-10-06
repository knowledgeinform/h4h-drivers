/**
 * @file
 * @brief File contains the MATS_contact structure used for MATS and MATS ATR
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
#ifndef SRC_MATS_CONTACT_H_
#define SRC_MATS_CONTACT_H_

#include <vector>
#include <string>
#include "MATS_platform.h"
#include "MATS_data.h"

#ifdef MATS_MEMORY
#include "MATS_memory.h"

extern MemoryManager GlMemoryManager;
#endif


namespace mats {

class MATS_contact;

/**
 * A vector of MATS_contact structures.
 */
typedef std::vector<MATS_contact> MATS_contact_list;


/** Operator feedback substructure */
struct MATS_LIB MATS_opfeedback{
  signed char opdisplay;  /**< operator display (int8) */
  signed char opconf;   /**< operator confidence (int8) */
  signed char type;     /**< operator determined obj. type (int8) */
};


/**
 * Base contact data container. Used internally to store MATS_contact
 * information. This class is not intended to be used outside of MATS_contact.
 */
class MATS_LIB MATS_contact_base {
 public:
  size_t id; /**< Contact ID */

  /* Pixel locations */
  size_t x; /**< Contact cross-track pixel location */
  size_t y; /**< Contact along-track pixel location */

  std::string fn; /**< Input data filename */
  std::string side; /**< Vehicle side string ["PORT"|"STBD"] */

  /* Module ID strings */
  std::string normalizer; /**< Name of normalizer module */
  std::string detector;   /**< Name of detector module */
  std::vector<std::string> featureset; /**< List of feature module names */
  std::string classifier; /**< Name of classifier module */
  std::string contcorr; /**< Name of contact correlation module */
  std::string uuid; /**< Contact UUID string */

  bool gt; /**< Ground truth contact flag [0|1] */
  int type; /**< Contact type ID */
  int cls; /**< Classifier classification */
  float classconf; /**< Classifier confidence score */

  std::vector<double> features; /**< Contact feature vector */
  std::vector<size_t> feature_size; /**< Length of features added */
  MATS_opfeedback opfeedback; /**< Operator feedback block */

 private:
  friend class MATS_contact;
  unsigned count_;
  MATS_contact_base();  // Prevent users from directly using
};


/**
 * Main contact data structure
 */
class MATS_LIB MATS_contact {
  friend MATS_LIB void
  mats_contact_swap(mats::MATS_contact& a, mats::MATS_contact& b);

 public:
  /**
   * Construct an empty MATS_contact.
   */
  MATS_contact();

  /**
   * Construct a copy of an existing MATS_contact.
   *
   * @param[in] con MATS_contact to be copied.
   */
  MATS_contact(const MATS_contact& con);

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
   * Returns the x-coordinate of contact (cross-track index).
   */
  size_t x() const;

  /**
   * Returns the y-coordinate of contact (along-track index).
   */
  size_t y() const;

  /**
   * Set the x-coordinate of contact (cross-track index).
   *
   * @param[in] x Cross-track index of contact.
   */
  void setX(size_t x);

  /**
   * Set the y-coordinate of contact (along-track index).
   *
   * @param[in] y Along-track index of contact.
   */
  void setY(size_t y);

  /**
   * Set the coordinates of contact.
   *
   * @param[in] x Cross-track index of contact.
   * @param[in] y Along-track index of contact.
   */
  void setLocation(size_t x, size_t y);

  /**
   * Returns filename of input data.
   */
  const char* filename() const;

  /**
   * Set filename of input data.
   *
   * @param[in] filename Name of file from which input data was read.
   */
  void setFilename(const char* filename);

  /**
   * Set filename of input data.
   *
   * @param[in] filename Name of file from which input data was read.
   */
  void setFilename(const std::string& filename);

  /**
   * Returns side of vehicle from which contact originates.
   */
  const char* side() const;

  /**
   * Set side of vehicle from which contact originates.
   *
   * @param[in] side Vehicle side ("PORT"|"STBD").
   */
  void setSide(const char* side);

  /**
   * Set side of vehicle from which contact originates.
   *
   * @param[in] side Vehicle side ("PORT"|"STBD").
   */
  void setSide(const std::string& side);

  /**
   * Returns name of normalizer module.
   */
  const char* normalizer() const;

  /**
   * Set name of normalizer module.
   *
   * @param[in] normalizer Normalizer module name.
   */
  void setNormalizer(const char* normalizer);

  /**
   * Set name of normalizer module.
   *
   * @param[in] normalizer Normalizer module name.
   */
  void setNormalizer(const std::string& normalizer);

  /**
   * Returns name of detector module.
   */
  const char* detector() const;

  /**
   * Set name of detector module.
   *
   * @param[in] detector Detector module name.
   */
  void setDetector(const char* detector);

  /**
   * Set name of detector module.
   *
   * @param[in] detector Detector module name.
   */
  void setDetector(const std::string& detector);

  /**
   * Returns names of feature modules (and detector modules that produce
   * features).
   */
  const std::vector<std::string>& featureset() const;

  /**
   * Set names of feature modules (and detector modules that produce
   * features).
   *
   * @param[in] featureset Feature module names.
   */
  void setFeatureset(const std::vector<std::string>& featureset);

  /**
   * Returns sizes of features for contact.
   */
  const std::vector<size_t>& featureSize() const;

  /**
   * Returns size of feature.
   *
   * @param name Feature name.
   * @return size_t Size of requested feature.
   */
  size_t featureSize(const char *name) const;

  /**
   * Sets size for each featureset in contact. The featureset must be set before
   * the feature size can be set. Returns 0 on success.
   *
   * @param feature_size Size of contact featuresets.
   * @return int
   */
  int setFeatureSize(const std::vector<size_t> &feature_size);

  /**
   * Returns name of classifier module.
   */
  const char* classifier() const;

  /**
   * Set name of classifier module.
   *
   * @param[in] classifier Classifier module name.
   */
  void setClassifier(const char* classifier);

  /**
   * Set name of classifier module.
   *
   * @param[in] classifier Classifier module name.
   */
  void setClassifier(const std::string& classifier);

  /**
   * Returns name of contact correlation module.
   */
  const char* contcorr() const;

  /**
   * Set name of contact correlation module.
   *
   * @param[in] contcorr Contact correlation module name.
   */
  void setContcorr(const char* contcorr);

  /**
   * Set name of contact correlation module.
   *
   * @param[in] contcorr Contact correlation module name.
   */
  void setContcorr(const std::string& contcorr);

  /**
   * Returns whether the contact is a ground truth target.
   */
  bool gt() const;

  /**
   * Sets whether the contact is a ground truth target.
   *
   * @param[in] gt True if the contact is a ground truth target.
   */
  void setGT(bool gt);

  /**
   * Returns the contact type id, where -99 = unknown.
   */
  int type() const;

  /**
   * Set the contact type id, where -99 = unknown.
   *
   * @param[in] type Contact type id.
   */
  void setType(int type);

  /**
   * Returns contact classification.  This is typically 0 or 1, but may be
   * higher depending on the classifier.
   */
  int cls() const;

  /**
   * Set the contact classification.
   *
   * @param[in] cls Contact classification.
   */
  void setCls(int cls);

  /**
   * Returns classifier confidence score (probability that classification of
   * contact is correct).
   */
  float classconf() const;

  /**
   * Set the classifier confidence score.
   *
   * @param[in] classconf Probability that classification of contact is
   * correct (0 < @p classconf < 1).
   */
  void setClassconf(float classconf);

  /**
   * Returns the vector of features used to classify the contact.
   */
  const std::vector<double>& features() const;

  /**
   * Returns the vector of features used to classify the contact.
   */
  std::vector<double>& features();

  std::vector<double> feature(const char*) const;

  /**
   * Set the vector of features used to classify the contact.
   *
   * @param[in] sz Length of feature array.
   * @param[in] features Array of features.
   */
  void setFeatures(size_t sz, double* features);

  /**
   * Add a feature to the contact.
   *
   * @param[in] name Feature module name.
   * @param[in] features Feature vector associated with the feature module.
   *
   * @return Returns 0 on success.
   */
  int addFeature(const char* name, const std::vector<double>& features);

  /**
   * Update feature in the contact.
   *
   * @param[in] name Feature module name.
   * @param[in] features Feature vector associated with the feature module.
   *
   * @return Returns 0 on success.
   */
  int updateFeature(const char* name, const std::vector<double>& features);

  /**
   * Returns the operator feedback structure.
   *
   * @warning This is currently only for %MATS compatiblility. Do not use
   * unless you know what you are doing.
   */
  const MATS_opfeedback &opfeedback() const;

  /**
   * Returns a reference to the operator feedback structure.
   *
   * @warning This is currently only for %MATS compatiblility. Do not use
   * unless you know what you are doing.
   */
  MATS_opfeedback& opfeedback();

  /**
   * Writes summary of MATS_contact to stdout.
   * This function only works if the MATS_DEBUG flag is set.
   */
  void display() const;

  /**
   * Returns the UUID of the contact.
   */
  const char* uuid() const;

  /**
   * Set the UUID of the contact.
   *
   * @param[in] uuid UUID string.
   */
  void setUUID(const std::string& uuid);

  /**
   * MATS_contact destructor
   */
  ~MATS_contact();

  /**
   * Copy an existing MATS_contact.
   *
   * @param[in] con MATS_contact to be copied.
   */
  void copy(const MATS_contact& con);

  /**
   * Assignment operator for MATS_contact.
   *
   * @param[in] con MATS_contact value to assign.
   */
  MATS_contact& operator=(const MATS_contact& con);

  #ifdef MATS_MEMORY
  inline void *operator new(size_t size) {
    return GlMemoryManager.allocate(sizeof(mats::MATS_contact));
  }

  inline void operator delete(void *object) {
    GlMemoryManager.free(object);
  }
  #endif

 private:
  MATS_contact_base* p_;
};


/**************************************************************************
 * Functions for working with MATS_contact structures
 *************************************************************************/

/**
 * Shallow copy of MATS Contact (uses assignment operator). This method is used
 * to support other language integration.
 *
 * @param[in] from MATS_contact to be copied.
 * @param[in] to Pointer to MATS_contact to be copied to.
 */
MATS_LIB void
mats_contact_shallow_copy(const MATS_contact &from, MATS_contact *to);


/**
 * Move @p source MATS_contact vector to the end of @p dest MATS_contact vector.
 *
 * @param[in,out] dest Destination MATS_contact vector.
 * @param[in,out] source Source MATS_contact vector (will be cleared upon
 * successful completion).
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
mats_contact_list_append(MATS_contact_list& dest, MATS_contact_list& source);


/**
 * Save a MATS_contact_list in an HDF5 file under the group name "contacts".
 *
 * @param[in] filename File to create.
 * @param[in] contacts List of contacts.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
mats_contact_save(const char* filename, const MATS_contact_list& contacts);


/**
 * Load contacts from an HDF5 file, from the group name "contacts".  A subset
 * of the contacts may be selected for loading.
 *
 * @param[in] filename File to read.
 * @param[in] indexVec Indices of the contacts to be loaded.  If empty, all
 * contacts will be loaded.
 * @param[out] contacts List of contacts.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
mats_contact_load(const char* filename, const std::vector<size_t>& indexVec,
    MATS_contact_list* contacts);


/**
 * Exchange the values of two MATS_contact objects.
 */
MATS_LIB void
mats_contact_swap(mats::MATS_contact& a, mats::MATS_contact& b);

}  // namespace mats

#endif  // SRC_MATS_CONTACT_H_
