/**
 * @file
 * @brief File contains the base MATS container class for data.
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
#ifndef SRC_MATS_DATA_H_
#define SRC_MATS_DATA_H_

#include <iostream>
#include "MATS_platform.h"


namespace mats {

/**
 * %MATS C precision types
 */
enum MATS_precision{matsUNKNOWN, matsUI, matsFLOAT, matsDOUBLE, matsUI8};


/**
 * %MATS C storage types (Column Major or Row Major)
 *
 * Number of rows = number of along-track samples.
 * Number of columns = number of cross-track samples.
 */
enum MATS_storage{matsCOL_MAJOR, matsROW_MAJOR};


/**
 * %MATS C data formats (data is real/complex data, or amplitude/phase)
 */
enum MATS_format{matsREAL_IMAG, matsAMP_PHASE};


/**
 * MATS_data structure is a generic 2-D data container class.
 */
class MATS_LIB MATS_data {
  friend MATS_LIB std::ostream&
  operator<<(std::ostream& strm, const mats::MATS_data& data);

  friend MATS_LIB int
  decimate(MATS_data& data, int dim, size_t rate, int mode);

 public:
  /**
   * MATS_data default constructor. Sets data storage to column major, data
   * format to Real/Imaginary, and precision to unknown.
   */
  MATS_data();

  /**
   * Constructs MATS_data with desired storage, precision and format.
   *
   * @param[in] storage Storage type.
   * @param[in] precision Data precision.
   * @param[in] format Data format.
   */
  MATS_data(MATS_storage storage, MATS_precision precision,
      MATS_format format);

  /**
   * MATS_data copy constructor.
   *
   * @param[in] indata MATS_data to be copied.
   */
  MATS_data(const MATS_data& indata);

  /**
   * Returns the precision of the MATS_data.
   */
  MATS_precision getPrecision() const;

  /**
   * Set the precision of the MATS_data.
   *
   * @param[in] precision Desired precision.
   *
   * @return Returns 0 on success.
   *
   * @warning This is not a reversible operation. Precision may be permanently
   * lost.
   */
  int setPrecision(MATS_precision precision);

  /**
   * Returns the current storage format of the data.
   */
  MATS_storage getStorage() const;

  /**
   * Sets the storage format of the data.  If data is already allocated and
   * the storage format is changed, the data undergoes a transpose.  If the
   * data is already in the desired storage format, no change occurs.
   *
   * @param[in] storage Desired data storage format.
   *
   * @return Returns 0 on success.
   *
   * @warning Calling this function can result in a transpose of the data,
   * which could take a considerable amount of time depending on data size.
   */
  int setStorage(MATS_storage storage);

  /**
   * Returns the current data format.
   */
  MATS_format getFormat() const;

  /**
   * Sets the data format.
   *
   * @param[in] format New desired format of data.
   *
   * @return Returns 0 on success.
   *
   * @warning Changing formats can result in some data precision lost.
   */
  int setFormat(MATS_format format);

  /**
   * Returns true if data has a complex component.
   */
  bool isComplex() const;

  /**
   * Returns true if the MATS_data is empty.
   */
  bool empty() const;

  /**
   * Returns the total number of data samples.
   */
  size_t length() const;

  /**
   * Returns number of along-track and/or cross-track data samples. A null
   * pointer indicates that the value should not be returned.
   *
   * @param[out] anum Number of along-track samples.
   * @param[out] cnum Number of cross-track samples.
   */
  void size(size_t* anum, size_t* cnum) const;

  /**
   * NOT IMPLEMENTED YET.
   *
   * Clears any generated precision data. Data pertaining to set precision is
   * retained.
   *
   * @return Returns 0 on success.
   */
  int clean();

  /**
   * Clears imported data from structure (all allocated memory is freed, and
   * sizes are set to zero).
   *
   * @return Returns 0 on success.
   */
  int clear();

  /**
   * Displays information about the MATS_data, such as size, resolution,
   * storage, format, and precision.
   * This function only works if the MATS_DEBUG flag is set.
   */
  void display() const;

