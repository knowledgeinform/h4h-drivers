# DISTRIBUTION STATEMENT D. Distribution authorized to the Department of
# Defense and U.S. DoD contractors only; Administrative or Operational Use; 1
# Jan 2017. Other U.S. requests shall be referred to Naval Surface Warfare
# Center Panama City Division, ATTN: Technical Director NSWC PCD, 110 Vernon
# Ave, Panama City, FL 32407.
"""
mats.sensor
-----------
Contains classes and functions related to sensor types.
"""
from mats.data import Precision

_sns_list = []


def data_description(stype=None, direction=None, precision=None,
                     processing=None, res=None):
    """
    Create Data Description dict

    :param stype: Type of sensor [SONAR|RADAR|MAG].
    :type stype: str
    :param direction: Direction of sensor [SIDELOOK|FORWARD|BOTTOM].
    :type direction: str
    :param precision: Expected data precision.
    :type precision: mats.data.Precision
    :param processing: ATR processing type [BLOCK|STREAM].
    :type processing: str
    :param res: Expected resolution of each dimension.
    :type res: [float]
    """
    if not stype:
        stype = ''
    if not direction:
        direction = ''
    if not precision:
        precision = Precision.UNKNOWN
    if not processing:
        processing = 'BLOCK'
    if not res:
        res = []
    return {'type': stype, 'direction': direction, 'precision': precision,
            'processing': processing, 'res': res}


class Sensor(object):
    """
    MATS Sensor module base class.
    """
    def __init__(self):
        self._name = ''
        self._version = ''
        self._description = ''
        self._data = {}             # each value is type MATS_data_description
        self._snippet_size = []      # each element is type int
        self._gt_dist_thresh = 0.0
        self._ref_name = ''
        self._has_nav = True

    def __repr__(self):
        return f"Sensor[{self._name}]"

    @property
    def name(self):
        """Name of sensor."""
        return self._name

    @property
    def version(self):
        """Sensor module version."""
        return self._version

    @property
    def description(self):
        """Description of sensor."""
        return self._description

    @property
    def ref_name(self):
        """Name of reference dataset for sensor."""
        return self._ref_name

    @property
    def has_nav(self):
        """Indicates if sensor has navigation data."""
        return self._has_nav

    @property
    def data_names(self):
        """Names of datasets for sensor."""
        return list(self._data.keys())

    @property
    def snippet_size(self):
        """Size of snippets for this sensor."""
        return self._snippet_size

    @property
    def gt_dist_thresh(self):
        """Distance threshold for matching contacts to ground truth."""
        return self._gt_dist_thresh

    def data(self, name_str):
        """
        Returns data description for requested sensor data.

        :param name_str: Name of sensor data.
        :type name_str: str

        :return: Data description if found. If not found, returns None.
        :rtype: dict|None
        """
        return self._data.get(name_str, None)

    def sweetspot(self, inp) -> None:   # mats_in is type MATS_input_base
        """
        Finds ideal sensor data region for ATR processing and sets the input
        sweetspot field accordingly.

        :param inp: MATS input object.
        :type inp: mats.Input
        """
        # TODO(Bradley): HF needs to be replaced by sensor reference band.
        # Default method: Sweetspot is full range of the image
        inp['sweetspot'] = [0, inp.data('HF')['cnum'] - 1]

    def snippet_generator(self, inp, con, ecd) -> None:
        """
        Sensor specific contact snippet generator. Extra contact data is updated
        directly. Nothing is returned.

        :param inp: MATS Input data corresponding to contact.
        :type inp: mats.Input
        :param con: Contact information.
        :type con: mats.Contact
        :param ecd: Extra contact data.
        :type ecd: mats.Ecdata
        """
        return

    def roi_recenter(self, inp, x, y):
        """
        Recenter contact position.

        :param inp: MATS Input data for contact.
        :type inp: mats.Input
        :param x: Contact X position.
        :type x: int
        :param y: Contact Y position.
        :type y: int
        :return: Recommended new (X, Y) position.
        :rtype: (int, int)
        """
        # Default method: No change
        return x, y

    # TODO: Something for loading data easier? (Required multi-step process)


def mats_known_sensors():
    """
    Return list of known sensors.

    :rtype: [str]
    """
    return [s.name for s in _sns_list]


def mats_sensor(name):
    """
    Return sensor module with given sensor name (not module name!).

    :param name: Name of sensor module
    :type name: str

    :return: MATS Sensor module for requested sensor.
    :rtype: Sensor
    :raises ValueError: If name does not match a known sensor module.
    """
    sns = [s for s in _sns_list if s.name == name]
    if not sns:
        raise ValueError(f'Unknown sensor name ({name}).')
    return sns[0]
