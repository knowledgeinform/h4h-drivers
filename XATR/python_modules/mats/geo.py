# DISTRIBUTION STATEMENT D. Distribution authorized to the Department of
# Defense and U.S. DoD contractors only; Administrative or Operational Use; 1
# Jan 2017. Other U.S. requests shall be referred to Naval Surface Warfare
# Center Panama City Division, ATTN: Technical Director NSWC PCD, 110 Vernon
# Ave, Panama City, FL 32407.
"""
mats.geo
--------
Contains functions related to geospatial coordinates.
"""
import numpy as np
import math


EarthRadius = 6368941.0

# TODO: calcdistbear


def geolocate(lat0, lng0, heading, adist, cdist, altitude):
    """
    Calculate lat/long coordinate of point location from vehicle data.

    :param lat0: Latitude of vehicle, in radians.
    :param lng0: Longitude of vehicle, in radians.
    :param heading: Heading of vehicle, in radians.
    :param adist: Along-track distance, in meters.
    :param cdist: Cross-track (slant range) distance, in meters. This number
        will be negative for Port side, positive for Starboard.
    :param altitude: Altitude of vehicle above bottom, in meters.
    :returns: (latXY, lngXY), the converted latitude and longitude (in radians)
    :rtype: (float, float)
    .. note::  Heading: 0 = North, pi/2 = East, pi = South, 3*pi/2 = West.
               Latitude ranges from -pi/2 (South Pole) to +pi/2 (North Pole).
               Longitude ranges from -pi (west of PM) to +pi (east of PM).
    """
    print('geolocate: lng0 = {} rad (initial, aka {} deg)'.format(lng0, lng0*180/np.pi))
    print('geolocate: heading = {}'.format(heading))
    if abs(altitude) <= abs(cdist):
        cdist = np.sqrt(cdist*cdist - altitude*altitude)*np.sign(cdist)
    else:
        cdist = 0.0
    print('adist = {}; cdist = {}'.format(adist, cdist))

    latXY = np.fmod(lat0, np.pi)
    if latXY < -np.pi/2.0:
        latXY = latXY + np.pi
    if latXY > np.pi/2.0:
        latXY = latXY - np.pi

    lngXY = np.fmod(lng0, 2.0*np.pi)
    print('geolocate: lngXY = {} rad (after wrap, aka {} deg)'.format(lngXY, lngXY*180/np.pi))

    if lngXY < -np.pi:
        lngXY = lngXY + np.pi*2.0
    if lngXY > np.pi:
        lngXY = lngXY - np.pi*2.0
    print('geolocate: lngXY = {} rad (after adj, aka {} deg)'.format(lngXY, lngXY*180/np.pi))

    # Short circuit if offset calculations are unnecessary
    if adist == 0.0 and cdist == 0.0: return (latXY, lngXY)

    # Rotate
    xN = np.cos(heading)*adist - np.sin(heading)*cdist
    yE = np.sin(heading)*adist + np.cos(heading)*cdist
    print('geolocate: xN = {}; yE = {}'.format(xN, yE))
    # Translate
    latXY = latXY + xN/EarthRadius
    print('lngXY = {} + {}/{}/{}'.format(lngXY, yE, EarthRadius, np.cos(latXY)))
    lngXY = lngXY + yE/EarthRadius/np.cos(latXY)
    print('geolocate: lng0 = {} --> lngXY = {}'.format(lng0, lngXY))
    return (latXY, lngXY)


def geo2NE(ref, mLat, loc):
    """
    Conversion of Lat/Long (radians) into meters east and north using a
    locally-flat earth.

    :param ref: Lat/Long reference point (radians). [2x1]
    :param mLat: Mean Latitude for area (radians).
    :param loc: Lat/Long points to be converted to North/East. [2xN]
    :returns: Converted Lat/Long points.
    """
    global EarthRadius

    for k in range(loc.shape[1]):
        loc[1,k] = (loc[1,k] - ref[1])*math.cos(mLat)*EarthRadius
        loc[0,k] = (loc[0,k] - ref[0])*EarthRadius
    return loc


def NE2geo(ref, mLat, loc):
    """
    Inplace conversion of meters North/East into Lat/Long (radians).

    :param ref: Lat/Long reference point (radians). [2x1]
    :param mLat: Mean Latitude for area (radians).
    :param loc: North/East points to be converted to Lat/Long. [2xN]
    :returns: Converted North/East points.
    """
    global EarthRadius

    for k in range(loc.shape[1]):
        loc[1,k] = loc[1,k]/(EarthRadius*math.cos(mLat)) + ref[1]
        loc[0,k] = loc[0,k]/EarthRadius + ref[0]
    return loc


# void
# mats::region_latlon(size_t N, const double* lat, const double* lon,
#     double rng, const char* side, double* bdd) {
#   size_t k;
#   double sGeo[2], loc[2];
#   double ref[2] = {0, 0};
#   double mLat, th, dist;

#   // Starting position
#   sGeo[0] = lat[0]*MATS_PI/180; sGeo[1] = lon[0]*MATS_PI/180;

#   // Ending position
#   loc[0] = lat[N-1]*MATS_PI/180; loc[1] = lon[N-1]*MATS_PI/180;
#   mean(N, 1, lat, 0, &mLat);  // mean latitude
#   mLat = mLat*MATS_PI/180;

#   if (strcmp(side, "STBD") == 0)
#     rng = -rng;

#   // Convert end Lat/Lon into North/East relative to starting Lat/Lon
#   geo2NE(&sGeo[0], mLat, 1, &loc[0]);

#   // get heading
#   th = -atan2(loc[0], loc[1]);
#   dist = sqrt(loc[0]*loc[0] + loc[1]*loc[1]);

#   // rotate dimensions of region to heading
#   bdd[0] = 0; bdd[2] = 0;    bdd[4] = rng;  bdd[6] = rng;
#   bdd[1] = 0; bdd[3] = dist; bdd[5] = dist; bdd[7] = 0;
#   rotatePoints(&ref[0], th, 4, &bdd[0]);

#   // convert region coordinates to lat/lon
#   NE2geo(&sGeo[0], mLat, 4, &bdd[0]);

#   for (k=0; k < 8; k++)
#     bdd[k] = bdd[k]*180/MATS_PI;

#   return;
# }


def latlon2dist(lat0, lon0, lat1, lon1):
    """
    Calculate the distance (and heading) between two lat/long points

    :param lat0: Latitude of initial point
    :type lat0: float
    :param lon0: Longitude of initial point
    :type lon0: float
    :param lat1: Latitude of final point
    :type lat1: float
    :param lon1: Longitude of final point
    :type lon1: float
    :return: 1. The distance between the two points (lat0, lon0) and (lat1, lon1)
             2. The heading of the vector going from (lat0, lon0) to (lat1, lon1)
    :rtype: (float, float)
    """
    loc0 = (lat0 * math.pi / 180.0, lon0 * math.pi / 180.0)
    loc1 = np.zeros((2,1))
    # loc0[0] = lat0 * math.pi / 180.0;
    # loc0[1] = lon0 * math.pi / 180.0;
    loc1[0] = lat1 * math.pi / 180.0
    loc1[1] = lon1 * math.pi / 180.0

    # Calculate mean latitude
    meanLat = (loc0[0] + loc1[0,0]) / 2

    # Convert end Lat/Lon into North/East relative to starting Lat/Lon
    loc1 = geo2NE(loc0, meanLat, loc1)

    # get heading
    heading = -np.arctan2(loc1[0], loc1[1]).item()
    dist = np.sqrt(loc1.T @ loc1).item()

    return dist, heading
