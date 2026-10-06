/**
 * @file
 * @brief File contains routines for latitude/longitude calculations.
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
#ifndef SRC_MATS_GEO_H_
#define SRC_MATS_GEO_H_

#include "MATS_platform.h"

namespace mats {

/**
 * Approximate radius of the Earth, in meters.
 */
#define MATS_EARTH_RADIUS 6368941.0


/**
 * Calculate latitude and longitude based on a given distance and bearing from
 * a reference lat/long.
 *
 * @note Bearing: 0 deg = North, 90 deg = East, 180 deg = South, 270 deg = West.
 * Latitude ranges from -90 deg (South Pole) to +90 deg (North Pole).
 * Longitude ranges from -180 deg (west of PM) to +180 deg (east of PM).
 *
 * @param[in] distance Distance from reference point, in meters.
 * @param[in] bearing Bearing from reference point, in degrees.
 * @param[in] lat0 Latitude of reference point, in degrees.
 * @param[in] lon0 Longitude of reference point, in degrees.
 * @param[out] lat Latitude of new point, in degrees.
 * @param[out] lon Longitude of new point, in degrees.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
calcdistbear(double distance, double bearing, double lat0, double lon0,
    double* lat, double* lon);


/**
 * Calculate lat/long coordinate of point location from vehicle data.
 *
 * @note Heading: 0 = North, pi/2 = East, pi = South, 3*pi/2 = West.
 * Latitude ranges from -pi/2 (South Pole) to +pi/2 (North Pole).
 * Longitude ranges from -pi (west of PM) to +pi (east of PM).
 *
 * @param[in] lat0 Latitude of vehicle, in radians.
 * @param[in] lng0 Longitude of vehicle, in radians.
 * @param[in] heading Heading of vehicle, in radians.
 * @param[in] adist Along-track distance, in meters.
 * @param[in] cdist Cross-track (slant range) distance, in meters. This number
 * will be negative for Port side, positive for Starboard.
 * @param[in] altitude Altitude of vehicle above bottom, in meters.
 * @param[out] latXY Latitude of point, in radians.
 * @param[out] lngXY Longitude of point, in radians.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
geolocate(double lat0, double lng0, double heading, double adist, double cdist,
    double altitude, double* latXY, double* lngXY);


/**
 * This function returns the average heading that is used in the motion
 * solution calculations in the NERDS code.
 *
 * @param[in] lat Array of latitude positions.
 * @param[in] lon Array of longitude positions.
 * @param[in] length Length of latitude and longitude arrays.
 *
 * @return Returns the average heading in degrees.
 *
 * @warning The input @p lat and @p lon arrays are modified.
 *
 * @author Jonathan King
 */
MATS_LIB float
calcNominalHeading(float* lat, float* lon, size_t length);


/**
 * Inplace conversion of Lat/Long (radians) into meters east and north using a
 * locally-flat earth.
 *
 * @param[in] ref Lat/Long reference point (radians). [2x1]
 * @param[in] mLat Mean Latitude for area (radians).
 * @param[in] N Number of points.
 * @param[in,out] loc Lat/Long points to be converted to North/East. [2xN]
 *
 * @warning Function does no allocation. @p loc is overwritten by this function.
 */
MATS_LIB void
geo2NE(const double* ref, double mLat, size_t N, double* loc);


/**
 * Inplace conversion of meters North/East into Lat/Long (radians).
 *
 * @param[in] ref Lat/Long reference point (radians). [2x1]
 * @param[in] mLat Mean Latitude for area (radians).
 * @param[in] N Number of points.
 * @param[in,out] loc North/East points to be converted to Lat/Long. [2xN]
 *
 * @warning Function does no allocation. @p loc is overwritten by this function.
 */
MATS_LIB void
NE2geo(const double* ref, double mLat, size_t N, double* loc);


/**
 * Computes Latitude/Longitude bounds based on vehicle track, side and range.
 *
 * @param[in] N Number of vehicle track samples.
 * @param[in] lat Vehicle latitude position vector in degrees [Nx1].
 * @param[in] lon Vehicle longitude position vector in degrees [Nx1].
 * @param[in] rng Range of vehicle sensor in meters.
 * @param[in] side Side of Vehicle (PORT|STBD).
 * @param[out] bdd Latitude/Longitude bounds in degrees [2x4].
 *
 * @warning @p bdd is assumed to be already allocated.
 */
MATS_LIB void
region_latlon(size_t N, const double* lat, const double* lon,
    double rng, const char* side, double* bdd);


/**
 * Calculate distance in meters and heading in radians between two lat/long
 * coordinates in degrees.  Heading is CW from E.
 *
 * @param[in] lat0 Latitude (degrees) of first point.
 * @param[in] lon0 Longitude (degrees) of first point.
 * @param[in] lat1 Latitude (degrees) of second point.
 * @param[in] lon1 Longitude (degrees) of second point.
 * @param[out] dist Distance (meters) between the two points.
 * @param[out] heading Heading (radians) from first to second point, CW from E.
 */
MATS_LIB void
latlon2dist(double lat0, double lon0, double lat1, double lon1,
    double& dist, double& heading);

}  // namespace mats

#endif  // SRC_MATS_GEO_H_
