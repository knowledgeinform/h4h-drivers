# DISTRIBUTION STATEMENT D. Distribution authorized to the Department of
# Defense and U.S. DoD contractors only; Administrative or Operational Use; 1
# Jan 2017. Other U.S. requests shall be referred to Naval Surface Warfare
# Center Panama City Division, ATTN: Technical Director NSWC PCD, 110 Vernon
# Ave, Panama City, FL 32407.
"""
mats.h5
__________
This submodule provides functions for read/write/update of MATS objects to HDF5
files.
"""
import h5py
import numpy as np
import mats.log
import mats.time
import mats.gt
# from mats import Contact, ContactList, Ecdata, EcdataList
# from mats import Struct, Cell, Input, Data
from mats._core.data import dtype_np2mats, dtype_mats2np

DEBUG_LEVELS = {'OFF': 0, 'MINIMAL': 1, 'DETAILED': 30, 'VERBOSE': 100}
DEBUG = DEBUG_LEVELS['MINIMAL']  # NOTE: Change key to desired level of messages

PRECISIONS = {'UNKNOWN': 0, 'UNSIGNED_INT': 1, 'FLOAT': 2, 'DOUBLE': 3}
FORMATS = {'REAL_IMAG': 0, 'AMP_PHASE': 1}
STORAGES = {'COL_MAJOR': 0, 'ROW_MAJOR': 1}


def _debug_check(key):
    return DEBUG >= DEBUG_LEVELS[key]


def __check_create(loc, name_str):
    if type(name_str) is not str:
        mats.log.error(f'Name string is not a string ({type(name_str)}).')
        return True
    if len(name_str) == 0:
        mats.log.error('Name string is empty')
        return True
    if name_str in loc:
        mats.log.error(f'Data already exists at {name_str}')
        return True
    return False


def __h5_type(value):
    dtype = type(value)
    if dtype == float:
        return 'float32'
    return None


def __check_attr_create(loc, name_str):
    if type(name_str) is not str:
        mats.log.error(f'Name string is not a string ({type(name_str)}).')
        return True
    if len(name_str) == 0:
        mats.log.error('Name string is empty')
        return True
    if name_str in loc.attrs:
        mats.log.error(f'Attribute already exists at {name_str} in {loc.name}')
        return True
    return False


def __check_get(loc, name_str):
    if type(name_str) is not str:
        mats.log.error(f'Name string is type {name_str}, not string')
        return True
    if len(name_str) == 0:
        mats.log.error('Name string is empty')
        return True
    if name_str not in loc:
        mats.log.error(f'No data found at {name_str}')
        return True
    return 0


# Lookup dictionary key from corresponding value
# NOTE: This function is intended to be used only for parameter dictionaries
#   that contain no duplicate values, thereby avoiding the need to create the
#   inverse dictionaries
def key_lookup(dictionary, value):
    for k, v in dictionary.items():
        if v == value:
            return k
    return None


def create_string(hh, name_str, value):
    """
    Write a string dataset to an H5 path location.

    :param hh: Valid H5 file or group to receive the dataset.
    :type hh: h5py.File|h5py.Group
    :param name_str: String ID or name for this new dataset.
    :type name_str: str
    :param value: String to be written.
    :type value: str

    :return: Returns 0 on success, or 1 if failure
    :rtype: int
    """
    if __check_create(hh, name_str):
        return 1
    if type(value) is not str:
        return mats.log.error(f'Data is type {type(value)}, not string')
    if len(value) == 0:
        return mats.log.warn(f'No data given to write to {name_str}')
    type_str = 'S%d' % len(value)
    hh.create_dataset(name_str, (1,), dtype=type_str)
    hh[name_str][0] = value.encode('ascii')
    return 0


def get_string(hh, name_str):
    """
    Read a string dataset from an H5 path location.

    :param hh: Valid H5 file or group object.
    :type hh: h5py.File|h5py.Group
    :param name_str: H5 location of string dataset.
    :type name_str: str

    :return: Dataset string or empty string if an error occurs.
    :rtype: str
    """
    default = ''
    # Check inputs
    if __check_get(hh, name_str):
        return default
    return hh[name_str][0].decode()


def create_string_list(hh, name_str, strs):
    """
    Write a string list dataset to an H5 path location.

    :param hh: Valid H5 file or group object.
    :type hh: h5py.File|h5py.Group
    :param name_str: H5 location of string dataset.
    :type name_str: str
    :param strs: List of strings to be written.
    :type strs: [str]

    :return: Returns 0 on success, or 1 if failure.
    :rtype: int
    """
    if __check_create(hh, name_str):
        return 1
    if type(strs) is not list or not all([type(x) is str for x in strs]):
        return mats.log.error(f'Data is type {type(strs)}, not list of strings')
    if len(strs) == 0:
        return mats.log.warn(f'No data given to write to {name_str}.')
    hh.create_dataset(name_str, (len(strs),),
                      data=[s.encode('ascii') for s in strs])
    return 0


def get_string_list(hh, name_str):
    """
    Read a string list dataset from an H5 path location

    :param hh: Valid H5 file or group object.
    :type hh: h5py.File|h5py.Group
    :param name_str: H5 location of string dataset.
    :type name_str: str

    :return: List of strings or empty list if error.
    :rtype: [str]
    """
    default = []
    if __check_get(hh, name_str):
        return default
    return [x.decode() for x in hh[name_str]]


def create_array(hh, name_str, value):
    """
    Write an array dataset to an H5 path location.

    :param hh: Valid H5 file or group object.
    :type hh: h5py.File|h5py.Group
    :param name_str: H5 location of data.
    :type name_str: str
    :param value: Array to be written.
    :type value: numpy.ndarray

    :return: Returns 0 on success, or 1 if failure.
    :rtype: int
    """
    if __check_create(hh, name_str):
        return 1
    if type(value) is not np.ndarray:
        return mats.log.error(f'Data is type {type(value)}, not ndarray')
    if value.size == 0:
        return mats.log.warn(f'No data given to write to {name_str}')
    # Reverse data dimensions
    shape = value.shape[::-1]
    temp = value.reshape(shape)
    hh.create_dataset(name_str, data=temp)
    return 0