  /**
   * Writes a section of the data to the specified output stream. The
   * displayed data will be in the range [anum1, anum2) and [cnum1, cnum2).
   *
   * @param[in] anum1 (Optional) Start along-track index (0-based).  Defaults
   * to 0.
   * @param[in] anum2 (Optional) End along-track index, plus one (0-based).
   * Defaults to number of along-track samples.
   * @param[in] cnum1 (Optional) Start cross-track index (0-based).  Defaults
   * to 0.
   * @param[in] cnum2 (Optional) End cross-track index, plus one (0-based).
   * Defaults to number of cross-track samples.
   * @param[in] strm (Optional) Output stream.  Defaults to standard output.
   */
  void displaySample(size_t anum1 = 0, size_t anum2 = 0, size_t cnum1 = 0,
      size_t cnum2 = 0, std::ostream& strm = std::cout) const;

  /**
   * Displays contents of MATS_data to stdout.
   * This function only works if the MATS_DEBUG flag is set.
   */
  void displayAll() const;

  /**
   * Gets data resolution in the along-track and cross-track directions.
   *
   * @param[out] ares Along-track resolution (meters).
   * @param[out] cres Cross-track resolution (meters).
   */
  template<class DT> void getResolution(DT& ares, DT& cres) const;

  /**
   * Set the data resolution for MATS_data.  No data alterations occur.
   *
   * @param[in] ares Along-track resolution (meters).
   * @param[in] cres Cross-track resolution (meters).
   */
  template<class DT> void setResolution(DT ares, DT cres);

  /**
   * Imports data. The data being imported is assumed to be in set storage and
   * format and is copied into internal memory. Any existing data is cleared
   * out before the import.
   *
   * @param[in] anum Number of along-track data samples being imported.
   * @param[in] cnum Number of cross-track data samples being imported.
   * @param[in] data1 Array of real/amplitude data samples to be imported.
   * @param[in] data2 (Optional) Array of imaginary/phase data samples to be
   * imported.
   *
   * @return Returns 0 on success.
   *
   * @warning The precision of the MATS_data will be changed to match that
   * of the imported data.
   */
  template<class DT> int
  loadData(size_t anum, size_t cnum, const DT* data1, const DT* data2 = NULL);

  /**
   * Allocate memory space for the specified data size in the set precision.
   * The data precision must be set before calling this method; it cannot be
   * unknown.  Any existing data is cleared out first.
   *
   * @param[in] anum Number of along-track data samples.
   * @param[in] cnum Number of cross-track data samples.
   * @param[in] complexData Whether the data has a complex component.
   *
   * @return Returns 0 on success.
   */
  int allocateData(size_t anum, size_t cnum, bool complexData);

  /**
   * Returns pointer to real data.
   *
   * Will return a null pointer if a pointer to a different precision than
   * the data is requested, or if the data is in the wrong format.
   */
  template<class DT> DT* getRealData();

  /**
   * Returns pointer to constant real data.
   *
   * Will return a null pointer if a pointer to a different precision than
   * the data is requested, or if the data is in the wrong format.
   */
  template<class DT> const DT* getRealData() const;

  /**
   * Returns pointer to amplitude data.
   *
   * Will return a null pointer if a pointer to a different precision than
   * the data is requested, or if the data is in the wrong format.
   */
  template<class DT> DT* getAmplitudeData();

  /**
   * Returns pointer to constant amplitude data.
   *
   * Will return a null pointer if a pointer to a different precision than
   * the data is requested, or if the data is in the wrong format.
   */
  template<class DT> const DT* getAmplitudeData() const;

  /**
   * Returns pointer to imaginary data.
   *
   * Will return a null pointer if a pointer to a different precision than
   * the data is requested, or if the data is in the wrong format.
   */
  template<class DT> DT* getImagData();

  /**
   * Returns pointer to constant imaginary data.
   *
   * Will return a null pointer if a pointer to a different precision than
   * the data is requested, or if the data is in the wrong format.
   */
  template<class DT> const DT* getImagData() const;

  /**
   * Returns pointer to phase data.
   *
   * Will return a null pointer if a pointer to a different precision than
   * the data is requested, or if the data is in the wrong format.
   */
  template<class DT> DT* getPhaseData();

  /**
   * Returns pointer to constant phase data.
   *
   * Will return a null pointer if a pointer to a different precision than
   * the data is requested, or if the data is in the wrong format.
   */
  template<class DT> const DT* getPhaseData() const;

