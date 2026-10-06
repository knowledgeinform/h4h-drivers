/**
 * @file
 * @brief File contains common ATR specific routines used by MATS and MATS
 *        modules.
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
#ifndef SRC_MATS_CORE_H_
#define SRC_MATS_CORE_H_

#include <list>
#include <set>

#include "MATS_platform.h"
#include "MATS_input.h"
#include "MATS_contact.h"
#include "MATS_ecdata.h"
#include "MATS_groundtruth.h"
#include "MATS_cfg.h"
#include "MATS_atrconfig.h"
#include "MATS_error.h"
#include "MATS_message.h"
#include "MATS_filesystem.h"
#include "MATS_basic.h"
#include "MATS_perf.h"


namespace mats {

/**
 * A structure for storing the coordinates of segments of data.
 */
struct MATS_LIB MATS_segment {
  /**
   * Clear contents.
   */
  void clear() {
    x_starts.clear();
    x_ends.clear();
    y_starts.clear();
    y_ends.clear();
    return;
  }

  std::vector<size_t> x_starts;  /**< Start cross-track indices (0-based) */
  std::vector<size_t> x_ends;  /**< End cross-track indices (0-based) */
  std::vector<size_t> y_starts;  /**< Start along-track indices (0-based) */
  std::vector<size_t> y_ends;  /**< End along-track indices (0-based) */
};


/**
 * Display a MATS_segment to stdout.
 * This function only works if the MATS_DEBUG flag is set.
 */
MATS_LIB void
mats_display_segment(const MATS_segment& seg);


/**
 * Save a MATS_segment in an HDF5 file, under the group name "chunks".
 *
 * @param[in] filename File to create.
 * @param[in] data MATS_segment to save.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
mats_segment_save(const char* filename, const MATS_segment& data);


/**
 * Load a MATS_segment from an HDF5 file, from the group name "chunks".
 *
 * @param[in] filename File to read.
 * @param[out] data The loaded MATS_segment.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
mats_segment_load(const char* filename, MATS_segment* data);


/**
 * A structure for storing the coordinates of a data region along with the
 * state (OK or BAD) and, if bad, the reason it is bad.
 */
struct MATS_region {
  MATS_region(): start(0), end(0) {}

  /**
   * Clear contents.
   */
  void clear() {
    start = 0;
    end = 0;
    state.clear();
    reason.clear();
    perf.clear();
    return;
  }

  /**
   * Less-than operator.  Returns true if the start of the first MATS_region is
   * less than the start of the second MATS_region.
   *
   * @param[in] in MATS_region to compare.
   */
  bool operator<(const MATS_region& in) const {return (start < in.start);}

  /**
   * Greater-than operator.  Returns true if the start of the first MATS_region
   * is greater than the start of the second MATS_region.
   *
   * @param[in] in MATS_region to compare.
   */
  bool operator>(const MATS_region& in) const {return (start > in.start);}

  size_t start;  /**< Start along-track index (0-based) */
  size_t end;  /**< End along-track index (0-based) */
  std::string state;  /**< Whether the region is "OK" or "BAD" */
  std::string reason;  /**< If the region is bad, the reason why */
  MATS_perf perf;  /**< Performance estimation for the region */
};


/**
 * Save a MATS_region vector in an HDF5 file, under the group name "segments".
 *
 * @param[in] filename File to create.
 * @param[in] data MATS_region vector to save.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
mats_region_vector_save(const char* filename,
    const std::vector<MATS_region>& data);


/**
 * Load a MATS_region vector from an HDF5 file, from the group name "segments".
 *
 * @param[in] filename File to read.
 * @param[out] data The loaded MATS_region vector.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
mats_region_vector_load(const char* filename, std::vector<MATS_region>* data);


/**
 * Groundtruth a contact list.
 *
 * @param[in] input Full input associated with contacts.
 * @param[in] gt Groundtruth information.
 * @param[in,out] con Contact list, updated with groundtruth info.
 */
MATS_LIB void
gt_contact_list(
    const mats::MATS_input& input,
    const std::vector<mats::MATS_groundtruth>& gt,
    mats::MATS_contact_list& con);


/**
 * Generate pixel groundtruth from Lat/Long groundtruth information.
 *
 * @param[in] gtLat Groundtruth latitudes.
 * @param[in] gtLon Groundtruth longitudes.
 * @param[in] gtTime Groundtruth times.
 * @param[in] input Full input for pixel generation.
 *
 * @return Returns vector of groundtruths.
 */
