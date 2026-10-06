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
import copy
import mats


if mats.cpp_backend:
    class Ecdata(mats.mc.MATS_ecdata):
        def __init__(self):
            super().__init__()


    class EcdataList(mats.mc.MATS_ecdata_list):
        def __init__(self):
            super().__init__()
else:
    class Ecdata:
        _fields = ['id', 'uuid', 'sensor', 'lat', 'lon', 'heading', 'time',
                   'height', 'detscore', 'groupnum', 'groupconf', 'grouplat',
                   'grouplon', 'groupcovmat', 'snippet_names']

        def __init__(self):
            self.id = 0
            self.uuid = ''
            self.sensor = ''
            self.detscore = -99

            self.snippets = {}
            self.image_sizes = {}

            self.lat = 0
            self.lon = 0
            self.heading = -99
            self.time = -99
            self.height = -99

            self.groupnum = 0
            self.groupconf = -99
            self.grouplat = 0
            self.grouplon = 0
            self._groupcovmat = numpy.zeros((2,2)).astype(numpy.float32)

        def __repr__(self):
            bands = self.snippetNames()
            bstr = ', '.join(bands)
            fmt = '[{0} | '+bstr+']'
            return fmt.format(self['uuid'])

        def __str__(self):
            n = max([len(f) for f in self._fields])
            fmt = '  {0: >'+str(n)+'}: {1}\n'
            out = []
            for f in self._fields:
                out.append(fmt.format(f, str(self[f])))

            bands = self.snippetNames()
            bstr = ', '.join(bands)
            out.append(fmt.format('snippets', bstr))
            return ''.join(out)

        def __getitem__(self, key):
            if key == 'id':
                return self.id
            elif key == 'uuid':
                return self.uuid
            elif key == 'sensor':
                return self.sensor
            elif key == 'lat':
                return self.lat
            elif key == 'lon':
                return self.lon
            elif key == 'heading':
                return self.heading
            elif key == 'time':
                return self.time
            elif key == 'height':
                return self.height
            elif key == 'detscore':
                return self.detscore
            elif key == 'groupnum':
                return self.groupnum
            elif key == 'groupconf':
                return self.groupconf
            elif key == 'grouplat':
                return self.grouplat
            elif key == 'grouplon':
                return self.grouplon
            elif key == 'groupcovmat':
                return self.groupcovmat()
            elif key == 'snippet_names':
                return self.snippetNames()
            raise KeyError('Field does not exist ({})'.format(key))

        def __setitem__(self, key, value):
            if key == 'id':
                self.id = value
            elif key == 'uuid':
                self.uuid = value
            elif key == 'sensor':
                self.sensor = value
            elif key == 'lat':
                self.lat = value
            elif key == 'lon':
                self.lon = value
            elif key == 'heading':
                self.heading = value
            elif key == 'time':
                self.time = value
            elif key == 'height':
                self.height = value
            elif key == 'detscore':
                self.detscore = value
            elif key == 'groupnum':
                self.groupnum = value
            elif key == 'groupconf':
                self.groupconf = value
            elif key == 'grouplat':
                self.grouplat = value
            elif key == 'grouplon':
                self.grouplon = value
            elif key == 'groupcovmat':
                self.set_groupcovmat(value)
            elif key in ['snippet_names']:
                raise KeyError('Cannot set this field directly ({}).'.format(key))
            else:
                raise KeyError('Field does not exist ({})'.format(key))

        def __contains__(self, key):
            return (key in self._fields)

        def __iter__(self):
            for field in self._fields:
                yield field

        def keys(self):
            return self._fields.copy()

        def groupcovmat(self):
            return self._groupcovmat

        def set_groupcovmat(self, cov):
            if type(cov) is not numpy.ndarray:
                raise TypeError('cov must be a numpy array')
            if cov.ndim != 2 or cov.shape[0] != 2 or cov.shape[1] != 2:
                raise TypeError('cov must 2x2 numpy array')
            # NOTE: There are some flags set here in the .pyx file; are they
            #   necessary/applicable here?
            self._groupcovmat = cov.astype(numpy.float32)

        def get_size(self, band_str):
            if band_str in self.image_sizes.keys():
                return (self.image_sizes[band_str]['anum'],
                        self.image_sizes[band_str]['cnum'])

        # Set the dimensions of the original source image
        # (NOTE: band_str must correspond to an existing sensor band)
        def set_size(self, band_str, anum, cnum):
            if type(band_str) is not str:
                raise TypeError('band_str must be a string')
            if type(anum) is not int or anum < 0:
                raise TypeError('anum must be a positive integer')
            if type(cnum) is not int or cnum < 0:
                raise TypeError('cnum must be a positive integer')
            if band_str in self.snippets.keys():
                self.image_sizes[band_str] = {'anum':anum, 'cnum':cnum}

        def snippetNames(self):
            return [x for x in self.snippets.keys()]

        def snippet(self, band_str):
            if type(band_str) is not str:
                raise TypeError('band_str must be a string')
            if band_str not in self.snippetNames():
                raise KeyError('{} is not a valid band name'.format(band_str))
            return self.snippets[band_str]

        def set_snippet(self, band_str, snip):
            if type(band_str) is not str:
                raise TypeError('band_str must be a string')
            # TODO: check that snip is also the correct type
            self.snippets[band_str] = snip

    #    def load_input


    class EcdataList:
        def __init__(self):
            self.data = []

        def __repr__(self):
            return 'MATS_ecdata_list ({0} contacts)'.format(self.size())

        def __getitem__(self, index):
            if type(index) is not int:
                raise TypeError('Index must be an integer')
            if index < 0 or index >= self.size():
                raise IndexError('Index is out of range')
            return self.data[index]

        def __setitem__(self, index, value):
            if type(index) is not int:
                raise TypeError('Index must be an integer')
            if index < 0 or index >= self.size():
                raise IndexError('Index is out of range')
            if type(value) is not Ecdata:
                raise TypeError('value must be an Ecdata object')
            self.data[index] = value
    #        self.data[index] = copy.deepcopy(value) # causes disagreements w/ C version

        def __iter__(self):
            for key in range(self.size()):
                yield self[key]

        def __len__(self):
            return self.size()

        def clear(self):
            self.data.clear()

        def resize(self, new_len):
            if type(new_len) is not int and new_len > 0:
                raise TypeError('Index must be a positive integer')
            n = self.size()
            new_data = [self.data[x] if x < n else Ecdata()
                                     for x in range(new_len)]
            self.data = new_data

        def size(self):
            return len(self.data)

        def append(self, value):
            if type(value) is not Ecdata:
                raise TypeError('value must be an Ecdata object')
            self.data.append(copy.deepcopy(value))

        def pop(self, index=None):
            return self.data.pop(index)