def get_array(hh, name_str):
    """
    Read an array dataset from an H5 path location

    :param hh: Valid H5 file or group object.
    :type hh:  h5py.File|h5py.Group
    :param name_str: H5 location of dataset.
    :type name_str: str

    :return: Retrieved array dataset.
    :rtype: numpy.ndarray
    """
    default = np.array([])
    if __check_get(hh, name_str):
        return default
    # Undo the dimension reverse
    shape = hh[name_str][:].shape[::-1]
    return hh[name_str][:].reshape(shape)


def update_array(hh, name_str, data):
    # Check inputs
    if __check_get(hh, name_str):
        return False
    n = data.size

    # Open the dataset; check type and size
    dh = hh[name_str]
    req_type = str(type(data))
    tid = str(dh.dtype)
    if req_type not in tid:
        mats.log.warn(f"Type mismatch ({req_type} vs {tid}). Write may fail.")
    if not np.prod(dh.shape) == n:
        mats.log.error("Data size must be the same as Dataset.")
        return False
    dh[...] = data
    return True


def create_value(hh, name_str, value):
    """
    Write a numeric value to an H5 path location.

    :param hh: Valid H5 file or group object.
    :type hh: h5py.File|h5py.Group
    :param name_str: H5 location of string dataset.
    :type name_str: str
    :param value: Data value to be written.
    :type value: int|double

    :return: Returns 0 on success, or 1 if failure.
    :rtype: int
    """
    if __check_create(hh, name_str):
        return 1
    if not np.isscalar(value):
        return mats.log.error('Data must be numeric scalar.')
    # Write numeric value as one-element data arrays
    hh.create_dataset(name_str, data=[[value]])
    return 0


def get_value(hh, name_str):
    """
    Retreive a single numeric value from a data field.

    :param hh: Valid H5 file or group object.
    :type hh: h5py.File|h5py.Group
    :param name_str: H5 location of dataset.
    :type name_str: str

    :return: Retrieved value or empty if error.
    """
    default = None
    if __check_get(hh, name_str):
        return default
    if hh[name_str].size != 1:
        print('{} contains multiple values'.format(name_str))
        return default

    if len(hh[name_str].shape) == 1:   # i.e., shape == (1,)
        val = hh[name_str][0]
    else:                               # i.e., shape == (1,1)
        # loc[name_str][0] in np.ndarray --> extract value at index 0
        val = hh[name_str][0][0]

    # NOTE: There used to be a conversion to Python types here, but that
    #   made it impossible to disambiguate types.  If a conversion is
    #   necessary, do it downstream.
    return val


def update_value(hh, name_str, data):
    """
    Replace or update a single value dataset in a HDF5 file. The file must be
    opened with 'r+' permissions for this to work. Also, this will not change
    the data type of the dataset. So, if the data types differ, update value
    will be cast to the file data type or error.

    :param hh: Valid H5 file or group object.
    :type hh:  h5py.File|h5py.Group
    :param name_str: H5 location of string dataset.
    :type name_str: str
    :param data: Data value to be written.
    :type data: int|double

    :return: Returns True on success. Otherwise, returns False.
    :rtype: bool
    """
    # Check inputs
    if __check_get(hh, name_str):
        return False

    # Open dataset; check type and size
    dh = hh[name_str]

    req_type = str(type(data))
    tid = str(dh.dtype)
    if req_type not in tid:
        mats.log.warn(f"Type mismatch ({req_type} vs {tid}). Write may fail.")

    if not np.prod(dh.shape) == 1:
        mats.log.error("Dataset must contain a single value.")
        return False
    # h5py seems to enforce the type
    dh[...] = data
    return True


def create_attr_string(hh, name_str, value) -> int:
    """
    Write a string attribute to an H5 path location.

    :param hh: Valid H5 file or group object.
    :type hh: h5py.File|h5py.Group
    :param name_str: H5 location of dataset.
    :type name_str: str
    :param value: Attribute string to be written.
    :type value: str

    :return: Returns 0 on success, or 1 if failure.
    """
    if __check_attr_create(hh, name_str):
        return 1
    if type(value) is not str:
        return mats.log.error(f'Data is type {type(value)}, not string.')
    if len(value) == 0:
        return mats.log.error(
            f'No data given to write to attribute {name_str}.')
    type_str = 'S%d' % len(value)
    hh.attrs.create(name_str, value.encode('ascii'), shape=(1,),
                    dtype=type_str)
    return 0


def get_attr_string(loc, name_str):
    default = ''
    # Check inputs
    if type(name_str) is not str:
        print('Name string is type {}, not string'.format(type(name_str)))
        return default
    if len(name_str) == 0:
        print('Name string is empty')
        return default
    if name_str not in loc.attrs:
        print('No attribute string found at {}'.format(name_str))
        return default
    # TODO: Robustify this like the other functions
    return loc.attrs[name_str][0].decode()


def create_mats_struct(hh, name_str, value) -> int:
    """
    Write a structure dataset to an H5 path location (may contain nested
    structures).

    :param hh: Valid H5 file or group object.
    :type hh: h5py.File|h5py.Group
    :param name_str: H5 location of string dataset.
    :type name_str: str
    :param value: MATS Struct data to be written.
    :type value: mats.Struct|dict

    :return: Returns 0 on success, or 1 if failure.
    """
    if __check_create(hh, name_str):
        return 1
    # NOTE: Native python implementation uses dict instead of MATS Struct b/c
    #   they are functionally equivalent
    if type(value) not in [mats.Struct, dict]:
        return mats.log.error(f'Data is type {type(value)}, not struct.')
    mats.log.info(f'struct @ {hh.name}:{name_str}')

    hh.create_group(name_str)
    create_attr_string(hh[name_str], 'type', 'struct')
    field_names = [f.encode() for f in value]
    hh[name_str].create_dataset('fields', data=field_names)
    for f in value:
        field_loc = hh[name_str].create_group(f)
        _save_field(field_loc, 'data', value[f])
    status = 0

    mats.log.info(f'end struct @ {hh.name}:{name_str}')
    return status