MATS_LIB std::vector<MATS_groundtruth>
gt_latlong2pixel(
    const std::vector<double>& gtLat,
    const std::vector<double>& gtLon,
    const std::vector<double>& gtTime,
    const MATS_input& input);


/**
 * Fills in contact fields with default values or values coming directly
 * from the input structure.  This function should be called after running the
 * detector (not within the detector itself), but before running the classifier.
 * It should be used with a full MATS_input, not a chunk.
 *
 * @param[in] input The input to be used to fill in contact information.
 * @param[in,out] con MATS_contact to be filled.
 * @param[in,out] ecd MATS_ecdata to be filled.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
detsub_contact_fill(const MATS_input& input,
    MATS_contact& con, MATS_ecdata& ecd);


/**
 * Determine the lat/long coordinates of a specified image location using
 * vehicle data.
 *
 * This version uses the geolocate() function.
 *
 * @param[in] input     The input containing interpolated vehicle nav data.
 * @param[in] x         Cross-track index of contact (0-based).
 * @param[in] y         Along-track index of contact (0-based).
 * @param[out] lat      Latitude of (x,y) location (deg).
 * @param[out] lng      Longitude of (x,y) location (deg).
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
get_contact_latlong(const MATS_input_base& input, size_t x, size_t y,
    double& lat, double& lng);


/**
 * Determine the lat/long coordinates of a specified image location using
 * vehicle data.
 *
 * This version uses the geo2NE(), rotatePoints(), and NE2geo() functions.
 *
 * @param[in] input     The input containing interpolated vehicle nav data.
 * @param[in] x         Cross-track index of contact (0-based).
 * @param[in] y         Along-track index of contact (0-based).
 * @param[out] lat      Latitude of (x,y) location (deg).
 * @param[out] lng      Longitude of (x,y) location (deg).
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
get_contact_latlong2(const MATS_input_base& input, size_t x, size_t y,
    double& lat, double& lng);


/**
 * Remove duplicate contacts from a contact list using the ecdata.groupnum
 * field.  A contact list is examined for groups of multiple contacts.  If
 * such a group is found, only the contact with the highest confidence is
 * kept in the list.
 *
 * @param[in,out] contacts The contact list.
 * @param[in,out] ecdata The corresponding ecdata list.
 *
 * @return A flag indicating whether anything was removed from the list.
 *
 * @author Derek Kolacinski, NSWC PC (derek.kolacinski@navy.mil)
 */
MATS_LIB bool
prune_duplicate_contacts(MATS_contact_list& contacts, MATS_ecdata_list& ecdata);


/**
 * This function calculates the area of the image which is most suitable to ATR.
 * The calcuation uses a different method for different sensors. The values are
 * put into the input structure.
 *
 * @param[in,out] input An input to have its sweetspot field set.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
calc_sweetspot(MATS_input_base& input);


/**
 * Contact centering.
 *
 * @param[in] input The input corresponding to the (x,y) coordinates.
 * @param[in,out] x Contact cross-track index.
 * @param[in,out] y Contact along-track index.
 */
MATS_LIB void
roi_recenter(const mats::MATS_input& input, size_t& x, size_t& y);


/**
 * Based on the (x,y) position of a contact, add a snippet to ecdata for each
 * band.  The (x,y) position applies to the reference band of input.  This
 * function is similar to snippet_generator() from the original %MATS.
 *
 * @param[in] input Input structure associated with contacts.
 * @param[in] con Contact structure containing (x,y) position.
 * @param[in,out] ecd Ecdata structure, updated with snippet(s).
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
add_snippets(const mats::MATS_input_base& input, const mats::MATS_contact& con,
    mats::MATS_ecdata& ecd);


/**
 * Calculate the boundaries of image chunks within full image represented
 * by input.
 *
 * @param[in] input Input to be chunked.
 * @param[in] bad_regions Regions of input to ignore.
 * @param[out] chunk_data Calculated boundaries of image chunks.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
calc_image_partitions(const MATS_input& input,
    const std::vector<MATS_region>& bad_regions, MATS_segment& chunk_data);


/**
 * Data Integrity Verification (DIV) Phase:
 * Analyze the input data and determine which ping ranges have corrupt or
 * unusable data (e.g., turns, sudden spikes in vehicle data).
 *
 * @param[in] input The input to be analyzed.
 *
 * @return Region struct vector of bad region elements
 *         @li .start/.end = ping range of bad region.
 *         @li .reason = string describing why the region is bad.
 */
