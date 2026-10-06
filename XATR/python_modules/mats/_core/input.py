import numpy as np
import mats
import mats._core.data
import mats.core


class InputBase:
    _fields = ['filename', 'sweetspot', 'data_names', 'ref_name', 'nav_size',
               'sensor', 'target_type', 'side', 'mode', 'lat', 'lon',
               'heading', 'time', 'height', 'depth']

    def __init__(self):
        if self.__class__ == InputBase:
            raise TypeError('This is an abstract base class.')
        self._is_chunk = False

        self._filename = ''
        self._sweetspot = [0, 0]
        self._data_names = []
        self._ref_name = ''
        self._nav_size = 0
        self._sensor = ''
        self._target_type = 0
        self._side = ''
        self.mode = ''
        self._lat = np.array([])
        self._lon = np.array([])
        self._heading = np.array([])
        self._time = np.array([])
        self._height = np.array([])
        self._depth = np.array([])
        self._data = {}

    def __repr__(self):
        return 'Input({} - {})'.format(self['filename'], self['side'])

    def __str__(self):
        sweetspot = self['sweetspot']
        ss = f'[{sweetspot[0]}, {sweetspot[1]}]'
        num_nav = self['nav_size']

        if num_nav > 0:
            t = self.get_time()
            time = f'[{t[0]}, ..., {t[num_nav-1]}]'
            lat = self.get_lat()
            latitude = f'[{lat[0]}, ..., {lat[num_nav-1]}]'
            lon = self.get_lon()
            longitude = f'[{lon[0]}, ..., {lon[num_nav-1]}]'
            head = self.get_heading()
            heading = f'[{head[0]}, ..., {head[num_nav-1]}]'
            h = self.get_height()
            height = f'[{h[0]}, ..., {h[num_nav-1]}]'
            d = self.get_depth()
            depth = f'[{d[0]}, ..., {d[num_nav-1]}]'
        else:
            time = '[]'
            latitude = '[]'
            longitude = '[]'
            heading = '[]'
            height = '[]'
            depth = '[]'

        out = (
            'MATS_input:\n\n'
            '    Filename: {0}\n'
            '        Side: {1}\n'
            '      Sensor: {2}\n'
            '   Sweetspot: {3}\n'
            '  Nav Length: {4}\n'
            '        Time: {5}\n'
            '    Latitude: {6}\n'
            '   Longitude: {7}\n'
            '     Heading: {8}\n'
            '      Height: {9}\n'
            '       Depth: {10}\n'
            '        Data:\n'
        ).format(self['filename'], self['side'], self['sensor'], ss, num_nav,
                 time, latitude, longitude, heading, height, depth)

        bands = self['data_names']
        for band in bands:
            sz = self.data(band).size()
            ares = self.data(band).ares
            cres = self.data(band).cres
            bout = '              [{0} | {1}x{2} @ ({3}, {4})]\n'.format(
                    band, sz[0], sz[1], ares, cres)
            out += bout

        return out

    def __getitem__(self, key):
        if key == 'filename':
            return self._filename
        elif key == 'sweetspot':
            return self._sweetspot
        elif key == 'data_names':
            return self._data_names
        elif key == 'ref_name':
            return self._ref_name
        elif key == 'nav_size':
            return self._nav_size
        elif key == 'sensor':
            return self._sensor
        # elif key == 'target_type':
        #     return self.thisptr.targetType()
        elif key == 'side':
            return self._side
        # elif key == 'mode':
        #     return self.thisptr.mode()
        elif key == 'lat':
            return self._lat
        elif key == 'lon':
            return self._lon
        elif key == 'heading':
            return self._heading
        elif key == 'time':
            return self._time
        elif key == 'height':
            return self._height
        elif key == 'depth':
            return self._depth
        raise KeyError('Field does not exist ({})'.format(key))

    def __setitem__(self, key, value):
        if key == 'filename':
            self._filename = value
        elif key == 'sweetspot':
            if len(value) != 2:
                raise ValueError('sweetspot must contain 2 values')
            self._sweetspot = value
        elif key == 'sensor':
            self._sensor = value
        # elif key == 'target_type':
        #     self.thisptr.setTargetType(value)
        elif key == 'side':
            self._side = value
        # elif key == 'mode':
        #     self.thisptr.setMode(value)
        elif key in ['data_names', 'ref_name', 'nav_size', 'lat', 'lon',
                     'heading', 'time', 'height', 'depth']:
            raise KeyError('Cannot set this field directly ({}).'.format(key))
        else:
            raise KeyError('Field does not exist ({})'.format(key))

    def __contains__(self, key):
        return key in self._fields

    def __iter__(self):
        for field in self._fields:
            yield field

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, val):
        if isinstance(val, str):
            val = str
        elif isinstance(val, Path):
            val = str(val)
        else:
            raise ValueError('filename must be a str.')

    @property
    def side(self):
        return self._side

    @side.setter
    def side(self, val):
        if isinstance(val, str):
            self._side = val
        else:
            raise ValueError('side must be str.')

    @property
    def sweetspot(self):
        return self._sweetspot

    @sweetspot.setter
    def sweetspot(self, val):
        if isinstance(val, list) and len(val) == 2:
            self._sweetspot = val
        else:
            raise ValueError('sweetspot must be list of length 2.')

    @property
    def sensor(self):
        return self._sensor

    @sensor.setter
    def sensor(self, val):
        if isinstance(val, str):
            self._sensor = val
        else:
            raise ValueError('sensor must be a str.')

    @property
    def data_names(self):
        return self._data_names

    @data_names.setter
    def data_names(self, val):
        raise AttributeError("Use 'add_data' method to add data.")

    @property
    def ref_name(self):
        return self._ref_name

    @ref_name.setter
    def ref_name(self, val):
        if isinstance(val, str):
            self._ref_name = val
        else:
            raise ValueError('ref_name must be a str')

    @property
    def nav_size(self):
        return self._nav_size

    def is_chunk(self):
        return self._is_chunk

    def data(self, band: str):
        """
        Returns a channel of sensor data.

        :param band: Name of data channel.
        :type band: str
        :return: Sensor data object
        :rtype: mats.Data
        """
        if not (band in self._data):
            raise ValueError('Unknown band {}.'.format(band))
        return self._data[band]

    def get_lat(self):
        return self._lat

    def get_lon(self):
        return self._lon

    def get_heading(self):
        return self._heading

    def heading(self, ix: int):
        return self._heading[ix]

    def get_time(self):
        return self._time

    def get_height(self):
        return self._height

    def get_depth(self):
        return self._depth