def get_mats_struct(hh, name_str):
    """
    Read a MATS Struct from an H5 path location.

    :param hh: Valid H5 file or group object.
    :type hh: h5py.File|h5py.Group
    :param name_str: H5 location of string dataset.
    :type name_str: str
    :return: Loaded MATS Struct.
    :rtype: mats.Struct
    """
    d = mats.Struct()
    if __check_get(hh, name_str):
        return d
    mats.log.info(f'struct @ {hh.name}:{name_str}')
    if 'fields' in hh[name_str].keys():
        mats.log.info(
            f"{hh[name_str].name} contains {hh[name_str]['fields'][:]}")
        for fld in hh[name_str]['fields']:
            fld = fld.decode()  # bytes --> string
            x = _load_field(hh[name_str][fld])
#                print('loc[{}][{}] is type {}'.format(name_str, fld, type(x)))
            d.set(fld, x)
    mats.log.info(f'end struct @ {hh.name}:{name_str}')
    return d


# Write a cell dataset to an H5 path location (may contain nested structures)
#   loc = valid location ID of file or group to receive the dataset
#   name_str = string ID for this new dataset
#   value = cell data to be written
# Returns 0 on success, or 1 if failure
def create_mats_cell(loc, name_str, value):
    if __check_create(loc, name_str):
        return 1
    # NOTE: Native python implementation uses list instead of MATS Cell b/c
    #   they are functionally equivalent
    if type(value) not in [mats.Cell, list]:
        return mats.log.error(f'Data is type {type(value)}, not cell')

    mats.log.info(f'cell @ {loc.name}:{name_str}')
    if type(value) is mats.Cell:
        val_dims = value.dims()
    else:
        # Assume that this is a python list acting as a 1-D cell array
        # (lists being simpler while providing most of the functionality)
        val_dims = (1, len(value))
    # print('val_dims = {}'.format(val_dims))
    loc.create_group(name_str)
    create_attr_string(loc[name_str], 'type', 'cell')

    create_array(loc[name_str], 'dims', np.array(val_dims))
    for q in range(len(value)):
        elem_name = 'cell_%d' % (q+1)
        elem_gid = loc[name_str].create_group(elem_name)
        _save_field(elem_gid, 'data', value[q])
    mats.log.info(f'end cell @ {loc.name}:{name_str}')
    return 0


# Read a cell dataset from an H5 path location
#   loc = valid location ID of file or group containing the dataset
#   name_str = string ID for this dataset
# Returns cell located at loc[name_str], or empty cell if error
def get_mats_cell(loc, name_str):
    d = mats.Cell()

    if __check_get(loc, name_str):
        return d
    mats.log.info(f'cell @ {loc.name}:{name_str}')
    dim_arr = loc[name_str]['dims'][:]
    d.resize(dim_arr[0], dim_arr[1])
    size = dim_arr[0]*dim_arr[1]
    mats.log.info(f'cell contains {size} elements')
    for q in range(size):
        item_path = 'cell_%d' % (q+1)
        d.set(q, _load_field(loc[name_str][item_path]))
    mats.log.info(f'end cell @ {loc.name}:{name_str}')
    return d


# Write a MATSInput dataset to an H5 path location
#   loc = valid location ID of file or group to receive the dataset
#   name_str = string ID for this new dataset
#   d = MATSInput data to be written
# Returns 0 on success, or 1 if failure
def create_mats_input(loc, name_str, d):
    if __check_create(loc, name_str):
        return 1
    if type(d) != mats.Input:
        return mats.log.error(f'Data is type {type(d)}, not MATS Input.')
    # Make group for local root of all input data
    in_root = loc.create_group(name_str)
    create_attr_string(in_root, 'type', 'input')
    # Write imagery data
    create_string(in_root, 'refname', d['ref_name'])
    create_string_list(in_root, 'data/names', d['data_names'])
    for band in d['data_names']:
        band_loc = in_root.create_group('data/data/%s' % band)
        band_data = d.data(band)
        dtype_str = dtype_np2mats(band_data['data'].dtype)
        create_value(band_loc, 'data_precision', PRECISIONS[dtype_str])
        create_value(band_loc, 'data_storage', 0)  # 'COL_MAJOR'
        create_value(band_loc, 'data_format', 0)  # 'REAL_IMAG'
        create_value(band_loc, 'data_anum', band_data['anum'])
        create_value(band_loc, 'data_ares', band_data['ares'])
        create_value(band_loc, 'data_cnum', band_data['cnum'])
        create_value(band_loc, 'data_cres', band_data['cres'])
        band_loc['data_real'] = band_data['real'].T
        band_loc['data_imag'] = band_data['imag'].T
    # Write navigation data
    create_value(in_root, 'navlen', d['nav_size'])
    create_array(in_root, 'lat', d['lat'])
    create_array(in_root, 'lon', d['lon'])
    create_array(in_root, 'heading', d['heading']*np.pi/180.0)
    create_array(in_root, 'time', d['time'])
    create_array(in_root, 'height', d['height'])
    create_array(in_root, 'depth', d['depth'])
    # Write other parameters
    create_string(in_root, 'fn', d['filename'])
    create_string(in_root, 'sensor', d['sensor'])
    create_string(in_root, 'side', d['side'])
    create_array(in_root, 'sweetspot',
                 np.array(d['sweetspot'], dtype=np.uint64))
    # TODO: d['target_type'], GT, VERSION
    return 0


