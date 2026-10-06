# DISTRIBUTION STATEMENT D. Distribution authorized to the Department of
# Defense and U.S. DoD contractors only; Administrative or Operational Use; 1
# Jan 2017. Other U.S. requests shall be referred to Naval Surface Warfare
# Center Panama City Division, ATTN: Technical Director NSWC PCD, 110 Vernon
# Ave, Panama City, FL 32407.
"""
mats.log
--------
Contains function for log reporting.
"""
import time
import logging
import logging.handlers
import sys
import os.path as osp
import mats.filesystem

__time_format = '%Y-%m-%d %H:%M:%S'
__logger = None  # type: None or logging.Logger
__debug_level = 0

def _timestamp():
    return time.strftime(__time_format, time.gmtime())


def setup(logname=None, loglevel=logging.DEBUG, logfile=None, maxbytes=None,
          backups=0):
    """
    Creates and sets up logger.

    .. note:: Run mats.log.setup to enable use of log file.

    :param logname: Name used to identify logger object.
    :type logname: str
    :param loglevel: Logging level.
    :type loglevel: int
    :param logfile: Log filename.
    :type logfile: str
    :param maxbytes: Max bytes for log file size.
    :type maxbytes: int
    :param backups: Number of backup log files to allow.
    :type backups: int
    :return: None
    """
    if logname is None:
        logname = __name__
    if logfile is None:
        logfile = 'pymats.log'
    if maxbytes is None:
        maxbytes = 5 * 1024 * 1024
    global __logger
    __logger = logging.getLogger(logname)
    __logger.setLevel(loglevel)

    rfh = logging.handlers.RotatingFileHandler(
        logfile, mode='w', maxBytes=maxbytes, backupCount=backups)
    __logger.addHandler(rfh)


def info(msg):
    """
    Reports an information message.

    .. note:: Run mats.log.setup to enable use of log file.

    :param msg: Message to report.
    :type msg: str
    :return: None
    """
    time_str = _timestamp()
    if __logger is None:
        print(f'INFO[{time_str}]: {msg}')
        return
    filename, line_num, func, x = __logger.findCaller(stack_info=True)
    err_str = '--------\n---- %s\n' % time_str
    err_str += '    File: %s (line %d)\n' % (filename, line_num)
    err_str += 'Function: %s\n' % func
    err_str += '    Info: %s\n%s\n' % (msg, x)
    __logger.warning(time_str+': '+msg)
    return


def warn(msg):
    """
    Reports a warning message.

    .. note:: Run mats.log.setup to enable use of log file.

    :param msg: Warning message to report.
    :type msg: str
    :return: None
    """
    time_str = _timestamp()
    if __logger is None:
        print(f'WARN[{time_str}]: {msg}')
        return
    filename, line_num, func, x = __logger.findCaller(stack_info=True)
    err_str = '--------\n---- %s\n' % time_str
    err_str += '    File: %s (line %d)\n' % (filename, line_num)
    err_str += 'Function: %s\n' % func
    err_str += ' Warning: %s\n%s\n' % (msg, x)
    __logger.warning(time_str+': '+msg)
    return


def error(msg):
    """
    Reports an error message.

    .. note:: Run mats.log.setup to enable use of log file.

    :param msg: Error message to report.
    :type msg: str
    :return: None
    """
    time_str = _timestamp()
    if __logger is None:
        print(f'ERROR[{time_str}]: {msg}')
        return
    filename, line_num, func, x = __logger.findCaller(stack_info=True)
    err_str = '--------\n---- %s\n' % time_str
    err_str += '    File: %s (line %d)\n' % (filename, line_num)
    err_str += 'Function: %s\n' % func
    err_str += '   Error: %s\n%s\n' % (msg, x)
    __logger.warning(time_str+': '+msg)
    return


def debug_str2int(lvl):
    """
    Convert debug level string name to integer value. Accepted string values
    are: OFF, MINIMAL, DETAILED, and VERBOSE.

    :param lvl: Debug level string name.
    :type lvl: str
    :return: Debug integer value of named debug level.
    :rtype: int
    """
    levels = {'OFF': 0, 'MINIMAL': 1, 'DETAILED': 30, 'VERBOSE': 100}
    if lvl not in levels:
        raise ValueError(f'Unknown debug level "{lvl}."')
    return levels[lvl]


def debug_level(lvl):
    """
    Set or retrieves debug level.

    :param lvl: Desired debug level.
    :type lvl: int or str
    :return: Set debug level.
    :rtype: int
    """
    global __debug_level

    if type(lvl) == str:
        __debug_level = debug_str2int(lvl)
    elif type(lvl) == int:
        if lvl < 0:
            raise ValueError('Debug level should be >= 0.')
        __debug_level = lvl
    else:
        raise ValueError('Unhandled debug level value type.')
    return __debug_level


def debug(lvl, msg):
    """
    Prints debug message if level is less than or equal to the current debug
    level.

    :param lvl: Message debug level.
    :type lvl: int or str
    :param msg: Debug message.
    :type msg: str
    :return: None
    """
    global __debug_level
    if lvl > __debug_level:
        return
    print(msg)
    return
