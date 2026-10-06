/**
 * @file
 * @brief File contains the generic information storage classes MATS_struct
 * and MATS_cell.
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
#ifndef SRC_MATS_STRUCT_H_
#define SRC_MATS_STRUCT_H_

#include <string>
#include <vector>
#include <map>

#include "MATS_platform.h"
#include "MATS_data.h"
#include "MATS_uuid.h"


namespace mats {

class MATS_cell;
class MATS_struct;


/**
 * Enum describing the type of data contained in a field of a MATS_struct or a
 * cell of a MATS_cell.
 */
enum MATS_field_type {tEMPTY, tUNKNOWN, tCELL, tSTRUCT, tDOUBLE, tFLOAT, tINT,
    tUINT, tCHAR, tSIZE_T};


/**
 * MATS_fieldinfo is the general container used by MATS_struct and MATS_cell to
 * store data.
 */
struct MATS_fieldinfo {
  std::vector<size_t> dims; /**< Dimensions of @p data */
  MATS_field_type type; /**< Data type */
  void* data; /**< Pointer to data storage */
};


/**
 * Return a MATS_field_type based on the type name.  Possible input values are:
 * "cell", "struct", "char", "int", "unsigned int", "float", "double", "size_t",
 * "empty", "logical".  Any other input will return a value of tUNKNOWN.
 *
 * @param[in] type Name of the type.
 *
 * @return Returns the MATS_field_type associated with the type name.
 */
MATS_LIB MATS_field_type
field_type_id(const char* type);


/**
 * Return a type name based on the field type.  Possible return values are:
 * "cell", "struct", "char", "int", "unsigned int", "float", "double", "size_t",
 * "empty", "Unknown".
 *
 * @param[in] type The field type.
 *
 * @return Returns the type name.
 */
MATS_LIB std::string
field_type_name(mats::MATS_field_type type);


/**
 * Free the memory in a MATS_fieldinfo and reset it to empty.
 *
 * @param[in,out] data The MATS_fieldinfo to clear.
 */
MATS_LIB void
mats_fieldinfo_clear(MATS_fieldinfo& data);


/**
 * Set the members of a MATS_fieldinfo to the appropriate data type and
 * dimensions, and allocate the data array. If @p value is specified, copy
 * the data to the MATS_fieldinfo array.
 *
 * @param[out] info The MATS_fieldinfo to set.
 * @param[in] dims The dimensions of the data array.
 * @param[in] value Data to copy. If none, use NULL.
 *
 * @warning This function does not check for existing data in @p info. If
 * @p info already contains data, use mats_fieldinfo_clear() to free its
 * memory before calling this function.
 *
 * @warning If @p dims indicates a total array size of 0, no array will be
 * allocated. Instead, the data pointer will be set to NULL. (This warning
 * does not apply to the char template specialization.)
 */
template<class DT> MATS_LIB void
mats_fieldinfo_set(MATS_fieldinfo& info, const std::vector<size_t>& dims,
    const DT* value);


/**
 * Template specialization for char. An extra null character is added to the
 * end of the string so that it can be read as a C-string.
 *
 * If @p dims indicates an empty string (total size 0), the char array will
 * be allocated as size 1 and will contain the null character.
 *
 * @param[out] info The MATS_fieldinfo to set.
 * @param[in] dims The dimensions of the data array.
 * @param[in] value Data to copy. If none, use NULL.
 *
 * @warning If @p value is provided, the number of characters copied will be
 * the total size indicated by @p dims, regardless of whether @p value is a
 * null-terminated string of shorter length.  The array allocated for @p value
 * must be at least this big.
 */
template<> MATS_LIB void
mats_fieldinfo_set<char>(MATS_fieldinfo& info, const std::vector<size_t>& dims,
    const char* value);


/**
 * Returns the total size indicated by a dimension vector.
 *
 * @param[in] dims A dimension vector.
 *
 * @return Returns the product of all entries. If @p dims is empty, returns 0.
 */
MATS_LIB size_t totalSize(const std::vector<size_t>& dims);


/**
 * MATS_struct is a general name-based storage container built on the STL map
 * container. It is comprised of named fields that contain data arrays or
 * c-strings. Supported data types are int, unsigned int, float, double, size_t,
 * char, MATS_struct, and MATS_cell. All other data types will fail to link.
 *
 * This class is equivalent to a scalar structure.  There is no structure
 * array; for an array of MATS_struct objects, use a MATS_cell (cell array)
 * object.
 */
