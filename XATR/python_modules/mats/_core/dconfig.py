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
import h5py
import os.path
import numpy as np
import mats
from mats import Struct
import mats.h5


if mats.cpp_backend:
    class DConfig(mats.mc.MATS_dconfig):
        def __init__(self):
            super().__init__()
else:
    class DConfig:
        _fields = ['config_dir', 'filename', 'version', 'note', 'time',
                   'sensor', 'detector', 'det_lang', 'det_ver', 'det_cfg',
                   'normalizer', 'norm_lang', 'norm_ver', 'norm_cfg']

        def __init__(self):
            self.cfgDir = ''
            self.fn = ''

            self.ver = ''
            self.note = ''
            self.time = 0.0
            self.sensor = ''

            self.stream = ''
            self.streamver = ''

            self.det = ''
            self.detlang = ''
            self.detver = ''
            self.detcfg = Struct()

            self.normalizer = ''
            self.normlang = ''
            self.normver = ''
            self.normcfg = Struct()

        def __repr__(self):
            return 'DConfig[{}]({}, {})'.format(
                self['filename'], self['sensor'], self['note'])

        def __str__(self):
            n = max([len(f) for f in self._fields])
            fmt = '  {0: >'+str(n)+'}: {1}\n'
            out = []
            for f in self._fields:
                out.append(fmt.format(f, repr(self[f])))
            return ''.join(out)

        def __getitem__(self, key):
            if key == 'config_dir':
                return self.cfgDir
            elif key == 'filename':
                return self.fn
            elif key == 'version':
                return self.ver
            elif key == 'note':
                return self.note
            elif key == 'time':
                return self.time
            elif key == 'sensor':
                return self.sensor
            elif key == 'detector':
                return self.det
            elif key == 'det_lang':
                return self.detlang
            elif key == 'det_ver':
                return self.detver
            elif key == 'det_cfg':
                return self.detcfg
            elif key == 'normalizer':
                return self.normalizer
            elif key == 'norm_lang':
                return self.normlang
            elif key == 'norm_ver':
                return self.normver
            elif key == 'norm_cfg':
                return self.normcfg
            raise KeyError('Field does not exist ({})'.format(key))

        def __setitem__(self, key, value):
            if key == 'config_dir':
                self.cfgDir = value
            elif key == 'filename':
                self.fn = value
            elif key == 'version':
                self.ver = value
            elif key == 'note':
                self.note = value
            elif key == 'time':
                self.time = value
            elif key == 'sensor':
                self.sensor = value
            elif key == 'detector':
                self.det = value
            elif key == 'det_lang':
                self.detlang = value
            elif key == 'det_ver':
                self.detver = value
            elif key == 'det_cfg':
                self.detcfg = value
            elif key == 'normalizer':
                self.normalizer = value
            elif key == 'norm_lang':
                self.normlang = value
            elif key == 'norm_ver':
                self.normver = value
            elif key == 'norm_cfg':
                self.normcfg = value
            else:
                raise KeyError('Field does not exist ({})'.format(key))

        def __contains__(self, key):
            return key in self._fields

        def __iter__(self):
            for field in self._fields:
                yield field

        def keys(self):
            return self._fields.copy()

        def load(self, filename):
            if type(filename) is not str:
                raise TypeError('filename must be a string')
            print('Loading %s ...' % filename)
            with h5py.File(filename, 'r') as fid:
                self.ver = mats.h5.get_string(fid, 'version')
                self.note = mats.h5.get_string(fid, 'note')
                self.time = mats.h5.get_value(fid, 'time')
                self.sensor = mats.h5.get_string(fid, 'sensor')
                self.det = mats.h5.get_string(fid, 'detector')
                self.detlang = mats.h5.get_string(fid, 'detlang')
                self.detver = mats.h5.get_string(fid, 'detver')
                self.detcfg = mats.h5.get_mats_struct(fid, 'detcfg')
                self.normalizer = mats.h5.get_string(fid, 'normalizer')
                self.normlang = mats.h5.get_string(fid, 'normlang')
                self.normver = mats.h5.get_string(fid, 'normver')
                self.normcfg = mats.h5.get_mats_struct(fid, 'normcfg')

        # NOTE: C version of this function only saves to self.fn, but that seems
        #   potentially dangerous with all the loading and saving occurring in
        #   the test cases
        def save(self, filename=None):
            if filename is None:
                filename = self.fn
            if type(filename) is not str:
                raise TypeError('filename must be a string')
            elif os.path.exists(filename):
                raise RuntimeError(f'DConfig file {filename} already exists')
            print('Saving %s ...' % filename)
            with h5py.File(filename, 'w') as fid:
                mats.h5.create_string(fid, 'version', self.ver)
                mats.h5.create_string(fid, 'note', self.note)
                mats.h5.create_array(fid, 'time', np.array([self.time]))
                mats.h5.create_string(fid, 'sensor', self.sensor)

                mats.h5.create_string(fid, 'detector', self.det)
                mats.h5.create_string(fid, 'detlang', self.detlang)
                mats.h5.create_string(fid, 'detver', self.detver)
                mats.h5.create_mats_struct(fid, 'detcfg', self.detcfg)

                mats.h5.create_string(fid, 'normalizer', self.normalizer)
                mats.h5.create_string(fid, 'normlang', self.normlang)
                mats.h5.create_string(fid, 'normver', self.normver)
                mats.h5.create_mats_struct(fid, 'normcfg', self.normcfg)
