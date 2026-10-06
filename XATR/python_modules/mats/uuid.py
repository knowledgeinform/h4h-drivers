# DISTRIBUTION STATEMENT D. Distribution authorized to the Department of
# Defense and U.S. DoD contractors only; Administrative or Operational Use; 1
# Jan 2017. Other U.S. requests shall be referred to Naval Surface Warfare
# Center Panama City Division, ATTN: Technical Director NSWC PCD, 110 Vernon
# Ave, Panama City, FL 32407.
"""
mats.uuid
---------
Contains functions related to universally unique identifiers (UUIDs).
"""
import uuid


def uuid_generator():
    """
    Generate a new UUID string of the form 00000000-0000-0000-0000-000000000000.

    :return: UUID string of the form above.
    :rtype: str
    """
    return str(uuid.uuid4()).upper()


def uuid_equal(uuid1, uuid2):
    """
    Tests if two UUIDs are equal. Throws an exception if one of the inputs is
    not a valid UUID.

    :param uuid1: A UUID string.
    :type uuid1: str
    :param uuid2: A UUID string.
    :type uuid2: str

    :return: Returns true if UUID strings are equal and false for not equal.
    :rtype: bool
    """
    if is_uuid(uuid1):
        raise ValueError("uuid_equal: first argument is not a valid UUID")
    if is_uuid(uuid2):
        raise ValueError("uuid_equal: second argument is not a valid UUID")
    return uuid1.upper() == uuid2.upper()


def is_uuid(uuid_str):
    """
    Verifies if a string is a valid UUID string.

    :param uuid_str: A UUID string.
    :type uuid_str: str

    :return: Returns true if UUID string is of the form
             00000000-0000-0000-0000-000000000000. Otherwise, returns false.
    :rtype: bool
    """
    # UUID format: 00000000-0000-0000-0000-000000000000
    #              012345678901234567890123456789012345
    #              000000000011111111112222222222333333

    # Check length
    if len(uuid_str) != 36:
        return False

    # Check for '-' in correct place
    for ix in [8, 13, 18, 23]:
        if uuid_str[ix] != '-':
            return False

    # Check digits
    for k in range(0, 8):
        if uuid_str[k] not in '0123456789ABCDEF':
            return False
    for k in range(9, 13):
        if uuid_str[k] not in '0123456789ABCDEF':
            return False
    for k in range(14, 18):
        if uuid_str[k] not in '0123456789ABCDEF':
            return False
    for k in range(19, 23):
        if uuid_str[k] not in '0123456789ABCDEF':
            return False
    for k in range(24, 36):
        if uuid_str[k] not in '0123456789ABCDEF':
            return False
    return True
