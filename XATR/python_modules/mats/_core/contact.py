# DISTRIBUTION STATEMENT D. Distribution authorized to the Department of
# Defense and U.S. DoD contractors only; Administrative or Operational Use; 1
# Jan 2017. Other U.S. requests shall be referred to Naval Surface Warfare
# Center Panama City Division, ATTN: Technical Director NSWC PCD, 110 Vernon
# Ave, Panama City, FL 32407.
import numpy
import copy
import mats


if mats.cpp_backend:
    class Contact(mats.mc.MATS_contact):
        def __init__(self):
            super().__init__()


    class ContactList(mats.mc.MATS_contact_list):
        def __init__(self):
            super().__init__()
else:
    class Contact:
        """
        Main MATS contact data container.

        Attributes:
          x: Contact cross-track pixel location.
          y: Contact along-track pixel location.
          fn: Input data filename.

        """
        _fields = ['id', 'x', 'y', 'filename', 'side', 'normalizer', 'detector',
                   'classifier', 'contcorr', 'gt', 'type', 'cls', 'classconf',
                   'uuid', 'featureset', 'features']

        def __init__(self):
            self.id = 0     # obsolete?
            self._x = 0
            self._y = 0
            self.features = numpy.zeros((0,)).astype(numpy.float64)
            self._fn = ''
            self._side = ''
            self.gt = -99
            self.normalizer = ''
            self.detector = ''
            self.featureset = []
            self.classifier = ''
            self.cls = -99
            self._classconf = -99
            self.type = -99
            self.contcorr = ''
            self.opfeedback = {'opdisplay':0, 'opconf':-99, 'type':-99}
            self.status = 'accepted'
            self.ecdata_fn = ''
            self.uuid = ''

        def __repr__(self):
            return f'[{self._fn} {self._side} @ '\
                   f'({self._x}, {self._y}) - {self._classconf}]'

        def __str__(self):
            n = max([len(f) for f in self._fields])
            fmt = '  {0: >'+str(n)+'}: {1}\n'
            out = []
            for f in self._fields:
                out.append(fmt.format(f, repr(getattr(self, f))))
            return ''.join(out)

        @property
        def x(self):
            return self._x

        @x.setter
        def x(self, val):
            self._x = val

        @property
        def y(self):
            return self._y

        @y.setter
        def y(self, val):
            self._y = val

        @property
        def filename(self):
            return self._fn

        @filename.setter
        def filename(self, val):
            self._fn = val

        @property
        def side(self):
            return self._side

        @side.setter
        def side(self, val):
            self._side = val

        @property
        def classconf(self):
            return self._classconf

        @classconf.setter
        def classconf(self, val):
            self._classconf = val

        def __getitem__(self, key):
            if key in ['x', 'y', 'filename', 'side', 'classconf']:
                raise DeprecationWarning(f'Use Contact "{key}" property.')
            if key == 'id': return self.id
            elif key == 'gt': return self.gt
            elif key == 'type': return self.type
            elif key == 'cls': return self.cls
            elif key == 'uuid': return self.uuid
            elif key == 'normalizer': return self.normalizer
            elif key == 'detector': return self.detector
            elif key == 'classifier': return self.classifier
            elif key == 'contcorr': return self.contcorr
            elif key == 'featureset': return self.featureset
            elif key == 'features': return self.features
            raise KeyError('Field does not exist ({})'.format(key))

        def __setitem__(self, key, value):
            if key in ['x', 'y', 'filename', 'side', 'classconf']:
                raise DeprecationWarning(f'Use Contact "{key}" property.')
            if key == 'id': self.id = value
            elif key == 'gt': self.gt = value
            elif key == 'type': self.type = value
            elif key == 'cls': self.cls = value
            elif key == 'uuid': self.uuid = value
            elif key == 'normalizer': self.normalizer = value
            elif key == 'detector': self.detector = value
            elif key == 'classifier': self.classifier = value
            elif key == 'contcorr': self.contcorr = value
            elif key == 'featureset':
                if type(value) is str:
                    self.featureset = [value]
                else:
                    self.featureset = value
            elif key == 'features':
                if type(value) is numpy.ndarray:
                    self.features = value
                else:
                    print('features type = %s' % str(type(value)))
            else:
                raise KeyError('Field does not exist ({})'.format(key))

        def __contains__(self, key):
            return key in self._fields

        def __iter__(self):
            for field in self._fields:
                yield field

        def keys(self):
            return self._fields.copy()

        def set_location(self, x, y):
            self.x = x
            self.y = y

        # Incorporate new features and module label to respective fields
        def add_feature(self, name, new_feats):
            if type(new_feats) is not numpy.ndarray:
                raise TypeError('new_feats must be a numpy array')
            new_feats = new_feats.astype(numpy.float64).ravel('F')
            self.features = numpy.append(self.features, new_feats)
            self.featureset.append(name)

        def display(self):
            print(self)

        # Import data from another contact
        def copy(self, other):
            # NOTE: Some fields will not be copied over using this method, but
            # the ones left out look like they are not accessed by other
            # functions anyway
            if type(other) is type(self):
                for f in self._fields:
                    self[f] = other[f]
            else:
                raise TypeError('other must be a Contact')

    class ContactList:

        def __init__(self):
            self.contacts = []

        def __repr__(self):
            return 'ContactList ({0} contacts)'.format(len(self.contacts))

        def __getitem__(self, index):
            if type(index) is not int:
                raise TypeError('Index must be an integer')
            if index < 0 or index >= self.size():
                raise IndexError('Index is out of range')
            return self.contacts[index]

        def __setitem__(self, index, value):
            if type(index) is not int:
                raise TypeError('Index must be an integer')
            if index < 0 or index >= self.size():
                raise IndexError('Index is out of range')
            if type(value) is not Contact:
                raise TypeError('ContactLists may only contain contacts')
            self.contacts[index] = value

        def __iter__(self):
            for key in range(self.size()):
                yield self[key]

        def __len__(self):
            return self.size()

        def size(self):
            return len(self.contacts)

        def clear(self):
            self.contacts.clear()

        def resize(self, new_len):
            if type(new_len) is not int and new_len > 0:
                raise TypeError('Index must be a positive integer')
            n = self.size()
            new_data = [self.contacts[x] if x < n else Contact()
                        for x in range(new_len)]
            self.contacts = new_data

        def append(self, value):
            if type(value) is not Contact:
                raise TypeError('ContactLists may only contain contacts')
            self.contacts.append(copy.deepcopy(value))

        def pop(self, index=None):
            return self.contacts.pop(index)

        def filter(self, cond_tuple):
            return self.sublist(self.mask(cond_tuple))

        def mask(self, cond_tuple):
            out = numpy.ndarray((len(self),), dtype=bool)
            out.fill(False)
            field, op, val = cond_tuple
            if self.size() == 0:
                return out

            for q in range(len(self.contacts)):
                try:
                    x = self.contacts[q][field]
                    if op == '<':
                        out[q] = x < val
                    if op == '<=':
                        out[q] = x <= val
                    if op == '>':
                        out[q] = x > val
                    if op == '>=':
                        out[q] = x >= val
                    if op == '==':
                        out[q] = x == val
                except:
                    out[q] = False  # Redundant
            return out

        def sublist(self, mask):
            out = ContactList()
            for con, keep in zip(self.contacts, mask):
                if keep:
                    out.append(con)
            return out
