/**
 * @file
 * @brief File contains functions for reading/writing HDF5 files.
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
#ifndef SRC_MATS_HDF5_H_
#define SRC_MATS_HDF5_H_

#include <string>
#include <vector>
#include <typeinfo>

#include "MATS_core.h"
#include "MATS_platform.h"
#include "MATS_cfg.h"
#include "MATS_data.h"
#include "MATS_struct.h"
#include "MATS_contact.h"
#include "MATS_ecdata.h"
#include "MATS_input.h"


/** Define ID type for HDF5 to match HDF5's hid_t */
typedef int mats_hid_t;


/** Define status return type for HDF5 to match HDF5's herr_t */
typedef int mats_herr_t;


/** Define status return type for HDF5 to match HDF5's htri_t */
typedef int mats_htri_t;


/** Define file object size type for HDF5 to match HDF5's hsize_t */
typedef unsigned long long 	mats_hsize_t;


namespace mats {


/**
 * Obtain lock for HDF5 read/write.
 *
 * @warning Only use this function if you are obtaining a file ID for an HDF5
 * file, e.g., using mats_H5Fcreate() or mats_H5Fopen(). Many convenience
 * functions already use this lock.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int mats_lock_hdf5();


/**
 * Release lock for HDF5 read/write.
 *
 * @return Return 0 on success.
 */
MATS_LIB int mats_unlock_hdf5();


/*******************************************************************************
 HDF5 Pass-through Functions
 ******************************************************************************/


/**
 * Creates an HDF5 file.
 *
 * Calls the H5Fcreate() function in the HDF5 library using H5P_DEFAULT for
 * file creation properties and file access properties.
 *
 * @param[in] filename Name of the file to access.
 * @param[in] overwrite (Optional) True to overwrite file if it already exists;
 * false to fail if file already exists. Default is false.
 *
 * @return Returns a file ID if successful; otherwise returns a negative value.
 *
 * @warning For thread safety, use the mats_lock_hdf5() and mats_unlock_hdf5()
 * functions before creating an HDF5 file and after closing the file,
 * respectively. Also, the lock should be released if creating the file fails.
 */
MATS_LIB mats_hid_t mats_H5Fcreate(const char* filename,
    bool overwrite = false);


/**
 * Opens an existing HDF5 file.
 *
 * Calls the H5Fopen() function in the HDF5 library using H5P_DEFAULT for file
 * access properties.
 *
 * @param[in] filename Name of the file to be opened.
 * @param[in] rw (Optional) True for read-write access; false for read-only
 * access. Default is false.
 *
 * @return Returns a file ID if successful; otherwise returns a negative value.
 *
 * @warning For thread safety, use the mats_lock_hdf5() and mats_unlock_hdf5()
 * functions before opening an HDF5 file and after closing the file,
 * respectively. Also, the lock should be released if opening the file fails.
 */
MATS_LIB mats_hid_t mats_H5Fopen(const char* filename, bool rw = false);


/**
 * Terminates access to an HDF5 file.
 *
 * Calls the H5Fclose() function in the HDF5 library.
 *
 * @param[in] fid Identifier of a file to terminate access to.
 *
 * @return Returns a non-negative value if successful; otherwise returns a
 * negative value.
 */
MATS_LIB mats_herr_t mats_H5Fclose(mats_hid_t fid);


/**
 * Determine whether a link with the specified name exists in a group.
 *
 * Calls the H5Lexists() function in the HDF5 library using H5P_DEFAULT for
 * link access properties.
 *
 * @param[in] root Identifier of the file or group to query.
 * @param[in] name The name of the link to check.
 *
 * @return Returns a positive value if the link exists. Returns 0 if the link
 * does not exist. Returns a negative value if the function fails.
 */
MATS_LIB mats_htri_t mats_H5Lexists(mats_hid_t root, const char* name);


/**
 * Creates a group.
 *
 * Calls the H5Gcreate() function in the HDF5 library using H5P_DEFAULT for
 * group access properties.
 *
 * @param[in] root File or group identifier specifying the location of the
 * group to be created.
 * @param[in] name Name of the group to create.
 *
 * @return Returns a group identifier if successful; otherwise returns a
 * negative value.
 */
MATS_LIB mats_hid_t mats_H5Gcreate(mats_hid_t root, const char* name);


/**
 * Opens an existing group.
 *
 * Calls the H5Gopen() function in the HDF5 library using H5P_DEFAULT for
 * group access properties.
 *
 * @param[in] root File or group identifier specifying the location of the
 * group to be opened.
 * @param[in] name Name of the group to open.
 *
 * @return Returns a group identifier if successful; otherwise returns a
 * negative value.
 */
MATS_LIB mats_hid_t mats_H5Gopen(mats_hid_t root, const char* name);


/**
 * Closes the specified group.
 *
 * Calls the H5Gclose() function in the HDF5 library.
 *
 * @param[in] gid Group identifier to release.
 *
 * @return Returns a non-negative value if successful; otherwise returns a
 * negative value.
 */
MATS_LIB mats_herr_t mats_H5Gclose(mats_hid_t gid);


/*******************************************************************************
 HDF5 Utility Routines
 ******************************************************************************/

/**
 * Return the HDF5 type corresponding to a typeid.
 *
 * @param[in] in Type info.
 *
 * @return Returns the HDF5 type enum corresponding to the input type.
 */
MATS_LIB mats_hid_t
h5_type(const std::type_info& in);


/**
 * Return the MATS_precision corresponding to the type of a dataset.
 *
 * @param[in] root A valid location ID of file or group containing the dataset.
 * @param[in] name Name of the dataset.
 *
 * @return Returns the data type on success. Returns matsUNKNOWN on failure.
 */
MATS_LIB MATS_precision
h5_get_data_type(mats_hid_t root, const char* name);


/**
 * Return the size in bytes of a dataset's type.  This is usually used to
 * get the string length of a string dataset.  (In HDF5, a string dataset
 * has dimension 1, but the string length is part of its datatype.)
 *
 * @param[in] root A valid location ID of file or group containing the dataset.
 * @param[in] name Name of the dataset.
 *
 * @return Returns the string length / type size on success. Returns 0 on
 * failure.
 */
MATS_LIB size_t
h5_get_string_length(mats_hid_t root, const char* name);


/**
 * Return the dimensions of a dataset, in the original row-major order.  (Note
 * that %MATS uses column-major by convention.)
 *
 * @param[in] root A valid location ID of file or group containing the dataset.
 * @param[in] name Name of the dataset.
 *
 * @return Returns the dataset dimensions on success. Returns an empty vector
 * on failure.
 */
MATS_LIB std::vector<mats_hsize_t>
h5_get_data_dims(mats_hid_t root, const char* name);


/**
 * Return the total number of elements of a dataset.
 *
 * @param[in] root A valid location ID of file or group containing the dataset.
 * @param[in] name Name of the dataset.
 *
 * @return Returns the total number of elements on success. Returns 0 on
 * failure.
 */
MATS_LIB size_t
h5_get_data_length(mats_hid_t root, const char* name);


/*******************************************************************************
 HDF5 Attribute Routines
 ******************************************************************************/

/**
 * Add a fixed-length string attribute to an HDF5 file or object.
 *
 * @param[in] root A valid location ID to receive the attribute.
 * @param[in] name Name of the attribute.
 * @param[in] data The attribute string.
 *
 * @return Returns 0 on success.  Also returns 0 if @p data is empty, since
 * there is nothing to write.
 */
MATS_LIB int
h5a_create_string(mats_hid_t root, const char* name, const char* data);


/**
 * Read a fixed-length string attribute from an HDF5 file or object.
 *
 * @param[in] root A valid location ID containing the attribute.
 * @param[in] name Name of the attribute.
 *
 * @return Returns the attribute string on success. Returns an empty string on
 * failure.
 */
MATS_LIB std::string
h5a_get_string(mats_hid_t root, const char* name);


/*******************************************************************************
 HDF5 General Dataset Routines
 ******************************************************************************/

/**
 * Add a fixed-length string dataset to a file or group.
 *
 * @param[in] root A valid location ID of file or group to receive the dataset.
 * @param[in] name Name of the dataset.
 * @param[in] data Value to write.
 *
 * @return Returns 0 on success.  Also returns 0 if @p data is empty, since
 * there is nothing to write.
 */
MATS_LIB int
h5_create_string(mats_hid_t root, const char* name, const char* data);


/**
 * Read a fixed-length string dataset from a file or group.
 *
 * @param[in] root A valid location ID of file or group containing the dataset.
 * @param[in] name Name of the dataset.
 *
 * @return Returns the dataset string on success. Returns an empty string on
 * failure.
 */
MATS_LIB std::string
h5_get_string(mats_hid_t root, const char* name);


/**
 * Add a vector of variable-length strings dataset to a file or group.
 *
 * @param[in] root A valid location ID of file or group to receive the dataset.
 * @param[in] name Name of the dataset.
 * @param[in] data Value to write.
 *
 * @return Returns 0 on success.  Also returns 0 if @p data is empty, since
 * there is nothing to write.
 */
MATS_LIB int
h5_create_vlstring_vector(mats_hid_t root, const char* name,
    const std::vector<std::string>& data);


/**
 * Read a vector of variable-length strings dataset from a file or group.
 *
 * @param[in] root A valid location ID of file or group containing the dataset.
 * @param[in] name Name of the dataset.
 * @param[out] data Retrieved value.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
h5_get_vlstring_vector(mats_hid_t root, const char* name,
    std::vector<std::string>* data);


/**
 * Add a single numeric value to a file or group. The value may be one of the
 * following types: bool, signed char, char, int, unsigned int, size_t, float,
 * double.
 *
 * @param[in] root A valid location ID of file or group to receive the dataset.
 * @param[in] name Name of the dataset.
 * @param[in] data Value to write.
 *
 * @return Returns 0 on success.
 */
template<class DT> MATS_LIB int
h5_create_value(mats_hid_t root, const char* name, DT data);


/**
 * Boolean template specialization. Writes the value as an integer type.
 *
 * @param[in] root A valid location ID of file or group to receive the dataset.
 * @param[in] name Name of the dataset.
 * @param[in] data Value to write.
 *
 * @return Returns 0 on success.
 */
template<> MATS_LIB int
h5_create_value<bool>(mats_hid_t root, const char* name, bool data);


/**
 * Update a single numeric value in a file or group. The value may be one of
 * the following types: bool, signed char, char, int, unsigned int, size_t,
 * float, double.
 *
 * @param[in] root A valid location ID of file or group containing the dataset.
 * @param[in] name Name of the dataset.
 * @param[in] data New data value.
 *
 * @return Returns 0 on success.
 */
template<class DT> MATS_LIB int
h5_update_value(mats_hid_t root, const char* name, DT data);


/**
 * Boolean template specialization. Writes the value as an integer type.
 *
 * @param[in] root A valid location ID of file or group containing the dataset.
 * @param[in] name Name of the dataset.
 * @param[in] data New data value.
 *
 * @return Returns 0 on success.
 */
template<> MATS_LIB int
h5_update_value<bool>(mats_hid_t root, const char* name, bool data);


/**
 * Read a single numeric value from a file or group. The value may be one of
 * the following types: bool, signed char, char, int, unsigned int, size_t,
 * float, double.
 *
 * @param[in] root A valid location ID of file or group containing the dataset.
 * @param[in] name Name of the dataset.
 * @param[out] data Retrieved value.
 *
 * @return Returns 0 on success.
 */
template<class DT> MATS_LIB int
h5_get_value(mats_hid_t root, const char* name, DT* data);


/**
 * Boolean template specialization. Reads the value as an integer type.
 *
 * @param[in] root A valid location ID of file or group containing the dataset.
 * @param[in] name Name of the dataset.
 * @param[out] data Retrieved value.
 *
 * @return Returns 0 on success.
 */
template<> MATS_LIB int
h5_get_value<bool>(mats_hid_t root, const char* name, bool* data);


/**
 * Add an array with the specified dimensions to a file or group.  (The
 * dimensions should be specified for column-major storage.  They will be
 * reversed when writing to HDF5, which uses row-major storage.) The array may
 * be one of the following types: bool, signed char, char, int, unsigned int,
 * size_t, float, double.
 *
 * To add a vector, make @p dims size 1 and set dims[0] to the vector length.
 *
 * @param[in] root A valid location ID of file or group to receive the dataset.
 * @param[in] name Name of the dataset.
 * @param[in] dims Array dimensions in column-major order.
 * @param[in] data Pointer to the data array.
 *
 * @return Returns 0 on success.  Also returns 0 if @p data is empty, since
 * there is nothing to write.
 */
template<class DT> MATS_LIB int
h5_create_array(mats_hid_t root, const char* name,
    const std::vector<size_t>& dims, const DT* data);


/**
 * Boolean template specialization. Writes the array as an integer type.
 *
 * @param[in] root A valid location ID of file or group to receive the dataset.
 * @param[in] name Name of the dataset.
 * @param[in] dims Array dimensions in column-major order.
 * @param[in] data Pointer to the data array.
 *
 * @return Returns 0 on success.  Also returns 0 if @p data is empty, since
 * there is nothing to write.
 */
template<> MATS_LIB int
h5_create_array<bool>(mats_hid_t root, const char* name,
    const std::vector<size_t>& dims, const bool* data);


/**
 * Add an array with the specified dimensions to a file or group.  (The
 * dimensions should be specified for column-major storage.  They will be
 * reversed when writing to HDF5, which uses row-major storage.)
 *
 * @param[in] root A valid location ID of file or group to receive the dataset.
 * @param[in] name Name of the dataset.
 * @param[in] dims Array dimensions in column-major order.
 * @param[in] data data vector.
 *
 * @return Returns 0 on success.  Also returns 0 if @p data is empty, since
 * there is nothing to write.
 */
template<class DT> MATS_LIB int
h5_create_array(mats_hid_t root, const char* name,
    const std::vector<size_t>& dims, const std::vector<DT>& data);


/**
 * Boolean template specialization. Writes the array as an integer type.
 *
 * @param[in] root A valid location ID of file or group to receive the dataset.
 * @param[in] name Name of the dataset.
 * @param[in] dims Array dimensions in column-major order.
 * @param[in] data Pointer to the data array.
 *
 * @return Returns 0 on success.  Also returns 0 if @p data is empty, since
 * there is nothing to write.
 */
template<> MATS_LIB int
h5_create_array<bool>(mats_hid_t root, const char* name,
    const std::vector<size_t>& dims, const std::vector<bool>& data);


/**
 * Update an array dataset in a file or group.  The size of the updated
 * array must match the size of the existing dataset.  The array may be
 * one of the following types: bool, signed char, char, int, unsigned int,
 * size_t, float, double.
 *
 * @param[in] root A valid location ID of file or group containing the dataset.
 * @param[in] name Name of the dataset.
 * @param[in] N Size of the data array.
 * @param[in] data Pointer to the new data array.
 *
 * @return Returns 0 on success.
 */
template<class DT> MATS_LIB int
h5_update_array(mats_hid_t root, const char* name, size_t N, const DT* data);


/**
 * Boolean template specialization. Writes the array as an integer type.
 *
 * @param[in] root A valid location ID of file or group containing the dataset.
 * @param[in] name Name of the dataset.
 * @param[in] N Size of the data array.
 * @param[in] data Pointer to the new data array.
 *
 * @return Returns 0 on success.
 */
template<> MATS_LIB int
h5_update_array<bool>(mats_hid_t root, const char* name, size_t N,
    const bool* data);


/**
 * Read a dataset from a file or group into a pre-allocated array.  The
 * size of the array must match the size of the dataset.  The
 * array may be one of the following types: bool, signed char, char, int,
 * unsigned int, size_t, float, double.
 *
 * @param[in] root A valid location ID of file or group containing the dataset.
 * @param[in] name Name of the dataset.
 * @param[in] N Size of the pre-allocated data array.
 * @param[out] data Pointer to data array.
 *
 * @return Returns 0 on success.
 * @warning In case of an error, the array is left unchanged.
 */
template<class DT> MATS_LIB int
h5_get_array(mats_hid_t root, const char* name, size_t N, DT* data);


/**
 * Boolean template specialization. Reads the array as an integer type.
 *
 * @param[in] root A valid location ID of file or group containing the dataset.
 * @param[in] name Name of the dataset.
 * @param[in] N Size of the pre-allocated data array.
 * @param[out] data Pointer to data array.
 *
 * @return Returns 0 on success.
 * @warning In case of an error, the array is left unchanged.
 */
template<> MATS_LIB int
h5_get_array<bool>(mats_hid_t root, const char* name, size_t N, bool* data);


/**
 * Read a dataset from a file or group into a vector.  The vector may be one of
 * the following types: bool, signed char, char, int, unsigned int, size_t,
 * float, double.
 *
 * Optionally, the dataset dimensions may also be retrieved in
 * column-major order.  (The dimensions are reversed from those stored in
 * HDF5, which uses row-major order.)
 *
 * @param[in] root A valid location ID of file or group containing the dataset.
 * @param[in] name Name of the dataset.
 * @param[out] data Output data vector.
 * @param[out] dims (Optional) Array dimensions in column-major order.
 *
 * @return Returns 0 on success.
 */
template<class DT> MATS_LIB int
h5_get_array(mats_hid_t root, const char* name, std::vector<DT>* data,
    std::vector<size_t>* dims = NULL);


/**
 * Boolean template specialization. Reads the array as an integer type.
 *
 * @param[in] root A valid location ID of file or group containing the dataset.
 * @param[in] name Name of the dataset.
 * @param[out] data Output data vector.
 * @param[out] dims (Optional) Array dimensions in column-major order.
 *
 * @return Returns 0 on success.
 */
template<> MATS_LIB int
h5_get_array<bool>(mats_hid_t root, const char* name, std::vector<bool>* data,
    std::vector<size_t>* dims);


/*******************************************************************************
 HDF5 MATS Dataset Routines
 ******************************************************************************/

/**
 * Add an ATR_ROC to a file or group.
 *
 * The new group will be labeled with a "type" attribute of "roc".
 *
 * @param[in] root A valid location ID of file or group to receive the data.
 * @param[in] name Name of the ATR_ROC group.
 * @param[in] data Data to write.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
h5_create_atr_roc(mats_hid_t root, const char* name, const ATR_ROC& data);


/**
 * Read an ATR_ROC from a file or group.
 *
 * @param[in] root A valid location ID of file or group containing the data.
 * @param[in] name Name of the ATR_ROC group.
 * @param[out] data Retrieved data.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
h5_get_atr_roc(mats_hid_t root, const char* name, ATR_ROC* data);


/**
 * Add a MATS_struct to a file or group.
 *
 * The new group will be labeled with a "type" attribute of "struct".  Groups
 * for individual fields will be labeled with a "type" attribute based on the
 * mats::field_type_name() of the field's type.
 *
 * If a field is type MATS_cell or MATS_struct, the field is assumed to contain
 * only one cell array or struct.  If a field is type char, the field is
 * assumed to contain a single C-string.  For numeric fields, the stored field
 * dimensions are used.
 *
 * @param[in] root A valid location ID of file or group to receive the data.
 * @param[in] name Name of the MATS_struct group.
 * @param[in] data Data to write.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
h5_create_mats_struct(mats_hid_t root, const char* name,
    const MATS_struct& data);


/**
 * Read a MATS_struct from a file or group.
 *
 * If a field is type MATS_cell or MATS_struct, the field is assumed to contain
 * only one cell array or struct.  If a field is type char, the field is
 * assumed to contain a single C-string.  For numeric fields, the stored field
 * dimensions are used.
 *
 * @param[in] root A valid location ID of file or group containing the data.
 * @param[in] name Name of the MATS_struct group.
 * @param[out] data Retrieved data.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
h5_get_mats_struct(mats_hid_t root, const char* name, MATS_struct* data);


/**
 * Add a MATS_data to a file or group.
 *
 * The new group will be labeled with a "type" attribute of "data".
 *
 * @param[in] root A valid location ID of file or group to receive the data.
 * @param[in] name Name of the MATS_data group.
 * @param[in] data Data to write.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
h5_create_mats_data(mats_hid_t root, const char* name, const MATS_data& data);


/**
 * Read a MATS_data from a file or group.
 *
 * @param[in] root A valid location ID of file or group containing the data.
 * @param[in] name Name of the MATS_data group.
 * @param[out] data Retrieved data.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
h5_get_mats_data(mats_hid_t root, const char* name, MATS_data* data);


/**
 * Add a MATS_input to a file or group.
 *
 * The new group will be labeled with a "type" attribute of "input".
 *
 * @param[in] root A valid location ID of file or group to receive the data.
 * @param[in] name Name of the MATS_input group.
 * @param[in] data Data to write.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
h5_create_mats_input(mats_hid_t root, const char* name, const MATS_input& data);


/**
 * Read a MATS_input from a file or group.
 *
 * @param[in] root A valid location ID of file or group containing the data.
 * @param[in] name Name of the MATS_input group.
 * @param[out] data Retrieved data.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
h5_get_mats_input(mats_hid_t root, const char* name, MATS_input* data);


/**
 * Add a MATS_cell (cell array) to a file or group.
 *
 * The new group will be labeled with a "type" attribute of "cell".  Groups
 * for individual cells will be labeled with a "type" attribute based on the
 * mats::field_type_name() of the cell's type.
 *
 * If a cell is type MATS_cell or MATS_struct, the cell is assumed to contain
 * only one cell array or struct.  If a cell is type char, the cell is
 * assumed to contain a single C-string.  For numeric cells, the stored cell
 * dimensions are used.
 *
 * @param[in] root A valid location ID of file or group to receive the data.
 * @param[in] name Name of the MATS_cell group.
 * @param[in] data Data to write.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
h5_create_mats_cell(mats_hid_t root, const char* name, const MATS_cell& data);


/**
 * Read a MATS_cell (cell array) from a file or group.
 *
 * If a cell is type MATS_cell or MATS_struct, the cell is assumed to contain
 * only one cell array or struct.  If a cell is type char, the cell is
 * assumed to contain a single C-string.  For numeric cells, the stored cell
 * dimensions are used.
 *
 * @param[in] root A valid location ID of file or group containing the data.
 * @param[in] name Name of the MATS_cell group.
 * @param[out] data Retrieved data.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
h5_get_mats_cell(mats_hid_t root, const char* name, MATS_cell* data);


/**
 * Add a MATS_contact to a file or group.
 *
 * The new group will be labeled with a "type" attribute of "contact".
 *
 * @param[in] root A valid location ID of file or group to receive the data.
 * @param[in] name Name of the MATS_contact group.
 * @param[in] data Data to write.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
h5_create_mats_contact(mats_hid_t root, const char* name,
    const MATS_contact& data);


/**
 * Update an existing MATS_contact in a file or group. The new contact must
 * have the same UUID as the existing contact.
 *
 * The following fields can be updated: id, x, y, gt, type, cls, classconf,
 * features, opfeedback.
 *
 * @param[in] root A valid location ID of file or group containing the data.
 * @param[in] name Name of the MATS_contact group.
 * @param[in] data New data to write.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
h5_update_mats_contact(mats_hid_t root, const char* name,
    const MATS_contact& data);


/**
 * Read a MATS_contact from a file or group.
 *
 * @param[in] root A valid location ID of file or group containing the data.
 * @param[in] name Name of the MATS_contact group.
 * @param[out] data Retrieved data.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
h5_get_mats_contact(mats_hid_t root, const char* name, MATS_contact* data);


/**
 * Add a MATS_ecdata to a file or group.
 *
 * The new group will be labeled with a "type" attribute of "ecdata".
 *
 * @param[in] root A valid location ID of file or group to receive the data.
 * @param[in] name Name of the MATS_ecdata group.
 * @param[in] data Data to write.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
h5_create_mats_ecdata(mats_hid_t root, const char* name,
    const MATS_ecdata& data);


/**
 * Read a MATS_ecdata from a file or group.
 *
 * @param[in] root A valid location ID of file or group containing the data.
 * @param[in] name Name of the MATS_ecdata group.
 * @param[out] data Retrieved data.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
h5_get_mats_ecdata(mats_hid_t root, const char* name, MATS_ecdata* data);


/**
 * Add a MATS_contact_list to a file or group.
 *
 * The new group will be labeled with a "type" attribute of "contact_list".
 *
 * @param[in] root A valid location ID of file or group to receive the data.
 * @param[in] name Name of the MATS_contact_list group.
 * @param[in] data Data to write.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
h5_create_mats_contact_list(mats_hid_t root, const char* name,
    const MATS_contact_list& data);


/**
 * Update an existing MATS_contact_list in a file or group.
 *
 * @param[in] root A valid location ID of file or group containing the data.
 * @param[in] name Name of the MATS_contact_list group.
 * @param[in] data New data to write.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
h5_update_mats_contact_list(mats_hid_t root, const char* name,
    const MATS_contact_list& data);


/**
 * Read a MATS_contact_list from a file or group.
 *
 * @param[in] root A valid location ID of file or group containing the data.
 * @param[in] name Name of the MATS_contact_list group.
 * @param[out] data Retrieved data.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
h5_get_mats_contact_list(mats_hid_t root, const char* name,
    MATS_contact_list* data);


/**
 * Add a MATS_ecdata_list to a file or group.
 *
 * The new group will be labeled with a "type" attribute of "ecdata_list".
 *
 * @param[in] root A valid location ID of file or group to receive the data.
 * @param[in] name Name of the MATS_ecdata_list group.
 * @param[in] data Data to write.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
h5_create_mats_ecdata_list(mats_hid_t root, const char* name,
    const MATS_ecdata_list& data);


/**
 * Read a MATS_ecdata_list from a file or group.
 *
 * @param[in] root A valid location ID of file or group containing the data.
 * @param[in] name Name of the MATS_ecdata_list group.
 * @param[out] data Retrieved data.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
h5_get_mats_ecdata_list(mats_hid_t root, const char* name,
    MATS_ecdata_list* data);


/**
 * Add a MATS_groundtruth vector to a file or group.
 *
 * If the groundtruth vector group already exists but is empty, the groundtruth
 * will be added in the existing group.
 *
 * The new group will be labeled with a "type" attribute of "groundtruth".
 *
 * @param[in] root A valid location ID of file or group to receive the data.
 * @param[in] name Name of the MATS_groundtruth vector group.
 * @param[in] data Data to write.
 *
 * @return Returns 0 on success.
 * @warning An HDF5 groundtruth vector does not include the input filename and
 * side.
 */
MATS_LIB int
h5_create_mats_groundtruth_vector(mats_hid_t root, const char* name,
    const std::vector<MATS_groundtruth>& data);


/**
 * Update an existing MATS_groundtruth vector in a file or group.
 *
 * @param[in] root A valid location ID of file or group containing the data.
 * @param[in] name Name of the MATS_groundtruth vector group.
 * @param[in] data New data to write.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
h5_update_mats_groundtruth_vector(mats_hid_t root, const char* name,
    const std::vector<MATS_groundtruth>& data);


/**
 * Move a MATS_groundtruth vector to a new location within the same file
 * or group.
 *
 * The new group will be labeled with a "type" attribute of "groundtruth".
 *
 * A "date" field will be added with the current date/time.
 *
 * @param[in] root A valid location ID of file or group containing the data.
 * @param[in] source Name/location of the MATS_groundtruth vector group.
 * @param[in] dest Name/location to move to.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
h5_move_mats_groundtruth_vector(mats_hid_t root, const char* source,
    const char* dest);


/**
 * Read a MATS_groundtruth vector from a file or group.
 *
 * @param[in] root A valid location ID of file or group containing the data.
 * @param[in] name Name of the MATS_groundtruth vector group.
 * @param[out] data Retrieved data.
 *
 * @return Returns 0 on success.
 * @warning An HDF5 groundtruth vector does not include the input filename and
 * side.
 */
MATS_LIB int
h5_get_mats_groundtruth_vector(mats_hid_t root, const char* name,
    std::vector<MATS_groundtruth>* data);


/**
 * Add a MATS_perf to a file or group.
 *
 * @param[in] root A valid location ID of file or group to receive the data.
 * @param[in] name Name of the MATS_perf group.
 * @param[in] data Data to write.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
h5_create_mats_perf(mats_hid_t root, const char* name, const MATS_perf& data);


/**
 * Read a MATS_perf from a file or group.
 *
 * @param[in] root A valid location ID of file or group containing the data.
 * @param[in] name Name of the MATS_perf group.
 * @param[out] data Retrieved data.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
h5_get_mats_perf(mats_hid_t root, const char* name, MATS_perf* data);


/**
 * Add a MATS_segment (list of chunk boundaries) to a file or group.
 *
 * @param[in] root A valid location ID of file or group to receive the data.
 * @param[in] name Name of the MATS_segment group.
 * @param[in] data Data to write.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
h5_create_mats_segment(mats_hid_t root, const char* name,
    const MATS_segment& data);


/**
 * Read a MATS_segment (list of chunk boundaries) from a file or group.
 *
 * @param[in] root A valid location ID of file or group containing the data.
 * @param[in] name Name of the MATS_segment group.
 * @param[out] data Retrieved data.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
h5_get_mats_segment(mats_hid_t root, const char* name, MATS_segment* data);


/**
 * Add a MATS_region to a file or group.
 *
 * @param[in] root A valid location ID of file or group to receive the data.
 * @param[in] name Name of the MATS_region group.
 * @param[in] data Data to write.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
h5_create_mats_region(mats_hid_t root, const char* name,
    const MATS_region& data);


/**
 * Read a MATS_region from a file or group.
 *
 * @param[in] root A valid location ID of file or group containing the data.
 * @param[in] name Name of the MATS_region group.
 * @param[out] data Retrieved data.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
h5_get_mats_region(mats_hid_t root, const char* name, MATS_region* data);


/**
 * Add a MATS_region vector to a file or group.
 *
 * @param[in] root A valid location ID of file or group to receive the data.
 * @param[in] name Name of the MATS_region vector group.
 * @param[in] data Data to write.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
h5_create_mats_region_vector(mats_hid_t root, const char* name,
    const std::vector<MATS_region>& data);


/**
 * Read a MATS_region vector from a file or group.
 *
 * @param[in] root A valid location ID of file or group containing the data.
 * @param[in] name Name of the MATS_region vector group.
 * @param[out] data Retrieved data.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
h5_get_mats_region_vector(mats_hid_t root, const char* name,
    std::vector<MATS_region>* data);

}  // namespace mats

#endif  // SRC_MATS_HDF5_H_
