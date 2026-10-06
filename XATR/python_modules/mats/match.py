# -*- coding: utf-8 -*-
"""
Functions that determine whether two data structures are equivalent

Created on Thu Mar 12 16:26:05 2020

@author: Derek Kolacinski
"""

import PyMATS_core
import mats
import numpy

# General type categories that capture all functionally equivalent versions
#   (i.e., C library version, Python version, and simple Python equivalent)
STRUCT_TYPES = [PyMATS_core.MATS_struct, mats.mats_struct.Struct, dict]
CELL_TYPES = [PyMATS_core.MATS_cell, mats.mats_cell.Cell, list]

# Returns true if two items contain the same value.
#
# ref = reference item that defines the proper structure of the other item
# path = relative path of these items (used to trace through nested levels)
# verbose = print messages describing differences found
# strict = if True, additional fields are permitted in other item (for structs only)
def match(ref, other, path=None, verbose=None, strict=None):
    if path is None: path = ''
    if verbose is None: verbose = False
    if strict is None: strict = True
    out = False
    if loose_type_match([ref, other], STRUCT_TYPES):
        out = match_struct(ref, other, path, verbose, strict)
    elif loose_type_match([ref, other], CELL_TYPES):
        out = match_cell(ref, other, path, verbose, strict)
    elif type(ref) == type(other):
        if type(ref) is numpy.ndarray:
            out = numpy.array_equal(ref, other)
        elif type(ref) is list:
            if len(ref) != len(other): return False
            out = True
            for q in range(len(ref)):
                out = out and match(ref[q], other[q])
        else:
            out = (ref == other)
    else:   # items have different data types
        # Check if this is merely superficial (e.g., 1.0 vs 1)
        # NOTE: While most numeric values are saved as doubles, some are saved
        #   as integers, and there does not appear to be a hard rule as to
        #   when this will occur.  Therefore, we'll allow it, and warn.
        try:
            out = (float(ref) == float(other))
            if out: print('WARNING: Mixed type for %s\ntype(x)=%s, type(y)=%s\n' % (path, type(ref), type(other)))
        except RuntimeError:
            if verbose: print('type(x)=%s, type(y)=%s' % (type(ref), type(other)))
    return out

# Returns true if all fields of two structures/dictionaries match
#
# ref = reference item that defines the fields of the other struct
# path = relative path of these items (used to trace through nested levels)
# verbose = print messages describing differences found
# strict = if True, additional fields are permitted in other item
def match_struct(ref, other, path=None, verbose=None, strict=None):
    if path is None: path = ''
    if verbose is None: verbose = False
    if strict is None: strict = True
    ref_keys = set(ref.keys())
    other_keys = set(other.keys())
    extras = False  # Are there extra fields? Assume not until found
    out = True      # Do these structs match? Assume yes until mismatches
    # Look for fields that exist in only one struct
    for k in ref_keys - other_keys:
        if verbose: print('Field %s\\%s in ref but not other' % (path, k))
        extras = True
    if strict:
        for k in other_keys - ref_keys:
            if verbose: print('Field %s\\%s in other but not ref' % (path, k))
            extras = True
    # Match fields shared by both recursively
    for k in ref_keys & other_keys:
        ok = match(ref[k], other[k], '%s\\%s' % (path, k), verbose, strict)
        if not ok and verbose:
            print('%s\\%s:\n     ref: %s (%s)\n   other: %s (%s)\n'
                  % (path, k, ref[k], type(ref[k]), other[k], type(other[k])))
        out = out and ok
    return out and not extras

# Returns true if all of the contents of two cell arrays/lists match
#
# ref = reference item that defines the elements of the other cell array/list
# path = relative path of these items (used to trace through nested levels)
# verbose = print messages describing differences found
# strict = (no effect, but will be passed to match to evaluate elements
def match_cell(ref, other, path=None, verbose=None, strict=None):
    if path is None: path = ''
    if verbose is None: verbose = False
    if strict is None: strict = True
    if len(ref) == len(other):
        out = True
        for q in range(len(ref)):
            ok = match(ref[q], other[q], '%s[%d]' % (path,q), verbose, strict)
            out = out and ok
        return out
    else:
        if verbose:
            temp = path if len(path) > 0 else 'root'
            print('Length mismatch for %s' % temp)
        return False

# Returns true if all members of items are one of the allowed types specified
#   in 'types'
def loose_type_match(items, types):
    return all([any([type(i) is t for t in types]) for i in items])

# =====
# Find the index of the closest element to the reference data
def closest(ref, queries, thresh=None):
    if thresh is None: thresh = 0
    out_inds = []
    out_errs = []
    for q in range(len(queries)):
        print('Looking for {}'.format(queries[q]))
        diff = [abs(ref[k] - queries[q]) for k in range(len(ref))]
        print(diff)
        min_idx = numpy.argmin(diff)
        print(min_idx)
        if abs(diff[min_idx]) <= thresh:
            out_inds.append(min_idx)
            out_errs.append(ref[min_idx]-queries[q])
        else:
            out_inds.append(None)
            out_errs.append(ref[min_idx]-queries[q])
    return out_inds, out_errs
