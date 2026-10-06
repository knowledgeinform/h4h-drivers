"""
DISTRIBUTION STATEMENT D. Distribution authorized to the Department of
Defense and U.S. DoD contractors only; Administrative or Operational Use; 1
Jan 2017. Other U.S. requests shall be referred to Naval Surface Warfare
Center Panama City Division, ATTN: Technical Director NSWC PCD, 110 Vernon
Ave, Panama City, FL 32407.

POC:

Bradley Marchand
NSWC Panama City Division, Code X24 (850)-230-7385
bradley.marchand@navy.mil

Derek Kolacinski
NSWC Panama City Division, Code X23 (850)-230-7218
derek.kolacinski@navy.mil
"""
import numpy
import mats


if mats.cpp_backend:
    class Cell(mats.mc.MATS_cell):
        def __init__(self, val=None):
            super().__init__(val)
else:
    class Cell:

        def __init__(self):
            self.data = []
            self._dims = (0, 0)

        def __repr__(self):
            if len(self.data) > 0:
                fv = ','.join([str(x) for x in self.data])
                fv = str(len(self.data))
            else:
                fv = '<EMPTY>'
            return 'Cell({0})'.format(fv)

        def __getitem__(self, index):
            return self.get(index)

        def __setitem__(self, index, value):
            self.set(index, value)

        def __iter__(self):
            for key in range(len(self.data)):
                yield self.get(key)

        def __len__(self):
            return len(self.data)

        def resize(self, numrows, numcols):
            new_data = [None for x in range(numrows*numcols)]
            old_numrows, old_numcols = self._dims
            for r in range(min([old_numrows, numrows])):
                for c in range(min([old_numcols, numcols])):
                    old_index = c*old_numrows + r
                    new_index = c*numrows + r
                    if new_index < numrows*numcols:
                        new_data[new_index] = self.data[old_index]
            self.data = new_data
            self._dims = (numrows, numcols)

        def size(self, index):
            if index < len(self.data):
                element = self.data[index]
                if element is None:
                    return 0
                elif type(element) is numpy.ndarray:
                    return element.size
                else:
                    try:
                        return len(element)
                    except:  # TODO: other cases?
                        return 1
            else:
                return []

        def dims(self):
            return self._dims

        def type(self, index):
            return type(self.data[index])

        def clear(self):
            for q in range(len(self.data)):
                self.data[q] = None

        def get(self, index):
            if index < len(self.data):
                return self.data[index]
            else:
                raise IndexError('Index is out of range.')

        def set(self, index, value):
            if index < len(self.data):
                self.data[index] = value
            else:
                raise IndexError('Index is out of range.')