# Read a MATSInput dataset from an H5 path location
#   loc = valid location ID of file or group containing the dataset
#   name_str = string ID for this dataset
# Returns MATSInput data located at loc[name_str], or empty MATSInput if error
def get_mats_input(hh, name_str, load_imagery=None):
    """
    Read a MATS Input from an H5 path location.

    :param hh: Valid H5 file or group object.
    :type hh: h5py.File|h5py.Group
    :param name_str: H5 location of data.
    :type name_str: str
    :param load_imagery: Array to be written.
    :type load_imagery: numpy.ndarray

    :return: Returns loaded MATS Input.
    :rtype: mats.Input
    """
    if load_imagery is None:
        load_imagery = True
    inp = mats.Input()
    if __check_get(hh, name_str):
        raise ValueError(f"Unable to locate 'name_str' location ({name_str})")
    in_loc = hh[name_str]
    if 'type' not in in_loc.attrs and in_loc.attrs['type'] != 'input':
        mats.log.warn(f'{in_loc} is not marked as input data!')

    # Import image data
    ref_band = get_string(in_loc, 'refname')
    band_names = get_string_list(in_loc, 'data/names')
    if band_names[0] != ref_band:
        # Rearrange band names so that the reference band is first
        ref_idx = band_names.index(ref_band)
        band_names.insert(0, band_names.pop(ref_idx))
        # raise RuntimeError('Reference band is not listed first')
    for band in band_names:
        # TODO: It seems like we should use get_mats_data for the imagery
        #   components, but I can't get the dimensions right - DK
        if band not in in_loc['data/data'] and not load_imagery:
            # This is probably a unit test data file, in which the imagery
            #   was omitted to save disk space
            continue
        data = get_mats_data(in_loc['data/data'], band)
        print(data.storage)
        inp.add_data(band)
        inp.data(band).copy(data)

        # band_loc = in_loc['data/data/%s' % band]
        # inp.add_data(band)
        # imgry_ptr = inp.data(band)
        # prcsn_num = get_value(band_loc, 'data_precision')
        # prcsn_str = key_lookup(PRECISIONS, prcsn_num)
        # imgry_ptr.precision = prcsn_str
        # imgry_ptr.storage = 'COL_MAJOR'
        # anum = get_value(band_loc, 'data_anum')
        # cnum = get_value(band_loc, 'data_cnum')
        # imgry_ptr.allocate_data(anum, cnum, False)
        # band_array = band_loc['data_real'][:]
        # is_complex = 'data_imag' in band_loc
        # if is_complex:
        #     imag_array = band_loc['data_imag'][:]
        #     band_array = band_array + 1j*imag_array
        # np_type = dtype_mats2np(prcsn_str, is_complex)
        # imgry_ptr.load_data(band_array.astype(np_type).T)
        # imgry_ptr.ares = get_value(band_loc, 'data_ares')
        # imgry_ptr.cres = get_value(band_loc, 'data_cres')
    # get_mats_data(band_loc, imgry_ptr)
    # Import navigation data
    num_nav = int(in_loc['navlen'][0])
    if num_nav > 0:
        inp.allocate_nav(num_nav)
        temp = inp.get_lat()  # latitude
        temp[:] = in_loc['lat']
        temp = inp.get_lon()  # longitude
        temp[:] = in_loc['lon']
        temp = inp.get_heading()  # heading (converted rad -> degrees)
        temp[:] = in_loc['heading']
        for q in range(len(temp)):
            temp[q] *= 180.0/np.pi
        temp = inp.get_time()  # time
        temp[:] = in_loc['time']
        temp = inp.get_height()  # height
        temp[:] = in_loc['height']
        temp = inp.get_depth()  # depth
        temp[:] = in_loc['depth']

    # Import other parameters
    inp.filename = get_string(in_loc, 'fn')
    inp.sensor = get_string(in_loc, 'sensor')
    inp.side = get_string(in_loc, 'side')
    inp.sweetspot = get_array(in_loc, 'sweetspot')

    # TODO: TargetType not implemented.
    # d['target_type'] = get_string(in_loc, 'targettype')
    return inp


def create_mats_contact(hh, name_str, con) -> bool:
    """
    Write a MATS Contact dataset to an H5 path location.

    :param hh: Valid H5 file or group object.
    :type hh: h5py.File|h5py.Group
    :param name_str: H5 location of string dataset.
    :type name_str: str
    :param con: MATS Contact data to be written.
    :type con: mats.Contact

    :return: Returns True on success, or False if failure
    """
    if __check_create(hh, name_str):
        return False
    if type(con) != mats.Contact:
        return mats.log.error(f'Data is type {type(con)}, not MATS Contact.')
    con_loc = hh.create_group(name_str)
    create_attr_string(con_loc, 'type', 'contact')
    if len(con['features']) > 0:
        create_array(con_loc, 'features', con['features'])
    for t in ['detector', 'normalizer', 'classifier', 'contcorr', 'side',
              'uuid']:
        if len(con[t]) > 0:
            create_string(con_loc, t, con[t])
    for t in ['classconf', 'cls', 'gt', 'id', 'type', 'x', 'y']:
        create_value(con_loc, t, con[t])
    create_string_list(con_loc, 'featureset', con['featureset'])
    create_string(con_loc, 'fn', con['filename'])
    return True


