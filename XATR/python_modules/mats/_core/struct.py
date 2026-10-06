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
import mats

if mats.cpp_backend:
    class Struct(mats.mc.MATS_struct):
        def __init__(self):
            super().__init__()

        def __setitem__(self, key, value):
            self.set(key, value)
else:
    class Struct:
        def __init__(self):
            self.data = {}

        def __repr__(self):
            if self.size() > 0:
                fv = ','.join(self.data.keys())
            else:
                fv = '<EMPTY>'
            return 'Struct({0})'.format(fv)

        def __str__(self):
            if self.size() == 0:
                return '<EMPTY>'
            fields = self.data.keys()
            n = max([len(f) for f in fields])
            fmt = '  {0: >'+str(n)+'}: {1}\n'
            out = []
            for f in fields:
                g = self.get(f)
                out.append(fmt.format(f, str(g)))
            return ''.join(out)

        def __getitem__(self, key):
            if key not in self.data.keys():
                raise KeyError('Field does not exist ({})'.format(key))
            return self.get(key)

        def __setitem__(self, key, value):
            self.set(key, value)

        def __delitem__(self, key):
            self.data.pop(key)

        def __len__(self):
            return len(self.data)

        def __contains__(self, key):
            return self.isfield(key)

        def __iter__(self):
            for field in self.data.keys():
                yield field

        def set(self, key, value):
            if type(value) is not list:
                self.data[key] = [value]
            else:
                self.data[key] = value

        def get(self, key):
            x = self.data[key]
    #        print('get: '+str(type(x)))
            if len(x) == 1:
                return x[0]
            else:
                return x

        def remove(self, field):
            return self.data.pop(field)

        def size(self, name=None):
            if name is None:
                return len(self)
            else:
                return len(self.data[name])

        def type(self, name):
            return type(self.data[name])

        def isfield(self, name):
            return name in self.data.keys()

        def keys(self):
            return self.data.keys()

        def clear(self):
            self.data.clear()