  /**
   * Returns a pointer to the amplitude component of the data, or to the
   * real component if the data is not complex.  If the data is complex and
   * in real/imaginary format, the format is changed to amplitude/phase and
   * the amplitude component is returned.
   *
   * Will return a null pointer if a pointer to a different precision
   * than the data is requested.
   *
   * @warning This function could result in changing the format of the data.
   * Changing formats can result in some data precision lost.
   */
  template<class DT> DT* getRealOrAmpData();

  /**
   * Returns a pointer to the constant amplitude component of the data, or
   * to the constant real component if the data is not complex.  If the
   * data is complex and in real/imaginary format, a null pointer is
   * returned.
   *
   * Will return a null pointer if a pointer to a different precision
   * than the data is requested.
   */
  template<class DT> const DT* getRealOrAmpData() const;

  /**
   * Convert the data into an absolute value of itself.  Any remaining sign or
   * phase information is discarded.
   *
   * @return Returns 0 on success.
   *
   * @warning This is not a reversible operation.
   */
  int absValue();

  /**
   * Returns a data snippet.
   *
   * @param[in] x Cross-track index of snippet's center pixel.
   * @param[in] y Along-track index of snippet's center pixel.
   * @param[in] snipwidth Cross-track width of snippet in pixels.
   * @param[in] snipheight Along-track height of snippet in pixels.
   *
   * @return Returns a MATS_data containing the snippet. Parameters such as
   * resolution and format are retained from the original MATS_data.
   */
  MATS_data
  snippet(size_t x, size_t y, size_t snipwidth, size_t snipheight) const;

  /**
   * Assignment operator for MATS_data.
   *
   * @param[in] indata MATS_data value to assign.
   */
  MATS_data& operator=(const MATS_data& indata);

  /**
   * Copy an existing MATS_data.
   *
   * @param[in] indata MATS_data to be copied.
   */
  void copy(const mats::MATS_data& indata);

  /**
   * Clear out any existing data, and copy all parameters from another
   * MATS_data, but not the data itself.
   *
   * @param[in] indata MATS_data to be copied.
   */
  void blankCopy(const mats::MATS_data& indata);

  /**
   * Obtain constant pointer to the specified data component, regardless of its
   * format.
   *
   * Will return a null pointer if a pointer to a different precision
   * than the data is requested.
   *
   * @param[in] k 0 for real or amplitude component; 1 for imaginary or
   * phase component.
   */
  template<class DT> const DT* component(int k) const;

  /**
   * Obtain a pointer to the specified data component, regardless of its
   * format.
   *
   * Will return a null pointer if a pointer to a different precision
   * than the data is requested.
   *
   * @param[in] k 0 for real or amplitude component; 1 for imaginary or
   * phase component.
   */
  template<class DT> DT* component(int k);

  /**
   * MATS_data destructor. Frees allocated memory.
   */
  ~MATS_data();

 private:
  MATS_storage data_storage;
  MATS_precision data_precision;
  MATS_format data_format;

  size_t data_anum; /**< Number of along-track data samples. */
  size_t data_cnum; /**< Number of cross-track data samples. */

  double data_ares; /**< Along-track resolution of data. */
  double data_cres; /**< Cross-track resolution of data. */

  /* We are only supporting certain types with this container class, so
   * instead of using lots of void pointers we are just going to create all
   * the points and just use the ones we want to.
   */
  double *ddata1; /**< Double precision real or amplitude sensor data. */
  double *ddata2; /**< Double precision imaginary or phase sensor data. */
  float *fdata1; /**< Float precision real or amplitude sensor data. */
  float *fdata2; /**< Float precision imaginary or phase sensor data. */
  unsigned int *uidata1; /**< UI precision real or amplitude sensor data. */
  unsigned int *uidata2; /**< UI precision imaginary or phase sensor data. */

  uint8_t *ui8data1; /**< UI8 precision real or amplitude sensor data. */
  uint8_t *ui8data2; /**< UI8 precision imaginary or phase sensor data. */
};


#ifndef MATS_WINDOWS

/**
 * Writes entire MATS_data contents to the specified output stream.
 *
 * @param[in] strm Desired output stream.
 * @param[in] data The MATS_data to write to output stream.
 */
MATS_LIB std::ostream&
operator<<(std::ostream& strm, const mats::MATS_data& data);

#endif


