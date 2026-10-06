# DISTRIBUTION STATEMENT D. Distribution authorized to the Department of
# Defense and U.S. DoD contractors only; Administrative or Operational Use; 1
# Jan 2017. Other U.S. requests shall be referred to Naval Surface Warfare
# Center Panama City Division, ATTN: Technical Director NSWC PCD, 110 Vernon
# Ave, Panama City, FL 32407.
"""
mats.time
---------
Contains functions related to date and time.
"""
import time
import math
import numpy as np
import mats.log


def display(date_dict):
    """
    Displays a MATS datetime dict as a standard date/time string.

    The format of the string is: 'MM/DD/YYYY HH:MM:SS'

    :param date_dict: MATS datetime dict to display.
    :type date_dict: dict
    """
    sec = math.floor(date_dict['dsecond'])
    print('{month:02d}/{day:02d}/{year:04d} {hour:02d}:{minute:02d}:{sec:02d}',
          **date_dict, sec=sec)


def datenum(date_val):
    """
    Converts a MATS datetime dict or date/time string to a double

    A string input should be formatted as follows: 'MM/DD/YYYY HH:MM:SS'

    :param date_val: The MATS datetime dict or string to convert.
    :type date_val: dict|string

    :return: The number of seconds since the epoch 00:00 hours, Jan 1, 1970 UTC.
             If date is invalid, returns 0.
    :rtype: double
    """
    if isinstance(date_val, str):
        d, t = date_val.split()
        d = d.split('/')
        t = t.split(':')
        date_val = {'year': int(d[2]), 'month': int(d[0]), 'day': int(d[1]),
                    'hour': int(t[0]), 'minute': int(t[1]),
                    'dsecond': float(t[2])}

    dim = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    day_secs = 24*60*60

    if date_val['month'] > 12 or date_val['month'] < 1:
        mats.log.error("Invalid month in date")
        return 0
    if date_val['day'] > 31 or date_val['day'] < 1:
        mats.log.error("Invalid day in date")
        return 0
    if date_val['hour'] > 24:
        mats.log.error("Invalid hour in date")
        return 0

    # TODO(Bradley): Do we also want to check for other invalid numbers in date?
    comp_years = int(date_val['year']) - 1970
    comp_leapdays = int(math.ceil((float(date_val['year'])-1972.0)/4.0))

    if (np.mod(date_val['year'], 4) == 0 and
            np.mod(date_val['year'], 100) != 0):
        dim[1] = 29

    # days in months
    dim_comp = np.sum(dim[0:date_val['month']-1])

    utc = comp_years*365 + comp_leapdays + dim_comp + date_val['day'] - 1
    utc = utc * day_secs
    utc = utc + date_val['hour']*60*60 + date_val['minute']*60
    utc = float(utc) + date_val['dsecond']

    return utc


def datetime(utc):
    """
    Converts a double to a MATS datetime dict.

    :param utc: The number of seconds since the epoch 00:00 hours, Jan 1, 1970 UTC.
    :type utc: double

    :return: The corresponding MATS datetime dict.
    :rtype: dict
    """
    date_val = {}
    day_secs = 24*60*60  # seconds in a day
    year_secs = day_secs*365
    days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    date_val['year'] = 1970
    while True:
        nutc = utc - year_secs
        if np.mod(date_val['year'], 4) == 0:
            nutc = nutc - day_secs
        if nutc < 0:
            break
        utc = nutc
        date_val['year'] = date_val['year'] + 1

    if np.mod(date_val['year'], 4) == 0 and np.mod(date_val['year'], 100) != 0:
        days[1] = 29

    date_val['month'] = 1
    for dim in days:
        nutc = utc - dim * day_secs
        if nutc < 0:
            break
        date_val['month'] = date_val['month'] + 1
        utc = nutc

    date_val['day'] = int(math.floor(utc / float(day_secs)))
    utc = utc - date_val['day'] * day_secs
    date_val['day'] = date_val['day'] + 1

    date_val['hour'] = int(math.floor(utc / 3600.0))
    utc = utc - date_val['hour'] * 3600

    date_val['minute'] = int(math.floor(utc / 60.0))
    utc = utc - date_val['minute'] * 60

    date_val['dsecond'] = utc

    return date_val


def datestr(utc):
    """
    Converts a double to a formatted string.

    :param utc: The number of seconds since the epoch 00:00 hours, Jan 1, 1970 UTC.
    :type utc: double

    :return: Date/time string with format: 'MM/DD/YYYY HH:MM:SS'
    :rtype: str
    """
    date_val = datetime(utc)
    sec = int(math.floor(date_val['dsecond']))
    date_str = '{month:02d}/{day:02d}/{year:04d} ' \
               '{hour:02d}:{minute:02d}:{sec:02d}'.format(**date_val, sec=sec)
    return date_str


def datenow() -> dict:
    """
    Returns the current date/time. Default is to return UTC date/time(GMT).
    """
    return datetime(time.time())


def is_leap_year(year):
    """
    Returns True if the given year is a leap year.

    :param year: Year to be tested.
    :type year: int
    :returns: Flag indicating whether the given year is a leap year
    :rtype: bool
    """
    if np.mod(year, 4) > 0:
        return False
    elif np.mod(year, 100) > 0:
        return True
    elif np.mod(year, 400) > 0:
        return False
    return True


def dst_correction(t):
    if t['hour'] != 0:
        t['hour'] -= 1
    else:
        # We are in the previous day. So everything needs to be adjusted.
        t['hour'] = 23

        if t['day'] != 1:
            t['day'] -= 1
        else:
            # Decreasing day goes to previous month. First we need to make sure
            # we didn't go to a different year.
            if t['month'] == 1:
                t['year'] -= 1
                t['month'] = 12
            else:
                t['month'] -= 1

            # Now we adjust the day. The number of days in each month is:
            # Month: 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12
            #  Days: 31, **, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31.
            # Set day to end of month for month we are in.
            if t['month'] == 2:
                # February - leap year??
                if is_leap_year(t['year']):
                    t['day'] = 29
                else:
                    t['day'] = 28
            elif t['month'] in [4, 6, 9, 11]:
                t['day'] = 30
            else:
                t['day'] = 31
    return