class MATS_LIB MATS_struct {
 public:
  friend MATS_LIB void swap(MATS_struct& a, MATS_struct& b);

  /**
   * Default constructor (creates empty MATS_struct).
   */
  MATS_struct();

  /**
   * Copy constructor (all data is copied from input MATS_struct).
   *
   * @param[in] in MATS_struct to be copied.
   */
  MATS_struct(const MATS_struct& in);

  /**
   * Removes a field.
   *
   * @param[in] field Name of field to be removed.
   */
  void remove(const char* field);

  /**
   * Returns the number of fields in the MATS_struct.
   */
  size_t size() const;

  /**
   * Returns the dimensions of a field.
   *
   * @param[in] name Name of field.
   *
   * @return Returns dimension vector of the field. If the field does
   * not exist, an empty vector is returned.
   */
  std::vector<size_t> size(const char* name) const;

  /**
   * Returns the type of data contained in field.
   *
   * @param[in] name Name of field.
   *
   * @return Returns the type value of the storage used to store the field.
   * If the field doesn't exist, returns tUNKNOWN.
   */
  MATS_field_type type(const char* name) const;

  /**
   * Retrieves a constant pointer to a field. Throws error if wrong data type
   * is requested.
   *
   * @param[in] field Name of field.
   *
   * @return Returns a constant pointer to field data. If the field does not
   * exist, returns a null pointer.
   */
  template<class DT> const DT* get(const char* field) const;

  /**
   * Retrieves a pointer to a field. Throws error if wrong data type is
   * requested.
   *
   * @param[in] field Name of field.
   *
   * @return Returns a pointer to field data. If the field does not
   * exist, returns a null pointer.
   */
  template<class DT> DT* get(const char* field);

  /**
   * Adds a field if it doesn't already exist.
   * Clears contents of field, sets with new parameters, and allocates memory
   * based on @p dims. If @p value is provided, the @p value array is copied to
   * the field.
   *
   * @param[in] field Name of field.
   * @param[in] dims Dimensions of field.
   * @param[in] value (Optional) Value of field.
   *
   * @warning If provided, @p value is assumed to be allocated to the number
   * of elements implied by @p dims.
   *
   * @warning The data type of @p value is used to determine the type of
   * storage to create. Valid data types are a c-string, int, unsigned int,
   * float, double, size_t, MATS_struct, and MATS_cell.
   *
   */
  template<class DT> void set(const char* field,
      const std::vector<size_t>& dims, const DT* value = NULL);

  /**
   * Adds a field if it doesn't already exist.
   * Clears contents of field, sets with new parameters, and allocates memory
   * based on @p dims. If @p value is provided, the @p value array is copied to
   * the field.
   *
   * @param[in] field Name of field.
   * @param[in] value Value of field.
   *
   * @warning The data type of @p value is used to determine the type of
   * storage to create. Valid data types are a c-string, int, unsigned int,
   * float, double, size_t, MATS_struct, and MATS_cell.
   *
   */
  template<class DT> void set(const char* field, const DT value);

  /**
   * Returns whether field exists.
   *
   * @param[in] name Name of field.
   *
   * @return Returns true if field exists, false otherwise.
   */
  bool isfield(const char* name) const;

  /**
   * Returns the names of the fields contained in the MATS_struct.
   */
  std::vector<std::string> fieldnames() const;

  /**
   * Writes out summary information of a MATS_struct.
   *
   * @warning This method writes to stdout. Do not use this if stdout does
   * not exist, i.e., if there is no terminal interface.
   */
  void display() const;

  /**
   * Clears contents of the MATS_struct (frees all field memory and
   * removes all fields).
   */
  void clear();

  /**
   * Assignment operator for MATS_struct.
   */
  MATS_struct& operator=(const MATS_struct& in);

  /**
   * Destructor clears all data fields.
   */
  virtual ~MATS_struct();

 private:
  std::map<std::string, MATS_fieldinfo> field_;
};


/**
 * Exchange the values of two MATS_struct objects.
 */
