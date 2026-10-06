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
import numpy as np
import math
import mats


def dtype_np2mats(dtype: type):
    if dtype in [np.float64, np.complex128]:
        return 'DOUBLE'
    elif dtype in [np.float32, np.complex64]:
        return 'FLOAT'
    elif dtype == np.uint32:
        return 'UNSIGNED_INT'
    else:
        raise ValueError('Unsupported numpy dtype.')


def dtype_mats2np(dtype: str, is_complex: bool = False):
    if dtype == 'DOUBLE':
        if is_complex:
            return np.complex128
        else:
            return np.float64
    elif dtype == 'FLOAT':
        if is_complex:
            return np.complex64
        else:
            return np.float32
    elif dtype == 'UNSIGNED_INT':
        return np.uint32
    else:
        raise ValueError('Unsupported MATS dtype.')


def order_np2mats(order: str):
    if order == 'F':
        return 'COL_MAJOR'
    elif order == 'C':
        return 'ROW_MAJOR'
    else:
        raise ValueError('Unsupported np order.')


def order_mats2np(order: str):
    if order == 'COL_MAJOR':
        return 'F'
    elif order == 'ROW_MAJOR':
        return 'C'
    else:
        raise ValueError('Unsupported MATS storage.')


if mats.cpp_backend:
    class Data(mats.mc.MATS_data):
        def __init__(self):
            super().__init__()