def get_mats_contact(hh, name_str):
    """
    Read a MATS Contact dataset from an H5 path location.

    :param hh: Valid h5py file or group object.
    :type hh: h5py.File|h5py.Group
    :param name_str: H5 location of string dataset.
    :type name_str: str

    :return: Data located at name_str, or empty MATS Contact if error.
    :rtype: mats.Contact
    """
    con = mats.Contact()
    if __check_get(hh, name_str):
        return con
    con_loc = hh[name_str]
    if 'type' not in con_loc.attrs:
        mats.log.warn(f'{hh} is not marked as contact data!')

    if 'features' in con_loc.keys():
        con['features'] = get_array(con_loc, 'features')
    if 'featureset' in con_loc.keys():
        con['featureset'] = get_string_list(con_loc, 'featureset')
    for t in ['detector', 'normalizer', 'classifier', 'contcorr', 'uuid']:
        if t in con_loc.keys():
            con[t] = get_string(con_loc, t)
    for t in ['cls', 'gt', 'id', 'type']:
        if t in con_loc.keys():
            con[t] = get_value(con_loc, t)
    con.x = get_value(con_loc, 'x')
    con.y = get_value(con_loc, 'y')
    con.filename = get_string(con_loc, 'fn')
    con.side = get_string(con_loc, 'side')
    con.classconf = get_value(con_loc, 'classconf')
    # con['ecdata_fn'] = get_string(loc, 'ecdata_fn')
    return con


def update_mats_contact(hh, name_str, data) -> bool:
    """
    Update an array dataset in a file or group. The size of the updated array
    must match the size of the existing dataset. The array may be one of the
    following types: bool, signed char, char, int, unsigned int, size_t, float,
    double.

    :param hh: A valid h5py file or group object.
    :type hh: h5py.File or h5py.Group
    :param name_str: H5 location of string dataset.
    :type name_str: str
    :param data: Data value to be written.
    :type data: int or double
    :return: Returns True on success.
    """
    # Check inputs
    if name_str is None:
        mats.log.error("Null name pointer.")
        return False
    if name_str not in hh:
        mats.log.warn(f"Link '{name_str}' does not exist.")
        return False
    gh = hh[name_str]

    dtype = get_attr_string(gh, "type")
    if dtype != "contact":
        mats.log.error(f"Group '{name_str}' is not of type 'contact'.")
        gh.close()
        return False

    # UUID's must match for update
    uuid = get_string(gh, "uuid")
    if uuid != data['uuid']:
        mats.log.error("Contact UUIDs do not match.")
        gh.close()
        return False

    update_value(gh, "id", data['id'])
    update_value(gh, "x", data['x'] + 1)  # to 1-indexing
    update_value(gh, "y", data['y'] + 1)

    update_value(gh, "gt", data['gt'])
    update_value(gh, "type", data['type'])
    update_value(gh, "cls", data['cls'])
    update_value(gh, "classconf", data['classconf'])

    # Update feature vector (in case x/y location changed).
    if data['features'].size > 0:
        update_array(gh, "features", data['features'])

    # Update operator feedback.
    # TODO: Skipping operator feedback.

    # fn, side, normalizer, detector, classifier, contcorr are fixed length
    # string fields. Allowing updates would be inefficient; unlikely to
    # happen; and not recommended.
    return True


# Write a MATSContactList dataset to an H5 path location
#   loc = valid location ID of file or group to receive the dataset
#   name_str = string ID for this new dataset
#   clist = contact list to be written
#
# This creates the following data/groups:
#   - loc[name_str]: group for all contacts
#   --- [contact_id]: group for a single contact.           (if len(clist) > 0)
#   --- Contacts: list of strings containing contact IDs    (if len(clist) > 0)
#
# Returns 0 on success, or 1 if failure
def create_mats_contact_list(loc, name_str, clist):
    if __check_create(loc, name_str):
        return 1
    if type(clist) != mats.ContactList:
        return mats.log.error(
            f'Data is type {type(clist)}, not MATS ContactList.')
    clist_loc = loc.create_group(name_str)
    if len(clist) > 0:
        uuid_list = []
        for con in clist:
            print(con['uuid'])
            create_mats_contact(clist_loc, con['uuid'], con)
            uuid_list.append(con['uuid'])
        create_string_list(clist_loc, 'Contacts', uuid_list)
    return 0


def get_mats_contact_list(hh, name_str):
    """
    Read a MATS ContactList from an H5 path location.

    :param hh: Valid H5 file or group object.
    :type hh: h5py.File|h5py.Group
    :param name_str: H5 location of dataset.
    :type name_str: str

    :return: MATS ContactList from file.
    :rtype: mats.ContactList
    """
    con_list = mats.ContactList()
    if __check_get(hh, name_str):
        return con_list
    list_loc = hh[name_str]
    if 'Contacts' not in list_loc:
        return con_list
    uuid_list = get_string_list(list_loc, 'Contacts')
    for uuid in uuid_list:
        con = get_mats_contact(list_loc, uuid)
        con_list.append(con)
    return con_list


def update_mats_contact_list(hh, name_str, data):
    """
    Update an existing Contact list in a HDF5 file or group.

    :param hh: A valid h5py file or group object.
    :type hh: h5py.File or h5py.Group
    :param name_str: H5 location of string dataset.
    :type name_str: str
    :param data: Updated contact data to be added to file.
    :type data: mats.ContactList
    :return: Returns True on success, or False if failure.
    :rtype: int
    """
    status = True

    # Check inputs
    if name_str is None:
        mats.log.error("Null name pointer.")
        return False
    if name_str not in hh:
        mats.log.warn(f"Link '{name_str}' does not exist.")
        return False
    gh = hh[name_str]

    # Update contacts information
    for con in data:
        if not update_mats_contact(gh, con['uuid'], con):
            mats.log.error(f"Contact update failure ({con['uuid']}).")
            status = False
    return status