MATS_LIB void swap(MATS_struct& a, MATS_struct& b);


/**
 * Copy of MATS Struct (uses assignment operator). This method is used
 * to support other language integration.
 *
 * @param[in] from MATS_struct to be copied.
 * @param[in] to Pointer to MATS_struct to be copied to.
 */
MATS_LIB void
mats_struct_copy(const MATS_struct &from, MATS_struct *to);


/**
 * MATS_cell is a general indexed storage container build on the STL vector
 * container. It is comprised of indexed elements that contain varying data
 * array types and/or c-strings. Element indexing is column-major. Supported
 * data array types are int, unsigned int, float, double, size_t, char,
 * MATS_struct, and MATS_cell. All other data array types will fail to link.
 *
 * This class is equivalent to a cell array.
 */
class MATS_LIB MATS_cell {
 public:
  /**
   * Default constructor (creates empty MATS_cell).
   */
  MATS_cell();

  /**
   * Copy constructor (all data is copied from input MATS_cell).
   *
   * @param[in] in MATS_cell to be copied.
   */
  MATS_cell(const MATS_cell& in);

  /**
   * Constructs a MATS_cell with the given dimensions.
   *
   * @param[in] nrow Number of rows.
   * @param[in] ncol Number of columns.
   */
  MATS_cell(size_t nrow, size_t ncol);

  /**
   * Resizes the MATS_cell. If resulting size contains more elements,
   * new elements are initialized as empty. If resulting size contains fewer
   * elements, last elements (and data) are cleared.
   *
   * @param[in] nrow Number of rows.
   * @param[in] ncol Number of columns.
   */
  void resize(size_t nrow, size_t ncol);

  /**
   * Returns the total number of elements in the MATS_cell.
   */
  size_t size() const;

  /**
   * Returns the dimensions of the data stored in element @p ix.
   *
   * @param[in] ix Index of element requested.
   *
   * @return Returns the dimension vector of the element. If the index is out
   * of bounds, returns an empty vector.
   */
  std::vector<size_t> size(size_t ix) const;

  /**
   * Returns the dimensions of the MATS_cell.
   */
  std::vector<size_t> dims() const;

  /**
   * Returns the type of data contained in element @p ix.
   *
   * @param[in] ix Index of element requested.
   *
   * @return Returns the type value of the storage used to store the element.
   * If the index is out of bounds, returns tUNKNOWN.
   */
  MATS_field_type type(size_t ix) const;

  /**
   * Retrieves a constant pointer to the element data. Throws error for
   * invalid index. Throws error if wrong data type is requested.
   *
   * @param[in] ix Index of element requested.
   *
   * @return Returns constant pointer to field data.
   */
  template<class DT> const DT* get(size_t ix) const;

  /**
   * Retrieves a pointer to the element data. Throws error for
   * invalid index. Throws error if wrong data type is requested.
   *
   * @param[in] ix Index of element requested.
   *
   * @return Returns pointer to field data.
   */
  template<class DT> DT* get(size_t ix);

  /**
   * Replaces contents of an element.
   *
   * @param[in] ix Index of element.
   * @param[in] dims Dimensions of element.
   * @param[in] value Value of element.
   */
  template<class DT> void set(size_t ix, const std::vector<size_t>& dims,
      const DT* value);

  /**
   * Replaces contents of an element.
   *
   * @param[in] ix Index of element.
   * @param[in] value Value of element.
   */
  template<class DT> void set(size_t ix, const DT value);

  /**
   * Clears contents of the MATS_cell (frees all element memory and
   * removes all elements).
   */
  void clear();

  /**
   * Returns an element of the MATS_cell. Throws an error if the index
   * is out of bounds.
   *
   * @param[in] i Index of element.
   *
   * @return Returns a reference to the MATS_cell element.
   */
  MATS_fieldinfo& operator[](size_t i);

  /**
   * Assignment operator for MATS_cell.
   *
   * @param[in] in A MATS_cell object.
   */
  MATS_cell& operator=(const MATS_cell& in);

  virtual ~MATS_cell();

 private:
  size_t rc2ix(size_t r, size_t c) const;

  std::vector<size_t> dims_;
  std::vector<MATS_fieldinfo> data_;
};

}  // namespace mats

#endif  // SRC_MATS_STRUCT_H_