else:
    class Data:
        _dtypes = ['DOUBLE', 'FLOAT', 'UNSIGNED_INT']
        _stypes = ['COL_MAJOR', 'ROW_MAJOR']
        _ftypes = ['REAL_IMAG', 'AMP_PHASE']
        _fields = ['precision', 'storage', 'format', 'anum', 'cnum', 'ares',
                   'cres', 'data']

        def __init__(self):
            self._precision = 'UNKNOWN'
            self._storage = 'COL_MAJOR'
            self._format = 'REAL_IMAG'
            self._res = [0.0, 0.0]
            self._data1 = None
            self._data2 = None

        def __repr__(self):
            if self._data1 is not None:
                sz = self._data1.shape
            else:
                sz = (0, 0)
            return 'MATS_data: {} x {} @ {} x {}'.format(
                sz[0], sz[1], self._res[0], self._res[1])

        @property
        def precision(self):
            return self._precision

        @property
        def storage(self):
            return self._storage

        @property
        def format(self):
            return self._format

        @property
        def anum(self):
            return self.size()[0]

        @property
        def cnum(self):
            return self.size()[1]

        @property
        def ares(self):
            return self._res[0]

        @property
        def cres(self):
            return self._res[1]

        @property
        def abs(self):
            if self.empty():
                return None
            if self.is_complex():
                if self.format == 'AMP_PHASE':
                    return np.copy(self.component(0))
                elif self.format == 'REAL_IMAG':
                    return np.abs(self.component(0) + 1j*self.component(1))
                raise RuntimeError(f'Unknown format ({self.format})')
            return np.abs(np.copy(self.component(0)))

        @property
        def phase(self):
            if self.empty():
                return None
            if self.is_complex():
                if self.format == 'AMP_PHASE':
                    return np.copy(self.component(1))
                elif self.format == 'REAL_IMAG':
                    return np.angle(
                        self.component(0) + 1j*self.component(1))
                raise RuntimeError(f'Unknown format ({self.format})')
            raise RuntimeError('Data is real')

        @property
        def real(self):
            if self.empty():
                return None
            if self.is_complex():
                if self.format == 'AMP_PHASE':
                    return np.copy(
                        self.component(0) * np.cos(self.component(1)))
                elif self.format == 'REAL_IMAG':
                    return np.copy(self.component(0))
                raise RuntimeError(f'Unknown format ({self.format})')
            return np.copy(self.component(0))

        @property
        def imag(self):
            if self.empty():
                return None
            if self.is_complex():
                if self.format == 'AMP_PHASE':
                    return np.copy(
                        self.component(0) * np.sin(self.component(1)))
                elif self.format == 'REAL_IMAG':
                    return np.copy(self.component(1))
                raise RuntimeError(f'Unknown format ({self.format})')
            raise RuntimeError('Data is real')

        @property
        def data(self):
            if self.empty():
                return None
            if self.is_complex():
                if self.format == 'REAL_IMAG':
                    return self.component(0) + 1j * self.component(1)
                elif self.format == 'AMP_PHASE':
                    out = np.cos(self.component(1)) \
                          + 1j * np.sin(self.component(1))
                    return self.component(0) * out
                raise RuntimeError(f'Unknown format ({self.format})')
            return np.copy(self.component(0))

        @precision.setter
        def precision(self, value):
            dt = None

            if value not in self._dtypes:
                raise ValueError(
                    'Value must be DOUBLE, FLOAT, or UNSIGNED_INT.')

            if not type(value) == 'str':
                ValueError('Input value must be a string.')
            if value == 'DOUBLE':
                dt = np.float64
            elif value == 'FLOAT':
                dt = np.float32
            elif value == 'UNSIGNED_INT':
                dt = np.uint32
            else:
                ValueError(f"Invalid value. Possible values are: "
                           f"{self._dtypes}")

            if self._data1 is not None:
                self._data1 = dt(self._data1)
            if self._data2 is not None:
                self._data2 = dt(self._data2)
            self._precision = value

        @storage.setter
        def storage(self, value):
            if value not in self._stypes:
                raise ValueError([
                    'Invalid storage value.',
                    'Possible values: COL_MAJOR, ROW_MAJOR.'
                ])
            self._storage = value

        @format.setter
        def format(self, value):
            if value not in self._ftypes:
                raise ValueError([
                    'Invalid format value.',
                    'Possible values: REAL_IMAG, AMP_PHASE'
                ])
            self._format = value

        @ares.setter
        def ares(self, value):
            self._res[0] = float(value)

        @cres.setter
        def cres(self, value):
            self._res[1] = float(value)

        @data.setter
        def data(self, value):
            if (value is None) or (type(value) is tuple and value == ()):
                self.clear()
            elif isinstance(value, tuple):
                self.load_data_as_tuple(value)
            self.load_data(value)

        @anum.setter
        def anum(self, value):
            raise KeyError("Cannot set 'anum' directly.")

        @cnum.setter
        def cnum(self, value):
            raise KeyError("Cannot set 'cnum' directly.")

        def __contains__(self, key):
            return key in self._fields

        def __iter__(self):
            for field in self._fields:
                yield field

        def __len__(self):
            return self.length()

        def keys(self):
            return self._fields.copy()

        def is_complex(self):
            return self._data2 is not None

        def empty(self):
            return self._data1 is None and self._data2 is None

        def length(self):
            return self._data1.size

        def size(self):
            if self._data1 is None:
                return 0, 0
            anum = self._data1.shape[0]
            cnum = self._data1.shape[1]
            return anum, cnum

        def clean(self):
            pass

        def clear(self):
            self._data1 = None
            self._data2 = None

        def set_resolution(self, ares, cres):
            self._res[0] = ares
            self._res[1] = cres

        def load_data(self, data: np.ndarray, amp_phase: bool = False):
            """
            This function forces the data to be column-major (Fortran
            contiguous). Input data must be a 2-D numpy array of a
            supported type (float, double, unsigned int, complex float, complex
            double).
            """
            if data.ndim != 2:
                raise ValueError('data must have 2 dimensions.')
            self.clear()
            # Always use column-major (Fortran) storage.
            self.storage = 'COL_MAJOR'
            if not data.flags['F_CONTIGUOUS']:
                data = np.asfortranarray(data)

            # The numpy array is in real/imag format unless specified otherwise.
            if amp_phase:
                self.format = 'AMP_PHASE'
            else:
                self.format = 'REAL_IMAG'

            self.precision = dtype_np2mats(data.dtype)
            if np.all(np.isreal(data)):
                self._data1 = np.copy(data)
            else:
                # Real part/magnitude (depending on format)
                self._data1 = np.asfortranarray(data.real)
                # Imaginary part/phase (depending on format)
                self._data2 = np.asfortranarray(data.imag)

        def load_data_as_tuple(self, data: tuple, amp_phase: bool = False):
            """
            This function forces the data to be column-major (Fortran
            contiguous). Input data must be a tuple containing 1 or 2 numpy
            arrays, where each array corresponds to a data component
            (real/imaginary or amplitude/phase).
            """

            # Check input.
            if len(data) < 1 or len(data) > 2:
                raise ValueError('data must contain 1 or 2 components.')

            if not isinstance(data[0], np.ndarray):
                raise TypeError('data component(s) must be numpy array(s).')
            if data[0].ndim != 2:
                raise ValueError('data component must have 2 dimensions.')
            anum = data[0].shape[0]
            cnum = data[0].shape[1]

            if len(data) == 2:
                if not isinstance(data[1], np.ndarray):
                    raise TypeError('data component(s) must be numpy array(s).')
                if data[1].ndim != 2:
                    raise ValueError('data component must have 2 dimensions.')
                if data[1].shape[0] != anum:
                    raise ValueError(
                        'data components must have the same dimensions.')
                if data[1].shape[1] != cnum:
                    raise ValueError(
                        'data components must have the same dimensions.')
                if data[1].dtype != data[0].dtype:
                    raise TypeError('data components must have the same type.')

            # The numpy arrays are in real/imag format unless specified
            # otherwise.
            if amp_phase:
                self.format = 'AMP_PHASE'
            else:
                self.format = 'REAL_IMAG'

            # Type the input data so we can access the numpy array members.
            realdata = data[0]
            if len(data) == 2:
                imagdata = data[1]

            # Always use column-major (Fortran) storage.
            self.storage = 'COL_MAJOR'
            if not realdata.flags['F_CONTIGUOUS']:
                realdata = np.asfortranarray(realdata)
            if len(data) == 2:
                if not imagdata.flags['F_CONTIGUOUS']:
                    imagdata = np.asfortranarray(imagdata)

            if realdata.dtype in [np.float64, np.float32, np.uint32]:
                # Real part/magnitude (depending on format)
                self._data1 = np.asfortranarray(realdata)
                if len(data) == 2:
                    # Imaginary part/phase (depending on format)
                    self._data2 = np.asfortranarray(imagdata)
            elif data.dtype == np.complex128:
                raise TypeError('For complex type, use load_data() instead.')
            elif data.dtype == np.complex64:
                raise TypeError('For complex type, use load_data() instead.')
            else:
                raise TypeError('Unsupported data type.')

        def allocate_data(self, anum: int, cnum: int, is_complex: bool = False):
            dtype = dtype_mats2np(self._precision, is_complex)
            order = order_mats2np(self._storage)
            self._data1 = np.zeros((anum, cnum), dtype, order)
            if is_complex:
                self._data2 = np.zeros((anum, cnum), dtype, order)

        def abs_value(self):
            if self.is_complex():
                raise NotImplementedError('Not implemented yet.')
            else:
                self._data1 = np.fabs(self._data1)

        def snippet(self, x: int, y: int, snipwidth: int, snipheight: int):
            snip = Data()
            width_buff = (float(snipwidth) - 1.0) * 0.5
            height_buff = (float(snipheight) - 1.0) * 0.5
            data_anum = self._data1.shape[0]
            data_cnum = self._data1.shape[1]

            # Find outermost snippet centers
            minx = math.ceil(width_buff)  # left-most valid center
            miny = math.ceil(height_buff)  # top-most valid center
            maxx = data_cnum - 1 - math.floor(
                width_buff)  # right-most valid center
            maxy = data_anum - 1 - math.floor(
                height_buff)  # bottom-most valid center

            # Adjust center position if near an edge of the image
            x = max(min(x, maxx), minx)
            y = max(min(y, maxy), miny)

            left = x - math.ceil(width_buff)
            right = x + math.floor(width_buff)
            top = y - math.ceil(height_buff)
            bottom = y + math.floor(height_buff)

            # Setup snippet
            snip.blank_copy(self)
            snip.allocate_data(snipheight, snipwidth, self.is_complex())

            # Make snippet
            snip._data1 = self._data1[left:right, top:bottom]
            if self.is_complex():
                snip._data2 = self._data2[left:right, top:bottom]

            return snip

        def copy(self, data):
            if not isinstance(data, type(self)):
                raise TypeError('data must be of type "{}"'.format(type(self)))
            self._precision = data._precision
            self._storage = data._storage
            self._format = data._format
            self._res = data._res.copy()
            self._data1 = data._data1.copy()
            self._data2 = data._data2.copy()

        def blank_copy(self, data):
            if not isinstance(data, type(self)):
                raise TypeError('data must be of type "{}"'.format(type(self)))
            self._precision = data._precision
            self._storage = data._storage
            self._format = data._format
            self._res = data._res.copy()

        def component(self, k: int):
            if k == 0:
                return self._data1
            elif k == 1:
                return self._data2
            else:
                raise ValueError('k must be 0 or 1.')
