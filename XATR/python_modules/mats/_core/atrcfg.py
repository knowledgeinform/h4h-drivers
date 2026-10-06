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

# TODO - Check feature normalization data.  Test script yields odd warning.

import numpy as np
import os.path
import h5py
import mats
from mats import Struct, CConfig, DConfig
import mats.h5
from mats.log import debug


if mats.cpp_backend:
    class AtrConfig(mats.mc.MATS_atrconfig):
        def __init__(self):
            super().__init__()
else:
    class AtrConfig:
        _fields = ['version', 'note', 'time', 'sensor', 'stream', 'detector',
                   'det_feat_len', 'classifier', 'normalizer', 'feat_lens',
                   'feat_len', 'features', 'feat_modules']

        def __init__(self):
            self.cfgDir = ''
            self._fn = ''

            self._ver = ''
            self._note = ''
            self._time = 0.0
            self._sensor = ''

            self._stream = {'name': '', 'version': '', 'interface': ''}
            self._det = {'name': '', 'version': '', 'interface': ''}
            self._cls = {'name': '', 'version': '', 'interface': ''}
            self._norm = {'name': '', 'version': '', 'interface': ''}

            self.detcfg = Struct()
            self.clscfg = Struct()
            self.normcfg = Struct()

    #        self.detlen = 0
            self.detfeatnorm = np.zeros((2, 0))

            self.feat = []
            self.featlang = []
            self.featver = []
            self.featcfg = []  # MATS_struct vector
            self.featlen = np.zeros((0,)).astype(np.int32)
            # NOTE: self.featnorm refers to only the feature normalization data.
            #   To include the detector feature normalization data, use the
            #   syntax
            #  self['feat_norm']
            self.featnorm = np.zeros((2, 0))

            # Contact loading info can be quite large, so this it will only be
            #   loaded if requested
            self.clinfo = []

        def __repr__(self):
            return 'AtrConfig[{}]({}, {})'.format(
                self['filename'], self['sensor'], self['stream'])

        def __str__(self):
            fields = ['version', 'note', 'time', 'sensor', 'stream', 'detector',
                      'det_feat_len', 'classifier', 'normalizer', 'feat_lens',
                      'feat_len', 'features']
            n = max([len(f) for f in fields])
            fmt = '  {0: >'+str(n)+'}: {1}\n'
            out = []
            for f in self._fields:
                out.append(fmt.format(f, repr(getattr(self, f))))
            return ''.join(out)

        @property
        def version(self):
            return self._ver

        @version.setter
        def version(self, val):
            self._ver = val

        @property
        def note(self):
            return self._note

        @note.setter
        def note(self, val):
            if type(val) != str:
                raise ValueError('Note must be a string.')
            self._note = val

        @property
        def time(self):
            return self._time

        @time.setter
        def time(self, val):
            if not isinstance(val, float):
                raise ValueError('Time must be a float.')
            self._time = val

        @property
        def sensor(self):
            return self._sensor

        @sensor.setter
        def sensor(self, val):
            self._sensor = val

        @property
        def filename(self):
            return self._fn

        @filename.setter
        def filename(self, val):
            if type(val) != str:
                raise ValueError('Filename must be a string.')
            self._fn = val

        @property
        def stream(self):
            return self._stream['name']

        @stream.setter
        def stream(self, val):
            raise ValueError('Use set_stream method to set stream value.')

        @property
        def stream_ver(self):
            return self._stream['version']

        @stream_ver.setter
        def stream_ver(self, val):
            raise ValueError('Use set_stream method to set stream version '
                             'value.')

        @property
        def detector(self):
            return self._det['name']

        @detector.setter
        def detector(self, val):
            raise ValueError('Use set_detector method to set detector name.')

        @property
        def det_feat_len(self):
            return self.detfeatnorm.shape[1]

        @det_feat_len.setter
        def det_feat_len(self, val):
            raise ValueError('Use set_det_feat_norm method to set length of detector features.')

        @property
        def det_ver(self):
            return self._det['version']

        @det_ver.setter
        def det_ver(self, val):
            raise ValueError('Use set_detector method to set detector version.')

        @property
        def det_lang(self):
            return self._det['interface']

        @det_lang.setter
        def det_lang(self, val):
            raise ValueError('Use set_detector method to set detector '
                             'interface.')

        @property
        def classifier(self):
            return self._cls['name']

        @classifier.setter
        def classifier(self, val):
            raise ValueError('Use set_classifier method to set classifier '
                             'name.')

        @property
        def cls_ver(self):
            return self._cls['version']

        @cls_ver.setter
        def cls_ver(self, val):
            raise ValueError('Use set_classifier method to set classifier '
                             'version.')

        @property
        def cls_lang(self):
            return self._cls['interface']

        @cls_lang.setter
        def cls_lang(self, val):
            raise ValueError('Use set_classifier method to set classifier '
                             'interface.')

        @property
        def feat_len(self):
            return int(sum(self.featlen.flatten())) + self.det_feat_len

        @property
        def feat_lens(self):
            return self.featlen

        @property
        def feat_modules(self):
            return self['feat_modules']

        @property
        def features(self):
            return self.feat

        @property
        def normalizer(self):
            return self._norm['name']

        @normalizer.setter
        def normalizer(self, val):
            raise ValueError('Use set_normalizer method to set normalizer '
                             'name.')

        @property
        def norm_ver(self):
            return self._norm['version']

        @norm_ver.setter
        def norm_ver(self, val):
            raise ValueError('Use set_normalizer method to set normalizer '
                             'version.')

        @property
        def norm_lang(self):
            return self._norm['interface']

        @norm_lang.setter
        def norm_lang(self, val):
            raise ValueError('Use set_normalizer method to set normalizer '
                             'interface.')

        def __getitem__(self, key):
            if key == 'det_feat_len':
                return self.detfeatnorm.shape[1]
            # Total number of features (includes detector features)
            elif key == 'feat_len':
                return int(sum(self.featlen.flatten())) + self['det_feat_len']
            elif key == 'feat_lens':
                return self.featlen
            elif key == 'features':
                return self.feat
            elif key == 'feat_norm':
                return np.append(self.detfeatnorm, self.featnorm, axis=1)
            elif key == 'feat_modules':
                feats = []
                for k in range(len(self.feat)):
                    feats.append({'name': self.feat[k],
                                  'interfaceName': self.featlang[k],
                                  'version': self.featver[k]})
                return feats
            elif key == 'stream_module':
                return self._stream
            elif key == 'normalizer_module':
                return self._norm
            elif key == 'detector_module':
                return self._det
            elif key == 'classifier_module':
                return self._cls
            elif key == 'config_dir':
                return self.cfgDir
            elif key == 'cls_cfg':
                return self.clscfg
            elif key == 'det_cfg':
                return self.detcfg
            elif key == 'norm_cfg':
                return self.normcfg
            elif key == 'clinfo':
                if not self.clinfo:
                    self._load_clinfo()
                return self.clinfo
            raise KeyError('Field does not exist ({})'.format(key))

        def __setitem__(self, key, value):
            if key == 'config_dir':
                self.cfgDir = value
            elif key == 'det_feat_norm':
                raise NotImplementedError()
            else:
                raise KeyError('Field does not exist ({})'.format(key))

        def set_stream(self, stream, stream_ver):
            self._stream['name'] = stream
            self._stream['version'] = stream_ver

        def set_detector(self, name, lang, ver, cfg):  # cfg = MATS_struct
            self._det['name'] = name
            self._det['interface'] = lang
            self._det['version'] = ver
            self.detcfg = cfg
            # Reset detector normalization data (will be overwritten later if
            #   applicable)
            self.set_det_feat_norm(np.zeros((2, 0)))

        def set_det_feat_norm(self, norm):
            if len(self.feat) == 0:
                if norm.shape[0] == 2:
                    self.detfeatnorm = norm
                else:
                    raise RuntimeError('Det. feature norm. data must be 2xN')
            else:
                raise RuntimeError('Detector features must be added before '
                                   'regular features')

        def set_classifier(self, name, lang, ver, cfg):  # cfg = MATS_struct
            self._cls['name'] = name
            self._cls['interface'] = lang
            self._cls['version'] = ver
            self.clscfg = cfg

        def set_normalizer(self, name, lang, ver, cfg):  # cfg = MATS_struct
            self._norm['name'] = name
            self._norm['interface'] = lang
            self._norm['version'] = ver
            self.normcfg = cfg

        def add_feature(self, name, lang, ver, norm, cfg):
            # TODO check inputs
            self.feat.append(name)
            self.featlang.append(lang)
            self.featver.append(ver)
            self.featcfg.append(cfg)
            self.featlen = np.append(self.featlen, int(norm.size/2))
            if norm.size > 0:
                self.featnorm = np.append(self.featnorm, norm, axis=1)
            else:
                print('Empty feature normalization matrix detected')

        def feature_config(self, index):
            return self.featcfg[index]

        # Make a new classifier configuration structure with this data
        def cconfig(self, fn=None):
            ccfg = CConfig()
            fields = ['config_dir', 'version', 'note', 'sensor', 'time',
                      'classifier', 'cls_lang', 'cls_ver', 'cls_cfg',
                      'detector']
            for field in fields:
                ccfg[field] = self[field]

            ccfg.detfeatnorm = self.detfeatnorm     # implicitly handles detlen

            ccfg.feat = self.feat
            ccfg.featlang = self.featlang
            ccfg.featver = self.featver
            ccfg.featcfg = self.featcfg
            # NOTE: atrcfg.featlen is numpy.array (uint64); ccfg.featlen is list
            #   of int.  Not sure if this intentional
            ccfg.featlen = [int(x) for x in self.featlen.flatten()]
            ccfg.featnorm = self.featnorm

    #        ccfg.thresh = self.thresh
            if fn is not None:
                ccfg['filename'] = fn
                ccfg.save()
            return ccfg

        # Make a new detector configuration structure with this data
        def dconfig(self, fn=None):
            dcfg = DConfig()

            fields = ['config_dir', 'version', 'note', 'time', 'sensor',
                      'detector', 'det_cfg', 'normalizer', 'norm_cfg']
            for field in fields:
                dcfg[field] = self[field]

            dcfg.detlang = self.det_lang
            dcfg.detver = self.det_ver
            dcfg.normlang = self.norm_lang
            dcfg.normver = self.norm_ver

            if fn is not None:
                dcfg['filename'] = fn
                dcfg.save()
            return dcfg

        def create_from(self, dcfg, ccfg):
            # TODO: Detector features should be included here when implemented
            for fld in ['version', 'note', 'time', 'sensor', 'config_dir']:
                self[fld] = ccfg[fld]
            self['filename'] = ''
            self.set_detector(dcfg['detector'], dcfg['det_lang'],
                              dcfg['det_ver'], dcfg['det_cfg'])
            self.set_normalizer(dcfg['normalizer'], dcfg['norm_lang'],
                                dcfg['norm_ver'], dcfg['norm_cfg'])
            self.set_classifier(ccfg['classifier'], ccfg['cls_lang'],
                                ccfg['cls_ver'], ccfg['cls_cfg'])
            self.set_stream('MATS_Python', '1.0')

    #        print('in create_from: {}'.format(ccfg))
            ix = ccfg['det_feat_len']
            # Split feature norm data into detector and feature components
            self.set_det_feat_norm(ccfg['feat_norm'][:, 0:ix])
            for k in range(len(ccfg['features'])):
                # NOTE: ccfg['feat_len'] corresponds to atrcfg['feat_lens'] and
                #   is the vector of lengths for each feature module
                feat_norm = ccfg['feat_norm'][:, ix:ix+ccfg['feat_len'][k]]
                ix += ccfg['feat_len'][k]
                self.add_feature(ccfg['features'][k], ccfg['feat_lang'][k],
                                 ccfg['feat_ver'][k], feat_norm,
                                 ccfg['feat_cfg'][k])

        # Load AtrConfig
        def load(self, filename):
            if type(filename) is not str:
                raise TypeError('filename must be a string')
            debug('MINIMAL', f'Loading {filename} ...')
            with h5py.File(filename, 'r') as fid:
                self._fn = filename
                self.note = mats.h5.get_string(fid, 'note')
                self.sensor = mats.h5.get_string(fid, 'sensor')
                self.time = mats.h5.get_value(fid, 'time')
                self.version = mats.h5.get_string(fid, 'version')

                self._stream['name'] = mats.h5.get_string(fid, 'stream')
                self._stream['version'] = mats.h5.get_string(fid, 'streamver')

                self._cls['name'] = mats.h5.get_string(fid, 'classifier')
                self._cls['interface'] = mats.h5.get_string(fid, 'clslang')
                self._cls['version'] = mats.h5.get_string(fid, 'clsver')
                self.clscfg = mats.h5.get_mats_struct(fid, 'clscfg')

                self._det['name'] = mats.h5.get_string(fid, 'detector')
                self._det['interface'] = mats.h5.get_string(fid, 'detlang')
                self._det['version'] = mats.h5.get_string(fid, 'detver')
                detlen = mats.h5.get_value(fid, 'detfeatlen')  # TODO FIX
                self.detcfg = mats.h5.get_mats_struct(fid, 'detcfg')

                self._norm['name'] = mats.h5.get_string(fid, 'normalizer')
                self._norm['interface'] = mats.h5.get_string(fid, 'normlang')
                self._norm['version'] = mats.h5.get_string(fid, 'normver')
                self.normcfg = mats.h5.get_mats_struct(fid, 'normcfg')

                if '/feat' in fid.keys():
                    # Read feature fields
                    # NOTE: Feature normalization matrix in test files are
                    # stored differently
                    featnorm = fid['/featnorm'][:].transpose()
                    featlen = mats.h5.get_array(fid, 'featlen')
                    # Split feature norm data into detector and feature
                    # components
                    self.set_det_feat_norm(featnorm[:, 0:detlen])
                    # print('{} =?= {}'.format(featnorm[:,detlen:].shape[1],
                    #                          np.sum(featlen)))
                    assert(featnorm[:, detlen:].shape[1] == np.sum(featlen))
                    self.featnorm = featnorm[:, detlen:]

                    feat_names = mats.h5.get_string_list(fid, 'feat')
                    for n in feat_names:
                        self.featcfg.append(
                            mats.h5.get_mats_struct(fid, 'features/'+n))
                    self.feat = feat_names
                    # self.featlen = featlen
                    self.featlen = np.array(featlen.flat)   # shape (N,1)->(N,)
                    self.featlang = mats.h5.get_string_list(fid, 'featlang')
                    self.featver = mats.h5.get_string_list(fid, 'featver')

        # Save AtrConfig
        def save(self, filename=None):
            if filename is None:
                filename = self._fn
            if type(filename) is not str:
                raise TypeError('filename must be a string')
            elif os.path.exists(filename):
                raise RuntimeError(f'AtrConfig file {filename} already exists')

            debug('MINIMAL', f'Saving {filename} ...')
            with h5py.File(filename, 'w') as fid:
                mats.h5.create_string(fid, 'classifier', self._cls['name'])
                mats.h5.create_string(fid, 'clslang', self._cls['interface'])
                mats.h5.create_string(fid, 'clsver', self._cls['version'])
                mats.h5.create_mats_struct(fid, 'clscfg', self.clscfg)

                mats.h5.create_string(fid, 'detector', self._det['name'])
                mats.h5.create_string(fid, 'detlang', self._det['interface'])
                mats.h5.create_array(fid, 'detfeatlen',
                                     np.array([self['det_feat_len']],
                                              dtype=np.uint64))
                mats.h5.create_string(fid, 'detver', self._det['version'])
                mats.h5.create_mats_struct(fid, 'detcfg', self.detcfg)

                mats.h5.create_string(fid, 'normalizer', self.normalizer)
                mats.h5.create_string(fid, 'normlang', self.norm_lang)
                mats.h5.create_string(fid, 'normver', self.norm_ver)
                mats.h5.create_mats_struct(fid, 'normcfg', self.normcfg)

                mats.h5.create_string(fid, 'note', self.note)
                mats.h5.create_string(fid, 'sensor', self.sensor)
                mats.h5.create_string(fid, 'stream', self.stream)
                mats.h5.create_string(fid, 'streamver', self.stream_ver)
                mats.h5.create_array(fid, 'time', np.array([self.time]))
                mats.h5.create_string(fid, 'version', self.version)

                mats.h5.create_string_list(fid, 'feat', self.feat)
                mats.h5.create_string_list(fid, 'featlang', self.featlang)
                mats.h5.create_array(fid, 'featlen', np.array([self.featlen]).T)
                # mats.h5.create_array(fid, 'featlen', self.featlen)
                # mats.h5.create_array(fid, 'featlen',
                #                      np.array(self.featlen, dtype=np.uint64))

                # Save entire combined feature normalization matrix
                # NOTE: This is stored in test files differently than other
                # arrays
                fid['/featnorm'] = self['feat_norm'].transpose()
                mats.h5.create_string_list(fid, 'featver', self.featver)

                num_feats = len(self.feat)
                for q in range(num_feats):
                    mats.h5.create_mats_struct(fid, f'features/{self.feat[q]}',
                                               self.featcfg[q])

        # Load contact loading info from file on demand
        def _load_clinfo(self):
            if not os.path.exists(self._fn):
                raise FileNotFoundError('atrcfg file %s not found', self._fn)
            with h5py.File(self._fn) as fid:
                self.clinfo = mats.h5.get_mats_struct(fid['clinfo'])
