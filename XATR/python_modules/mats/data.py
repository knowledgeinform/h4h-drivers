# DISTRIBUTION STATEMENT D. Distribution authorized to the Department of
# Defense and U.S. DoD contractors only; Administrative or Operational Use; 1
# Jan 2017. Other U.S. requests shall be referred to Naval Surface Warfare
# Center Panama City Division, ATTN: Technical Director NSWC PCD, 110 Vernon
# Ave, Panama City, FL 32407.
"""
mats.data
---------
Classes and functions used for storing and handling data matrices.
"""
from enum import Enum


class Precision(Enum):
    """
    MATS precision types
    """
    UNKNOWN = 0
    UI = 1
    FLOAT = 2
    DOUBLE = 3


class Storage(Enum):
    """
    MATS storage types (Column Major or Row Major)
    """
    COL_MAJOR = 0
    ROW_MAJOR = 1


class Format(Enum):
    """
    MATS data formats (data is real/complex data, or amplitude/phase)
    """
    matsREAL_IMAG = 0
    matsAMP_PHASE = 1


# Return subimage defined by index bounds
# - index_a1, index_a2 = initial/final index in along-track direction
# - index_c1, index_c2 = initial/final index in cross-track direction
def mats_data_snippet(data, index_a1, index_a2, index_c1, index_c2):
    return data['data'][index_a1:index_a2+1, index_c1:index_c2+1]

# Return magnitude subimage defined by index bounds
# - index_a1, index_a2 = initial/final index in along-track direction
# - index_c1, index_c2 = initial/final index in cross-track direction
def mats_data_abs_snippet(data, index_a1, index_a2, index_c1, index_c2):
    return data['abs'][index_a1:index_a2+1, index_c1:index_c2+1]
