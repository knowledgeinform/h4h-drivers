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
import os.path
import numpy as np
import h5py
import mats
from mats import Struct
from mats.log import debug
import mats.h5


if mats.cpp_backend:
    class CConfig(mats.mc.MATS_cconfig):
        def __init__(self):
            super().__init__()
else:
    class CConfig:
        _fields = ['config_dir', 'filename', 'version', 'note', 'time',
                   'sensor', 'detector', 'det_feat_len', 'classifier',
                   'cls_lang', 'cls_ver', 'cls_cfg', 'features', 'feat_lang',
                   'feat_ver', 'feat_cfg', 'feat_len', 'feat_norm', 'clinfo',
                   'threshold', 'ROC']

        def __init__(self):
            self.cfgDir = ''
            self.fn = ''
            self.ver = ''
            self.note = ''
            self.time = 0
            self.sensor = ''

            self.det = ''
    #        self.detlen = 0
            self.detfeatnorm = np.zeros((2, 0))

            self.feat = []
            self.featlang = []
            self.featver = []
            self.featcfg = []  # MATS_struct vector
            self.featlen = np.zeros((0,)).astype(np.int32)
            # NOTE: self.featnorm refers to only the feature normalization data.
            # To include the detector feature normalization data, use the
            # syntax self['feat_norm']
            self.featnorm = np.zeros((2, 0))

            self.cls = ''
            self.clslang = ''
            self.clsver = ''
            self.clscfg = Struct()

            self.clinfo = Struct()
            self.thresh = 0.0
            self.roc = []  # TODO

        def __repr__(self):
            return 'CConfig[{}]({}, {})'.format(
                self['filename'], self['sensor'], self['note'])

        def __str__(self):
            n = max([len(f) for f in self._fields])
            fmt = '  {0: >'+str(n)+'}: {1}\n'
            out = []
            for f in self._fields:
                if type(self[f]) is np.ndarray and self[f].size >= 10:
                    # Display abbreviated version of array indtead of contents
                    abbrev = f'array({self[f].shape}, dtype={self[f].dtype})'
                    out.append(fmt.format(f, abbrev))
                else:
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
            elif key == 'det_feat_len':
                return self.detfeatnorm.shape[1]
            elif key == 'classifier':
                return self.cls
            elif key == 'cls_lang':
                return self.clslang
            elif key == 'cls_ver':
                return self.clsver
            elif key == 'cls_cfg':
                return self.clscfg
            elif key == 'features':
                return self.feat
            elif key == 'feat_lang':
                return self.featlang
            elif key == 'feat_ver':
                return self.featver
            elif key == 'feat_cfg':
                return self.featcfg
            elif key == 'feat_len':
                # NOTE: Inconsistent w/ AtrConfig's feat_len, which is sum of
                # this. This should be feat_lens?
                return self.featlen
            elif key == 'feat_norm':
                return np.append(self.detfeatnorm, self.featnorm, axis=1)
            elif key == 'clinfo':
                return self.clinfo
            elif key == 'threshold':
                return self.thresh
            elif key == 'ROC':
                return self.roc
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
            elif key == 'classifier':
                self.cls = value
            elif key == 'cls_lang':
                self.clslang = value
            elif key == 'cls_ver':
                self.clsver = value
            elif key == 'cls_cfg':
                self.clscfg = value
            elif key == 'clinfo':
                self.clinfo = value
            elif key == 'threshold':
                self.thresh = value
            elif key == 'ROC':
                self.roc = value
            elif key in ['det_feat_len', 'features', 'feat_lang', 'feat_ver',
                         'feat_cfg', 'feat_len', 'feat_norm']:
                raise KeyError(f'Cannot set this field directly ({key}).')
            else:
                raise KeyError('Field does not exist ({})'.format(key))

        def set_det_feat_norm(self, norm):
            if len(self.feat) == 0:
                if norm.shape[0] == 2:
                    self.detfeatnorm = norm
                else:
                    raise RuntimeError('Det. feature norm. data must be 2xN')
            else:
                raise RuntimeError('Detector features must be added before '
                                   'regular features')

        def add_feature(self, name, lang, ver, norm, cfg):
            # NOTE: When loaded, feature norm data is of the form:
            #   [[mean_0, mean_1, ..., mean_N],
            #    [std_0,  std_1,  ..., std_N]]
            _, num_feat = norm.shape
            self.featlen.append(num_feat)
            self.feat.append(name)
            self.featlang.append(lang)
            self.featver.append(ver)
            self.featnorm = np.append(self.featnorm, norm, axis=1)
            self.featcfg.append(cfg)

        def remove_feature(self, index):
            if type(index) is not int:
                raise TypeError('Index must be an integer')
            if index < 0 or index >= self.feat.size():
                raise IndexError('Index is out of range')
            num_feat_keep = sum(self.featlen[:index])
            num_feat_rem = self.featlen[index]
            left = self.featnorm[:, :num_feat_keep]
            right = self.featnorm[:, (num_feat_keep+num_feat_rem):]
            self.featnorm = np.append(left, right, axis=1)
            self.featlen.pop(index)
            self.feat.pop(index)
            self.featlang.pop(index)
            self.featver.pop(index)
            self.featcfg.pop(index)

        def load(self, filename):
            if type(filename) is not str:
                raise TypeError('filename must be a string')
            debug('MINIMAL', f'Loading {filename} ...')
            with h5py.File(filename, 'r') as fid:
                self.fn = filename

                self.cls = mats.h5.get_string(fid, 'classifier')
                self.clscfg = mats.h5.get_mats_struct(fid, 'clscfg')
                self.clslang = mats.h5.get_string(fid, 'clslang')
                self.clsver = mats.h5.get_string(fid, 'clsver')

                self.det = mats.h5.get_string(fid, 'detector')
                detlen = int(mats.h5.get_value(fid, 'detfeatlen'))

                self.note = mats.h5.get_string(fid, 'note')
                self.sensor = mats.h5.get_string(fid, 'sensor')
                self.time = float(mats.h5.get_value(fid, 'time'))
                self.ver = mats.h5.get_string(fid, 'version')

                if '/feat' in fid.keys():
                    # Read feature fields
                    # NOTE: Feature normalization matrix in test files are
                    # stored differently
                    featnorm = fid['/featnorm'][:].transpose()
                    featlen = [int(x)
                               for x in mats.h5.get_array(fid, 'featlen')]
                    # Split feature norm data into detector and feature
                    # components
                    self.set_det_feat_norm(featnorm[:, 0:detlen])
                    assert(featnorm[:, detlen:].shape[1] == np.sum(featlen))
                    self.featnorm = featnorm[:, detlen:]

                    feat_names = mats.h5.get_string_list(fid, 'feat')
                    for n in feat_names:
                        self.featcfg.append(
                            mats.h5.get_mats_struct(fid, 'features/'+n))
                    self.feat = feat_names
                    self.featlen = featlen
                    self.featlang = mats.h5.get_string_list(fid, 'featlang')
                    self.featver = mats.h5.get_string_list(fid, 'featver')

        # NOTE: C version of this function only saves to self.fn
        def save(self, filename=None):
            if filename is None:
                filename = self.fn
            if type(filename) is not str:
                raise TypeError('filename must be a string')
            elif os.path.exists(filename):
                raise RuntimeError(f'CConfig file {filename} already exists')

            debug('MINIMAL', f'Saving {filename} ...')
            with h5py.File(filename, 'w') as fid:
                mats.h5.create_string(fid, 'classifier', self.cls)
                mats.h5.create_string(fid, 'clslang', self.clslang)
                mats.h5.create_string(fid, 'clsver', self.clsver)
                mats.h5.create_mats_struct(fid, 'clscfg', self.clscfg)

                mats.h5.create_string(fid, 'detector', self.det)
                mats.h5.create_array(fid, 'detfeatlen',
                                     np.array([self['det_feat_len']],
                                              dtype=np.uint64))

                mats.h5.create_string(fid, 'note', self.note)
                mats.h5.create_string(fid, 'sensor', self.sensor)
                mats.h5.create_array(fid, 'time', np.array([self.time]))
                mats.h5.create_string(fid, 'version', self.ver)

                mats.h5.create_string_list(fid, 'feat', self.feat)
                mats.h5.create_string_list(fid, 'featlang', self.featlang)
                mats.h5.create_array(
                    fid, 'featlen', np.array([self.featlen], dtype=np.uint64).T)
                # Save entire combined feature normalization matrix
                # NOTE: This is stored in test files differently than other
                # arrays
                fid['/featnorm'] = self['feat_norm'].transpose()
                mats.h5.create_string_list(fid, 'featver', self.featver)

                for q in range(len(self.feat)):
                    mats.h5.create_mats_struct(fid, f'features/{self.feat[q]}',
                                               self.featcfg[q])