/**
 * Perform decimation on 2-D data.
 *
 * @param[in,out] data  The data to be decimated.
 * @param[in]     dim   0 to decimate along-track; 1 to decimate cross-track.
 * @param[in]     rate  The decimation rate.  Must be positive.
 * @param[in]     mode  0 for average method, 1 for peak-pick method.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
decimate(MATS_data& data, int dim, size_t rate, int mode);


/**
 * Take a snippet of a MATS_data, and write the absolute value of it into a
 * data buffer of the desired precision. Snippet is taken over [a0, a1] and
 * [c0, c1]. Function handles complex numbers and changing of data precision.
 *
 * @note This function only supports column-major data at this time.
 *
 * @param[in] in The input data.
 * @param[in] a0 Starting along-track index.
 * @param[in] a1 Ending along-track index.
 * @param[in] c0 Starting cross-track index.
 * @param[in] c1 Ending cross-track index.
 * @param[out] data The output data, [ @p a1 - @p a0 + 1 x @p c1 - @p c0 + 1 ].
 *
 * @return Returns 0 on success.
 *
 * @warning Output @p data must be pre-allocated.
 */
template<class DT> MATS_LIB int
mats_data_abs_snippet(const MATS_data& in, size_t a0, size_t a1, size_t c0,
    size_t c1, DT* data);


/**
 * Write absolute value of MATS_data to a buffer of desired precision. Function
 * handles complex numbers and changing of data precision. Output buffer retains
 * the same storage type (column-major or row-major) as the input MATS_data.
 *
 * @param[in] in Data to perform action on.
 * @param[out] data Buffer to write abs to.
 *
 * @return Returns 0 on success.
 *
 * @warning Output @p data must be pre-allocated to at least the size of
 * the input data.
 */
template<class DT> MATS_LIB int
mats_data_abs(const MATS_data& in, DT* data);


/**
 * Take a snippet of a MATS_data, and write it into data buffer(s) of the
 * desired precision. Snippet is taken over [a0, a1] and [c0, c1].
 * Function handles changing of data precision. Output retains the
 * same format (real/imaginary or amplitude/phase) as the input MATS_data.
 * Each output buffer @p d1 and @p d2 will only be filled if a non-null
 * pointer is provided.
 *
 * @note This function only supports column-major data at this time.
 *
 * @param[in] in The input data.
 * @param[in] a0 Starting along-track index.
 * @param[in] a1 Ending along-track index.
 * @param[in] c0 Starting cross-track index.
 * @param[in] c1 Ending cross-track index.
 * @param[out] d1 The output data, real or amplitude component,
 * [ @p a1 - @p a0 + 1 x @p c1 - @p c0 + 1 ].
 * @param[out] d2 The output data, imaginary or phase component,
 * [ @p a1 - @p a0 + 1 x @p c1 - @p c0 + 1 ].
 *
 * @return Returns 0 on success.
 *
 * @warning Each output @p d1 and @p d2 must either be pre-allocated, or a
 * null pointer provided if the output is not needed.
 */
template<class DT> MATS_LIB int
mats_data_snippet(const MATS_data& in, size_t a0, size_t a1, size_t c0,
    size_t c1, DT* d1, DT* d2);


/**
 * Copies MATS_data into buffer(s) of desired precision. Function
 * handles complex numbers and changing of data precision. Output buffer retains
 * the same storage type (column-major or row-major) and the same
 * format (real/imaginary or amplitude/phase) as the input MATS_data.
 * Each output buffer @p d1 and @p d2 will only be filled if a non-null
 * pointer is provided.
 *
 * @param[in] in Data to perform action on.
 * @param[out] d1 Buffer to write real/abs component.
 * @param[out] d2 Buffer to write imag/phase component.
 *
 * @return Returns 0 on success.
 *
 * @warning Each output @p d1 and @p d2 must either be pre-allocated to at
 * least the size of the input data, or a
 * null pointer provided if the output is not needed.
 */
template<class DT> MATS_LIB int
mats_data_copy(const MATS_data& in, DT* d1, DT* d2);


/**
 * Save a MATS_data in an HDF5 file, under the group name "data".
 *
 * @param[in] filename File to create.
 * @param[in] data MATS_data to save.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
mats_data_save(const char* filename, const MATS_data& data);


/**
 * Load a MATS_data from an HDF5 file, from the group name "data".
 *
 * @param[in] filename File to read.
 * @param[out] data The loaded MATS_data.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
mats_data_load(const char* filename, MATS_data* data);

}  // namespace mats

#endif  // SRC_MATS_DATA_H_