MATS_LIB std::vector<MATS_region>
data_integ_verif_phase(const MATS_input_base& input);


/**
 * Detect ATR problematic data regions with height data.
 *
 * @param[in] input The input to be analyzed.
 *
 * @return Region struct vector of bad region elements
 *         @li .start/.end = ping range of bad region.
 *         @li .reason = string describing why the region is bad.
 */
MATS_LIB std::vector<MATS_region>
detect_height_anomaly(const MATS_input_base& input);


/**
 * Detect vehicle turning regions.
 *
 * @param[in] input The input to be analyzed.
 * @param[in] blk_sz (Optional) Block size for dividing data.  Default is 100.
 * @param[in] turn_ind (Optional) Initial threshold for turn in radians.
 * Default is 0.05.
 * @param[in] comp_turn (Optional) Turn threshold in radians for extending
 * turn region.  Default is 0.01.
 *
 * @return Region struct vector of bad region elements
 *         @li .start/.end = ping range of bad region.
 *         @li .reason = string describing why the region is bad.
 */
MATS_LIB std::vector<MATS_region>
detect_turns_hb(const MATS_input_base& input, size_t blk_sz = 100,
    double turn_ind = 0.05, double comp_turn = 0.01);


/**
 * Determines good image segments from problematic regions.
 *
 * @param[in] bad_regions Areas of image that contain errors. It is possible
 * that elements of bad_regions may overlap.
 * @param[in] full_y The full along-track size of the image.
 * @param[in] des_y The desired along-track chunk size. Chunks that are
 * significantly smaller than this will be folded into adjacent chunks or
 * dropped entirely.
 *
 * @return Returns the regions of an image that can be processed, based on the
 * areas that have been identified to contain errors. Only the y_starts and
 * y_ends fields are filled in. These regions are not chunked except for the
 * boundaries created by bad regions.
 */
MATS_LIB MATS_segment
calc_good_segments(
    const std::vector<MATS_region>& bad_regions,
    size_t full_y,
    size_t des_y);


/**
 * Determines good image segments from problematic regions.
 *
 * This version automatically calculates the desired along-track chunk size
 * based on a square chunk.
 *
 * @param[in] bad_regions Areas of image that contain errors. It is possible
 * that elements of bad_regions may overlap.
 * @param[in] input Input data.
 *
 * @return Returns the regions of an image that can be processed, based on the
 * areas that have been identified to contain errors. Only the y_starts and
 * y_ends fields are filled in. These regions are not chunked except for the
 * boundaries created by bad regions.
 */
MATS_LIB MATS_segment
calc_good_segments(const std::vector<MATS_region>& bad_regions,
    const MATS_input& input);


/**
 * Combines a MATS_segment with a MATS_region vector and sorts the regions.
 *
 * @param[in] good_regions MATS_segment listing good regions.
 * @param[in] bad_regions MATS_region vector, typically containing bad regions.
 *
 * @return Returns the combined MATS_region vector.
 */
MATS_LIB std::vector<MATS_region>
combine_all_regions(const MATS_segment& good_regions,
    const std::vector<MATS_region>& bad_regions);


/**
 * Sort contacts by ascending y-coordinates.
 *
 * @param[in,out] contacts Vector of MATS_contact objects to be sorted.
 * @param[in,out] ecdata Vector of MATS_ecdata objects, corresponding to
 * contacts.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
sort_contacts(MATS_contact_list& contacts, MATS_ecdata_list& ecdata);


/**
 * Contact correlation phase.
 *
 * @param[in] input The input corresponding to @p contacts and @p ecdata.
 * @param[in] contacts Vector of contacts to be grouped.
 * @param[in,out] ecdata Vector of ecdata objects, corresponding to
 * @p contacts.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
group_contacts(const MATS_input_base& input,
    const MATS_contact_list& contacts, MATS_ecdata_list& ecdata);


/**
 * Subroutine anisodiff from %MATS normalize_images function.
 *
 * @param[in,out] im Input/output image.
 * @param[in] niter Number of iterations.
 * @param[in] kappa Parameter.
 * @param[in] lambda Parameter.
 * @param[in] option Option (may be 1 or 2).
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
anisodiff(MATS_data& im, size_t niter, double kappa, double lambda,
    int option);

}  // namespace mats


#endif  // SRC_MATS_CORE_H_