# Write a MATSEcdata dataset to an H5 path location
#   loc = valid location ID of file or group to receive the dataset
#   name_str = string ID for this new dataset
#   ecd = MATSEcdata data to be written
# Returns 0 on success, or 1 if failure
def create_mats_ecdata(loc, name_str, ecd):
    if __check_create(loc, name_str):
        return 1
    if type(ecd) != mats.Ecdata:
        return mats.log.error(f'Data is type {type(ecd)}, not MATS Ecdata')
    ecd_loc = loc.create_group(name_str)
    create_attr_string(ecd_loc, 'type', 'ecdata')
    flds = ['detscore', 'groupconf', 'grouplat', 'grouplon',
            'groupnum', 'lat', 'lon', 'time']
    for f in flds:
        create_value(ecd_loc, f, ecd[f])
    hdg_radians = (ecd['heading'] % 360.0) * np.pi/180.0
    create_value(ecd_loc, 'heading', hdg_radians)
    create_value(ecd_loc, 'ID', ecd['id'])
    create_value(ecd_loc, 'alt', ecd['height'])
    create_string(ecd_loc, 'sensor', ecd['sensor'])
    create_string(ecd_loc, 'uuid', ecd['uuid'])
    create_string_list(ecd_loc, 'sensor_data_names', ecd['snippet_names'])
    data_loc = ecd_loc.create_group('data')
    for b in ecd['snippet_names']:
        # Add all data related to this band's snippet
        create_mats_data(ecd_loc, 'data/%s/snippet' % b, ecd.snippet(b))
        # Add original image sizes
        anum, cnum = ecd.get_size(b)
        create_value(ecd_loc['data'][b], 'anum', anum)
        create_value(ecd_loc['data'][b], 'cnum', cnum)
    return 0


def get_mats_ecdata(hh, name_str):
    """
    Read a MATS Ecdata dataset from an H5 path location.

    :param hh: Valid H5 file or group object.
    :type hh: h5py.File|h5py.Group
    :param name_str: H5 location of dataset.
    :type name_str: str

    :return: MATS Ecdata data located at `name_str`,
             or empty MATS Ecdata if error.
    :rtype: mats.Ecdata
    """
    ecd = mats.Ecdata()
    if __check_get(hh, name_str):
        return ecd
    ecd_loc = hh[name_str]
    if 'type' not in ecd_loc.attrs:
        mats.log.warn('{} is not marked as contact data!'.format(ecd_loc))
    flds = ['detscore', 'groupconf', 'grouplat', 'grouplon',
            'groupnum', 'heading', 'lat', 'lon', 'time']
    for f in flds:
        if f in ecd_loc.keys():
            ecd[f] = get_value(ecd_loc, f)
    ecd['heading'] *= 180.0/np.pi
    ecd['id'] = get_value(ecd_loc, 'ID')
    ecd['height'] = get_value(ecd_loc, 'alt')
    ecd['sensor'] = get_string(ecd_loc, 'sensor')
    ecd['uuid'] = get_string(ecd_loc, 'uuid')
    band_names = get_string_list(ecd_loc, 'sensor_data_names')
    # NOTE: There isn't a place for the original image's dimensions
    for b in band_names:
        snippet = get_mats_data(ecd_loc, 'data/%s/snippet' % b)
        ecd.set_snippet(b, snippet)
        anum = int(get_value(ecd_loc['data'][b], 'anum'))
        cnum = int(get_value(ecd_loc['data'][b], 'cnum'))
        ecd.set_size(b, anum, cnum)
    return ecd


def create_mats_ecdata_list(loc, name_str, ecd_list):
    if __check_create(loc, name_str):
        return 1
    if type(ecd_list) != mats.EcdataList:
        return mats.log.error(
            f'Data is type {type(ecd_list)}, not MATS EcdataList.')
    ecd_list_loc = loc.create_group(name_str)
    if len(ecd_list) > 0:
        uuid_list = []
        for ecd in ecd_list:
            create_mats_ecdata(ecd_list_loc, ecd['uuid'], ecd)
            uuid_list.append(ecd['uuid'])
        create_string_list(ecd_list_loc, 'Ecdata', uuid_list)
    return 0
    

def get_mats_ecdata_list(hh, name_str):
    """
    Read a MATS EcdataList dataset from an H5 path location.

    :param hh: Valid H5 file or group object.
    :type hh: h5py.File|h5py.Group
    :param name_str: H5 location of dataset.
    :type name_str: str

    :return: MATS EcdataList data located at loc[name_str], or empty MATS
             EcdataList if error.
    :rtype: mats.EcdataList
    """
    ecd_list = mats.EcdataList()
    if __check_get(hh, name_str):
        return ecd_list
    list_loc = hh[name_str]
    if 'Ecdata' not in list_loc:
        return ecd_list
    uuid_list = get_string_list(list_loc, 'Ecdata')
    for uuid in uuid_list:
        ecd = get_mats_ecdata(list_loc, uuid)
        ecd_list.append(ecd)
    return ecd_list


# Read a MATSData dataset from an H5 path location
#   loc = valid location ID of file or group containing the dataset
#   name_str = string ID for this dataset
# Returns MATSData data located at loc[name_str], or empty MATSData if error
def get_mats_data(loc, name_str):
    data = mats.Data()
    if __check_get(loc, name_str):
        return data
    data_loc = loc[name_str]
    # NOTE: MATSData groups are often not marked as 'data', but they can be
    # if 'type' not in data_loc.attrs:
    #     print('{} is not marked as MATS data!'.format(data_loc))

    # Convert stored integer parameter values to strings
    storage_str = key_lookup(STORAGES, get_value(data_loc, 'data_storage'))
    # if storage_str != 'COL_MAJOR':
    #     raise RuntimeError('{} case not implemented'.format(storage_str))
    format_str = key_lookup(FORMATS, get_value(data_loc, 'data_format'))
    data.storage = storage_str
    print(data.storage)
    data.ares = get_value(data_loc, 'data_ares')
    data.cres = get_value(data_loc, 'data_cres')
    prcsn_str = key_lookup(PRECISIONS,
                           get_value(data_loc, 'data_precision'))
    data.precision = prcsn_str
    data.format = format_str
    anum = get_value(data_loc, 'data_anum')
    cnum = get_value(data_loc, 'data_cnum')

    real_array = get_array(data_loc, 'data_real')
    if storage_str == 'ROW_MAJOR':
        # Dims are swapped from get_array
        real_array = real_array.reshape((anum, cnum))

    # Note: load_data functions will convert to COL_MAJOR
    ap_flag = format_str == 'AMP_PHASE'
    if 'data_imag' in data_loc:
        imag_array = get_array(data_loc, 'data_imag')
        if storage_str == 'ROW_MAJOR':
            # Dims are swapped from get_array
            imag_array = imag_array.reshape((anum, cnum))
        data.load_data_as_tuple((real_array, imag_array), ap_flag)
    else:
        data.load_data(real_array)
    return data