if mats.cpp_backend:
    class Input(mats.mc.MATS_input):
        """
        Input is an input containing the full along-track dataset.

        Each Input may contain multiple datasets that cover the same
        along-track section and originate from the same side of the vehicle. For
        example, the input may contain both HF (high-frequency) and BB
        (broad-band) data from the port side of the vehicle. The different
        datasets generally cover the same bottom area, although some datasets
        may have a farther range than others.

        **Properties:**

        :filename: Filename of sensor data. Generally, this does not have
            to be an actual file and can be used as a string identifier for the
            sensor data loaded.
        :sensor: Sensor ID string. String is used to identify the
            appropriate Sensor module to use for the data.
        """
        def __init__(self):
            super().__init__()
else:
    class Input(InputBase):
        """
        Input is an input containing the full along-track dataset.

        Each Input may contain multiple datasets that cover the same
        along-track section and originate from the same side of the vehicle. For
        example, the input may contain both HF (high-frequency) and BB
        (broad-band) data from the port side of the vehicle. The different
        datasets generally cover the same bottom area, although some datasets
        may have a farther range than others.
        """
        def __init__(self):
            InputBase.__init__(self)

        def add_data(self, band: str):
            """
            Add a dataset to the MATS Input. The first dataset to be added will
            be recorded as the reference dataset.

            .. note:: This only allocates space.  The actual assignment comes
                      later.

            :param band: Name of the dataset.
            :type band: str
            :rtype: None
            """
            if band in self._data:
                raise RuntimeError('Specified band already exists')
            self._data[band] = mats._core.data.Data()
            if len(self._data_names) == 0:
                # This is the first band added --> make it reference
                self._ref_name = band
            self._data_names.append(band)

        def allocate_nav(self, num: int):
            if num < 1:
                raise ValueError('Nav data length must be >= 1')
            if self._nav_size > 0:
                raise RuntimeError('Nav data arrays have already been allocated')
            self._nav_size = num
            self._lat = np.ndarray((num,))
            self._lon = np.ndarray((num,))
            self._heading = np.ndarray((num,))
            self._time = np.ndarray((num,))
            self._height = np.ndarray((num,))
            self._depth = np.ndarray((num,))
