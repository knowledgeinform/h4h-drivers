/**
 * @file
 * @brief File contains routines for using JSON.
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
#ifndef SRC_MATS_JSON_H_
#define SRC_MATS_JSON_H_

// #include "rapidjson/document.h"

#include "MATS_platform.h"
#include "MATS_contact.h"
#include "MATS_ecdata.h"
#include "MATS_struct.h"


namespace mats {


/**
 * Pointer to MATS JSON document object.
 */
typedef void mats_json_doc;


/**
 * Prints JSON document to standard out.
 *
 * @param[in] doc JSON document.
 *
 * @return None.
 */
void
json_print(mats::mats_json_doc *doc);

/**
 * Converts Object JSON string into the Object. Specialization for the object
 * type must be implemented for the function to work. Unhandled specializations
 * log an error.
 *
 * @param[in] json Stringified Object JSON.
 *
 * @return Object from input string.
 */
template<class DT> MATS_LIB DT
from_json(const std::string& json);


/**
 * Creates an empty JSON document.
 *
 * @return Pointer to allocated JSON document.
 */
MATS_LIB mats::mats_json_doc *
json_create();


/**
 * Destroys or deallocates JSON document.
 *
 * @return Zero on success.
 */
MATS_LIB int
json_destroy(mats_json_doc *);


/**
 * Load json file into a RapidJSON Document.
 *
 * @param[in] filename Name of JSON file.
 * @param[out] doc Loaded JSON file contents.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
json_load(const char* filename, mats::mats_json_doc* doc);


/**
 * Write a RapidJSON Document to a file.
 *
 * @param[in] filename Name of JSON file to write.
 * @param[in] doc JSON content to be written.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
json_save(const char* filename, const mats::mats_json_doc *doc);


/**
 * Converts MATS_contact into JSON string.
 *
 * @param[in] con MATS_contact to convert.
 *
 * @return Returns the equivalent JSON string.
 */
MATS_LIB std::string
to_json(const mats::MATS_contact& con);


/**
 * Write a sequence of %MATS contacts to an JSON file.
 *
 * @param[in] conList List of contacts.
 * @param[in] ecList List of ecdata. Entries should correspond to those
 * in @p conList.
 * @param[in] filename Path to file to be written.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
mats_contacts_to_jsonfile(const mats::MATS_contact_list &conList,
    const mats::MATS_ecdata_list &eclist, const char *filename);


/**
 * Converts MATS_struct into JSON string.
 *
 * @param[in] data MATS_struct to convert.
 *
 * @return Returns the equivalent JSON string.
 */
MATS_LIB std::string
to_json(const mats::MATS_struct& con);

}  // namespace mats
#endif  // SRC_MATS_JSON_H_
