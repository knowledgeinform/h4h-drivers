# DISTRIBUTION STATEMENT D. Distribution authorized to the Department of
# Defense and U.S. DoD contractors only; Administrative or Operational Use; 1
# Jan 2017. Other U.S. requests shall be referred to Naval Surface Warfare
# Center Panama City Division, ATTN: Technical Director NSWC PCD, 110 Vernon
# Ave, Panama City, FL 32407.
"""
mats.filesystem
_______________
Contains common functions for working with the filesystem. Further, it contains
functions that are usged to the search path for different parts of PyMATS.
"""
import os
import os.path as osp
import platform


def mats_working_dir(pathTo=None):
    """
    Sets and retrieves file path to PyMATS working directory.

    :param pathTo: Path to working directory.
    :type pathTo: str, optional
    :return: File path to working directory.
    :rtype: str
    """
    if pathTo:
        mats_working_dir.workingDir = pathTo
    elif not hasattr(mats_working_dir, "workingDir"):
        # mats_working_dir.workingDir = mc.mats_output_dir()
        if 'XATR_ROOT' in os.environ:
            if platform.system() == 'Windows':
                mats_working_dir.workingDir = osp.join('C:\\', 'ProgramData', 'XATR')
            else:
                mats_working_dir.workingDir = os.environ['XATR_ROOT']
        else:
            mats_working_dir.workingDir = '.'
    return mats_working_dir.workingDir


def mats_config_dir(pathTo=None):
    """
    Sets and retrieves file path to PyMATS configuration directory.

    :param pathTo: Path to configuration directory.
    :type pathTo: str, optional
    :return: File path to configuration directory.
    :rtype: str
    """
    if pathTo:
        mats_config_dir.configDir = pathTo
    elif not hasattr(mats_config_dir, "configDir"):
        # mats_config_dir.configDir = mc.mats_config_dir()
        if 'XATR_ROOT' in os.environ:
            mats_config_dir.configDir = osp.join(mats_working_dir(), 'config')
        else:
            mats_config_dir.configDir = osp.join('.', 'config')
    return mats_config_dir.configDir


def mats_package_dir(pathTo=None):
    """
    Sets and retrieves file path to PyMATS package directory.

    :param pathTo: Path to package directory.
    :type pathTo: str, optional
    :return: File path to package directory.
    :rtype: str
    """
    if pathTo:
        mats_package_dir.path = pathTo
    elif not hasattr(mats_package_dir, "path"):
        # mats_config_dir.path = mc.mats_config_dir()
        if 'XATR_ROOT' in os.environ:
            mats_package_dir.path = osp.join(os.environ['XATR_ROOT'], 'packages')
        else:
            mats_package_dir.path = osp.join('.', 'packages')
    return mats_package_dir.path


# Retrieve the basename of a file from a full path or full filename.
#
# filename = Path or filename.
# basename =
def file_basename(file_path):
    """
    Returns basename of a file from a full path or full filename.

    :param file_path: File path or filename.
    :type file_path: str
    :return: Local path of filename, minus file extension (i.e., substring of
             filename excluding all directories and any final extension
             (including .))
    :rtype: str
    """
    basename, _ = osp.splitext(os.path.basename(file_path))
    return basename