# Write a MATSData dataset to an H5 path location
#   data_loc = valid location ID of file or group to receive the dataset
#   name_str = string ID for this new dataset
#   value = cell data to be written
# Returns 0 on success, or 1 if failure
def create_mats_data(loc, name_str, value):
    if __check_create(loc, name_str):
        return 1
    if type(value) != mats.Data:
        return mats.log.error(f'Data is type {type(value)}, not MATS Data')
    data_loc = loc.create_group(name_str)
    create_value(data_loc, 'data_anum', value['anum'])
    create_value(data_loc, 'data_ares', value['ares'])
    create_value(data_loc, 'data_cnum', value['cnum'])
    create_value(data_loc, 'data_cres', value['cres'])
    create_value(data_loc, 'data_precision', PRECISIONS[value['precision']])
    create_value(data_loc, 'data_format', FORMATS[value['format']])
    create_value(data_loc, 'data_storage', STORAGES[value['storage']])
    if value['format'] == 'REAL_IMAG':
        data_loc['data_real'] = value['real'].T
        if value.is_complex():
            data_loc['data_imag'] = value['imag'].T
    elif value['format'] == 'AMP_PHASE':
        data_loc['data_real'] = value['abs'].T
        data_loc['data_imag'] = value['phase'].T
    else:
        return mats.log.error('Invalid format {}'.format(value['format']))
    return 0


def get_groundtruth(hh, name_str):
    """
    Read a MATS groundtruth from an H5 path location

    :param hh: Valid H5 file or group object.
    :type hh: h5py.File|h5py.Group
    :param name_str: H5 location of string dataset.
    :type name_str: str

    :return: MATS groundtruth list from `name_str` location.
    :rtype: [dict]
    """
    if __check_get(hh, name_str):
        return []
    data = hh[name_str]
    n = data['x'].size
    if n == 0:
        # Empty group - empty vector.
        return []

    # All data loaded successfully. Fill in the output vector.
    gt_data = [dict()] * n
    for k, gt in enumerate(gt_data):
        gt['x'] = data['x'][k]
        gt['y'] = data['y'][k]
        gt['num'] = data['num'][k]
        gt['type'] = data['type'][k]
    return gt_data


def create_groundtruth(hh, name_str, data):
    if name_str is None or not name_str:
        mats.log.error("Name string is None or empty.")
        return False

    if name_str in hh:
        # We can still use this group if it's empty
        gh = hh[name_str]
        if 'x' in gh or 'y' in gh or 'num' in gh or 'type' in gh:
            mats.log.error(f'Groundtruth at {name_str} already exists.')
            gh.close()
            return False
    else:
        # Create new group and label it.
        gh = hh.create_group(name_str)
        create_attr_string(gh, "type", "groundtruth")

    # At this point, we have a valid gid to an empty group.
    # Put values into arrays.
    tmp_x = np.array([d['x'] for d in data])
    tmp_y = np.array([d['y'] for d in data])
    tmp_num = np.array([d['num'] for d in data])
    tmp_type = np.array([d['type'] for d in data])

    mats.h5.create_array(gh, "x", tmp_x)
    mats.h5.create_array(gh, "y", tmp_y)
    mats.h5.create_array(gh, "num", tmp_num)
    mats.h5.create_array(gh, "type", tmp_type)
    gh.close()
    return True


def update_groundtruth(hh, name_str, data):
    """
    Update an existing MATS groundtruth in a file or group.

    :param hh: Valid H5 file or group object.
    :type hh: h5py.File|h5py.Group
    :param name_str: H5 location of dataset.
    :type name_str: str
    :param data: Updated MATS groundtruth data.
    :type data: [dict]

    :return: Returns True on success.
    :rtype: bool
    """
    if __check_get(hh, name_str):
        return False
    gh = hh[name_str]

    # New and existing groundtruth must be the same size.
    n = len(data)
    if gh['x'].size != n or gh['y'].size != n or gh['num'].size != n or gh['type'].size != n:
        mats.log.error("New and existing vector sizes must match.")
        return False
    if n == 0:
        return False

    # Put values into arrays.
    tmp_x = np.array([d['x'] for d in data])
    tmp_y = np.array([d['y'] for d in data])
    tmp_num = np.array([d['num'] for d in data])
    if type(data[0]['type']) == str:
        tmp_type = np.array([mats.gt.type2int(d['type']) for d in data])
    else:
        tmp_type = np.array([d['type'] for d in data])

    # Update H5 arrays.
    if not update_array(gh, "x", tmp_x):
        mats.log.error("Failed to update 'x' in groundtruth vector group.")
        return False
    if not update_array(gh, "y", tmp_y):
        mats.log.error("Failed to update 'y' in groundtruth vector group.")
        return False
    if not update_array(gh, "num", tmp_num):
        mats.log.error("Failed to update 'num' in groundtruth vector group.")
        return False
    if not update_array(gh, "type", tmp_type):
        mats.log.error("Failed to update 'type' in groundtruth vector group.")
        return False
    return True


