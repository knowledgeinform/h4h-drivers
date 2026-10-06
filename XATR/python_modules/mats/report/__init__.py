import os
from os.path import isfile, isdir, join
import json
import numpy as np
from math import floor
import matplotlib.pyplot as plt


def _load_json(filename):
    with open(filename) as fp:
        return json.load(fp)


def _cum_sum(bins, xarray):
    n = len(bins)
    m = len(xarray)
    cs = np.zeros(n)
    for x in xarray:
        for i in range(n):
            if x > bins[i]:
                continue
            cs[i] += 1
    cs = [(m-x)/m for x in cs]

    return cs


def _latex_sanitize(val):
    return val.replace('_', '\_')


from mats.report.configuration import ConfigReport
from mats.report.comparison import ComparisonReport
from mats.report.atrcfg import AtrcfgReport
