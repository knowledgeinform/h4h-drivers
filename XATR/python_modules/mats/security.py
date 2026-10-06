# DISTRIBUTION STATEMENT D. Distribution authorized to the Department of
# Defense and U.S. DoD contractors only; Administrative or Operational Use; 1
# Jan 2017. Other U.S. requests shall be referred to Naval Surface Warfare
# Center Panama City Division, ATTN: Technical Director NSWC PCD, 110 Vernon
# Ave, Panama City, FL 32407.
"""
mats.security
-------------
Contains functions that generate file hashes.
"""
import hashlib

__SHA1_BUF_SIZE = 161


def sha1_hash(fn):
    """
    Returns SHA1 hash of a file.

    :param fn: File name (full path).
    :type fn: str

    :return: SHA1 hash of the file.
    :rtype: str
    """
    sha1 = hashlib.sha1()
    with open(fn, 'rb') as f:
        while True:
            data = f.read(__SHA1_BUF_SIZE)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()