def move_groundtruth(hh, source, dest):
    # Check inputs
    if source is None:
        mats.log.error("None source value.")
        return False
    if dest is None:
        mats.log.error("None destination value.")
        return False
    if source not in hh:
        mats.log.error(f'Source {source} does not exist.')
        return False
    if dest in hh:
        mats.log.error(f'Destination link "{dest}" already exists.')
        return False
    gh = hh[source]

    # Create new group and label it.
    gh2 = hh.create_group(dest)
    create_attr_string(gh2, "type", "groundtruth")
    create_value(gh2, "date", mats.time.datenum(mats.time.datenow()))

    # Move x, y, num, type
    if "x" in gh:
        hh.move(source+'/x', dest+'/x')
    if "y" in gh:
        hh.move(source+"/y", dest+"/y")
    if "num" in gh:
        hh.move(source+"/num", dest+"/num")
    if "type" in gh:
        hh.move(source+"/type", dest+"/type")
    return True


# NOTE: For the purposes of saving GT info for GT-contact comparisons
def create_gt_list(loc, name_str, gt_data_list):
    list_loc = loc.create_group(name_str)
    for q, gt_data in enumerate(gt_data_list):
        create_gt_entry(list_loc, 'gt_{}'.format(q+1), gt_data)
    create_value(list_loc, 'length', len(gt_data_list))


def get_gt_list(loc, name_str):
    list_loc = loc[name_str]
    gt_list = []
    num = get_value(list_loc, 'length')
    for q in range(num):
        gt_entry = get_gt_entry(list_loc, 'gt_{}'.format(q+1))
        gt_list.append(gt_entry)
    return gt_list


def create_gt_entry(loc, name_str, gt_data):
    data_loc = loc.create_group(name_str)
    create_value(data_loc, 'enabled', int(gt_data['enabled']))
    for f in ['x', 'y', 'num', 'type']:
        create_value(data_loc, f, gt_data[f])
    for f in ['side', 'fn']:
        create_string(data_loc, f, gt_data[f])


def get_gt_entry(loc, name_str):
    data_loc = loc[name_str]
    gt_data = {'enabled': bool(get_value(data_loc, 'enabled'))}
    for f in ['x', 'y', 'num', 'type']:
        gt_data[f] = get_value(data_loc, f)
    for f in ['side', 'fn']:
        gt_data[f] = get_string(data_loc, f)
    return gt_data


# Load arbitrary data at given H5 path location
# NOTE: This function is intended to be used as a subroutine in the process
#   of loading nested structures.  When reading root-level fields, the proper
#   subroutine (e.g., get_string(...)) should be used instead.
def _load_field(loc):
    t = loc.attrs['type'][0].decode()
#    print(t)
    if t == 'empty' or 'data' not in loc:
        if _debug_check('DETAILED'):
            print('%s --> empty' % loc.name)
        return None
    elif t == 'char':
        if _debug_check('DETAILED'):
            print('%s --> char' % loc.name)
        return get_string(loc, 'data')
    elif t == 'struct':
        if _debug_check('DETAILED'):
            print('%s --> struct' % loc.name)
        return get_mats_struct(loc, 'data')
    elif t == 'cell':
        if _debug_check('DETAILED'):
            print('%s --> cell' % loc.name)
        return get_mats_cell(loc, 'data')
    else:  # numerical data
        if loc['data'].size == 1:
            # scalar case, extract value from array
            if _debug_check('DETAILED'):
                print('%s --> %s, scalar' % (loc.name, t))
            return get_value(loc, 'data')
        else:
            # vector/matrix case, keep ndarray
            if _debug_check('DETAILED'):
                print('%s --> %s' % (loc.name, t))
            return get_array(loc, 'data')


# Save arbitrary data at given H5 path location
# NOTE: This function is intended to be used as a subroutine in the process
#   of saving nested structures.  When writing root-level fields, the proper
#   subroutine (e.g., create_string(...)) should be used instead.
def _save_field(gid_loc, loc_str, value):
    t = type(value)
    data_str = '%s' % gid_loc.name
    # Depending on the type of data being saved, loc_str could indicate either
    #   a dataset or a group to which value will be written
    if value is None:   # occurs in empty element in cell array
        mats.log.info('empty --> %s:%s' % (data_str, loc_str))
        create_attr_string(gid_loc, 'type', 'empty')
    elif t is str:
        mats.log.info(f'char --> {data_str}:{loc_str}')
        create_attr_string(gid_loc, 'type', 'char')
        create_string(gid_loc, loc_str, value)
    elif t is np.ndarray:
        temp = value.transpose()
        mats.log.info(f'{temp.dtype} {temp.shape} --> {data_str}:{loc_str}')
        # NOTE: All numeric values appear to be stored as doubles, although
        #   that may not necessarily be true in all cases
        create_attr_string(gid_loc, 'type', 'double')
        create_array(gid_loc, loc_str, value)
    # NOTE: Native python implementation uses dict instead of MATS Struct b/c
    #   they are functionally equivalent
    elif t in [mats.Struct, dict]:
        mats.log.info('struct --> %s' % data_str)
        create_attr_string(gid_loc, 'type', 'struct')
        create_mats_struct(gid_loc, loc_str, value)
    # NOTE: Native python implementation uses list instead of MATS Cell b/c
    #   they are functionally equivalent
    elif t in [mats.Cell, list]:
        mats.log.info('cell --> %s' % data_str)
        create_attr_string(gid_loc, 'type', 'cell')
        create_mats_cell(gid_loc, loc_str, value)
    else:   # scalar numerical data
        # NOTE: This uses the default type conversion
        temp = np.array([value])
        mats.log.info('%s --> %s:%s' % (temp.dtype, data_str, loc_str))
        # NOTE: All numeric values appear to be stored as doubles, although
        #   that may not necessarily be true in all cases
        create_attr_string(gid_loc, 'type', 'double')
        create_array(gid_loc, loc_str, temp)
