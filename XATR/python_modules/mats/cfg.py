# DISTRIBUTION STATEMENT D. Distribution authorized to the Department of
# Defense and U.S. DoD contractors only; Administrative or Operational Use; 1
# Jan 2017. Other U.S. requests shall be referred to Naval Surface Warfare
# Center Panama City Division, ATTN: Technical Director NSWC PCD, 110 Vernon
# Ave, Panama City, FL 32407.
"""
mats.cfg
--------
Contains classes and methods for configuring the main MATS framework.
"""
import os
import os.path as osp
import mats
import mats.log
import mats.time
from mats.filesystem import mats_config_dir, mats_working_dir
import xml.etree.ElementTree as et
from threading import Lock
from xml.dom import minidom
from glob import glob


# Mutex for config operations to prevent multiple processes from changing
# things at the same time.
gMatsCfgLock = Lock()


_roc_format = {
    'PdPc': 'array-float',
    'Fad': 'array-float',
    'Threshold': 'array-float',
    'NumberOfPositives': 'int'
}


# ATR Configuration field names in file
# _cfg_format = {
#     'sensor': 'str',
#     'UUID': 'str',
#     'sourceUUID': 'str',
#     'name': 'str',
#     'date': 'float',
#     'description': 'str',
#     'threshold': 'float',
#     'ThreadSafe': 'bool',
#     'location': 'array-str',
#     'dependency': 'array-str',
#     'ROC': 'array-roc',
#     'disabled': 'bool',
#     'version': 'str',
#     'environment': 'array-str'
# }


# ATR Configuration field names (file name, loaded name, type)
_cfg_fields = [
    ('sensor', 'Sensor', 'str'),
    ('UUID', 'Uuid', 'str'),
    ('sourceUUID', 'SourceConfigId', 'str'),
    ('name', 'Name', 'str'),
    ('date', 'Date', 'float'),
    ('description', 'Description', 'str'),
    ('threshold', 'Threshold', 'float'),
    ('ThreadSafe', 'ThreadSafe', 'bool'),
    ('location', 'Location', 'array-str'),
    ('dependency', 'Dependency', 'array-str'),
    ('ROC', 'RoCs', 'array-roc'),
    ('disabled', 'Disabled', 'bool'),
    ('version', 'Version', 'str'),
    ('environment', 'Environment', 'array-str')
]


def _roc_extract(root):
    roc = {}
    for item in list(root):
        if item.tag not in _roc_format:
            print('Skipping unknown ROC field ({})'.format(item.tag))
            continue
        if _roc_format[item.tag] == 'float':
            roc[item.tag] = float(item.text)
        elif _roc_format[item.tag] == 'int':
            roc[item.tag] = int(item.text)
        elif _roc_format[item.tag] == 'array-float':
            roc[item.tag] = [float(v) for v in item.text.split(';') if v]
        else:
            print('Skipping "{}" field'.format(item.tag))
    return roc


def _roc_dom(root, roc):
    for fld in _roc_format:
        if fld not in roc:
            print('Missing "{}" ROC field.'.format(fld))
            et.SubElement(root, fld)
            continue

        if _roc_format[fld] == 'float':
            et.SubElement(root, fld).text = roc[fld]
        elif _roc_format[fld] == 'array-float':
            et.SubElement(root, fld).text = str(
                roc[fld])[1:-1].replace(', ', ';')
        else:
            print('Skipping "{}" ROC field'.format(fld))


def _et_indent(elem, level=0):
    i = "\n" + level*"  "
    j = "\n" + (level-1)*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for subelem in elem:
            _et_indent(subelem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = j
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = j
    return elem


def create_atr_configuration():
    """Creates an empty dict with fields for a ATR "cfg" file. """
    return {'Uuid': '', 'SourceConfigId': '', 'Sensor': '', 'Name': '',
            'Description': '', 'Version': '', 'Location': [], 'Environment': [],
            'Date': -1.0, 'Threshold': -1.0, 'RoCs': [], 'Dependency': [],
            'Active': False, 'Disabled': False, 'ThreadSafe': False}


def create_atr_roc():
    """
    Creates an empty dict with fields for an ATR ROC used in an ATR "cfg" file.
    """
    return {'PdPc': [], 'Fad': [], 'Threshold': [], 'NumberOfPositives': 0}


def load_cfg_file(fn):
    """
    Loads an ATR configuration CFG file.

    :param fn: File path to ATR CFG file.
    :type fn: str
    :return: Loaded CFG information.
    :rtype: dict
    """
    tree = et.parse(fn)
    root = tree.getroot()

    cfg = {
        'Date': 0.0,
        'Version': '',
        'Threshold': 0.0,
        'ThreadSafe': 0,
        'Location': [],
        'Environment': [],
        'Dependency': [],
        'RoCs': [],
        'Disabled': False,
        'Active': False
    }

    for child in root:
        field = [it for it in _cfg_fields if it[0] == child.tag]
        if len(field) == 0:
            print('Skipping unknown field ({})'.format(child.tag))
            continue
        field = field[0]

        if field[2] == 'str':
            cfg[field[1]] = child.text
        elif field[2] == 'float':
            cfg[field[1]] = float(child.text)
        elif field[2] == 'bool':
            cfg[field[1]] = bool(child.text)
        elif field[2] == 'array-str':
            cfg[field[1]].append(child.text)
        elif field[2] == 'array-roc':
            cfg[field[1]].append(_roc_extract(child))
        else:
            print('Skipping "{}" field'.format(child.tag))

    # Correct names of fields
    names = [('UUID', 'Uuid'), ('sourceUUID', 'SourceConfigId'),
             ('sensor', 'Sensor'), ('name', 'Name'),
             ('description', 'Description'), ('version', 'Version'),
             ('threshold', 'Threshold'), ('location', 'Location'),
             ('environment', 'Environment'), ('dependency', 'Dependency'),
             ('disabled', 'Disabled'), ('date', 'Date'), ('ROC', 'RoCs')]
    for name in names:
        if name[0] in cfg:
            cfg[name[1]] = cfg[name[0]]
            del cfg[name[0]]
    return cfg


def save_cfg_file(fn, cfg):
    """
    Saves an ATR configuration CFG file.

    :param fn: File path for ATR CFG file.
    :type fn: str
    :param cfg: ATR configuration CFG data.
    :type cfg: dict
    :return: None
    """
    root = et.Element('config')

    for fld in _cfg_fields:
        if fld[1] not in cfg:
            print('Missing field ({})'.format(fld[1]))
            et.SubElement(root, fld[0])
            continue

        if fld[2] == 'str':
            et.SubElement(root, fld[0]).text = cfg[fld[1]]
        elif fld[2] in ['float', 'int']:
            et.SubElement(root, fld[0]).text = str(cfg[fld[1]])
        elif fld[2] == 'bool':
            et.SubElement(root, fld[0]).text = str(int(cfg[fld[1]]))
        elif fld[2] == 'array-str':
            for item in cfg[fld[1]]:
                et.SubElement(root, fld[0]).text = item
        elif fld[2] == 'array-roc':
            for roc in cfg[fld[1]]:
                el = et.SubElement(root, fld[0])
                _roc_dom(el, roc)
        else:
            print(f'Skipping "{fld[1]}" field')

    xmlstr = et.tostring(root, 'utf-8')
    xmlstr = minidom.parseString(xmlstr).toprettyxml(indent='  ')
    with open(fn, 'w') as fid:
        fid.write(xmlstr)
    return


def check_config(config: dict):
    """
    Check an ATR_Configuration for completeness. Fill in certain fields if
    needed.

    Required fields: Uuid, Sensor, Threshold

    The following fields will be filled in if empty:
        SourceUUID, Date, Version
    
    :param config: ATR Configuration to be checked.
    :type config: dict
    :return: True if config is okay. False if config fails required field
             checks.
    :rtype: bool
    """
    if ('Uuid' not in config) or (len(config['Uuid']) == 0):
        mats.log.warn("Empty or missing config 'Uuid' field")
        return False
    if ('Sensor' not in config) or (len(config['Sensor']) == 0):
        mats.log.warn("Empty or missing config 'Sensor' field")
        return False
    if ('Threshold' not in config) or config['Threshold'] < 0 \
            or config['Threshold'] > 1:
        mats.log.warn("Missing or invalid config 'Threshold' field")
        return False

    if ('Date' not in config) or config['Date'] < 0:
        mats.log.info("Missing or invalid config 'Date'. Setting to now.")
        config['Date'] = mats.time.datenum(mats.time.datenow())
    if ('Version' not in config) or len(config['Version']) == 0:
        mats.log.info(
            "Missing or invalid config 'Version'. Setting to current.")
        config['Version'] = mats.get_mats_version()
    if ('SourceConfigId' not in config) or len(config['SourceConfigId']) == 0:
        mats.log.info("Missing or invalid config 'SourceConfigId'.")
        config['SourceConfigId'] = "00000000-0000-0000-0000-000000000000"

    # Convert UUIDs to uppercase
    config['Uuid'] = config['Uuid'].upper()
    config['SourceConfigId'] = config['SourceConfigId'].upper()
    return True


def read_config(uuid: str, cfg_dir = None):
    """
    Reads an ATR CFG file into an ATR_Configuration structure.

    :param uuid: Name of ATR configuration to load.
    :type uuid: str
    :param cfg_dir: Configuration directory to search for ATR CFG file. Will use
      the MATS config directory if None is given.
    :type cfg_dir: str, optional
    :return: Loaded ATR CFG information.
    :rtype: dict
    """
    if cfg_dir is None:
        cfg_dir = mats_config_dir()
    filename = osp.join(cfg_dir, uuid+'.cfg')
    gMatsCfgLock.acquire()
    config = load_cfg_file(filename)
    gMatsCfgLock.release()
    return config


def write_config(config: dict, cfg_fn: str = None, force: bool = False,
                 cfg_dir: str = None):
    """
    Writes an ATR_Configuration structure to an ATR CFG file. By default, the
    CFG file is saved to the 'config' directory in the XATR working directory
    with its filename being the config UUID.

    :param config: ATR CFG structure.
    :type config: dict
    :param cfg_fn: Desired ATR CFG filename/location. The default is None.
    :type cfg_fn: str, optional
    :param force: Allow overwriting of existing files. The default is False.
    :type force: bool, optional
    :param cfg_dir: Configuration directory.
    :type cfg_dir: str, optional
    :return: None
    """
    if cfg_dir is None:
        cfg_dir = mats_config_dir()
    if cfg_fn is None:
        cfg_fn = osp.join(cfg_dir, config['Uuid']+'.cfg')

    # TODO(Bradley): Missing any checks and force does not do anything.
    gMatsCfgLock.acquire()
    save_cfg_file(cfg_fn, config)
    gMatsCfgLock.release()
    return


def scan_configs(sensor=None, cfg_dir=None):
    """
    Search for available ATR configurations. Optionally, filters list by sensor.
    By default, the mats_config_dir is searched.

    :param sensor: Sensor filter.
    :type sensor: str, optional
    :param cfg_dir: Configuration directory to search.
    :type cfg_dir: str, optional
    :return: List of ATR configurations.
    :rtype: list
    """
    if cfg_dir is None:
        cfg_dir = mats_config_dir()

    # Compile a list of configs from the config folder.
    file_list = glob(osp.join(cfg_dir, '*.cfg'))
    configs = []
    for cfg in file_list:
        cfg_name = mats.filesystem.file_basename(cfg)
        if cfg_name == 'default':
            continue
        if 'blacklist' in cfg_name:
            continue
        config = read_config(cfg_name, cfg_dir)
        if not check_config(config):
            continue
        if sensor is not None and not sensor == config['Sensor']:
            continue
        configs.append(config)
    return configs


# MATS_cfg ---------------------------------------------------------------------
class Cfg:
    """
    **MATS Configuration Manager**

    This class handles config (CFG) files and the configuration information
    they contain.  A related class is AtrConfig, which handles an atrconfig
    (ATRCFG) file and processing stream configuration.

    Each CFG file contains a single configuration and is associated with an
    ATRCFG file, which contains the actual processing stream configuration and
    is handled by the MATS_atrconfig class.

    Typically, an ATRCFG file has the same basename as its associated CFG file.
    However, a CFG file may instead use an ATRCFG from a previous config in its
    configuration chain.

    In addition, there is a special file, "default.cfg".  This file does not
    contain a configuration, but rather, it holds system-wide configuration
    information, such as the writeContacts flag and the default configuration
    IDs for each sensor.
    """
    def __init__(self, cfg_dir=None, work_dir=None):
        if cfg_dir is None:
            self._cfg_dir = mats_config_dir()
        else:
            self._cfg_dir = cfg_dir

        if work_dir is None:
            self._wrk_dir = mats_working_dir()
        else:
            self._wrk_dir = work_dir

        # The default.cfg file is assumed to be in the config directory. If we
        # cannot find one, create a default structure to work with (not saved
        # unless requested).
        self._filename = osp.join(self._cfg_dir, 'default.cfg')
        if osp.exists(self._filename):
            self._doc_tree = et.parse(self._filename)
            self._doc = self._doc_tree.getroot()
        else:
            mats.log.warn('default.cfg not found.')
            dfg_xml = '<?xml version="1.0"?><config>'\
                      '<writeContacts>0</writeContacts>'\
                      '<maxThreads>4</maxThreads>'\
                      '<maxWorkers>5</maxWorkers>'\
                      '</config>'
            self._doc_tree = et.fromstring(dfg_xml)
            self._doc = self._doc_tree.getroot()

        self._default_configs = {}
        self._load_default_configurations()

        return

    def _load_default_configurations(self):
        sensors = self._doc.findall('system')
        for sensor in sensors:
            cfg_name = sensor.find('defaultCfg').text
            self._default_configs[sensor.find('name').text] = cfg_name
        return

    def _limit_chain(self, config):
        atrcfg_name = self.atrconfig_name(config)
        if atrcfg_name is None:
            return False

        # If there is no chain, leave the source UUID alone
        atrcfg_name = mats.filesystem.file_basename(atrcfg_name)
        if atrcfg_name == config['UUID']:
            return True

        # Otherwise, source UUID should be the ATRCFG name
        config['SourceUUID'] = atrcfg_name
        return True

    def save(self):
        """Saves system-wide configurations."""
        # Back up any existing config file.
        if osp.exists(self._filename+'.bak'):
            os.remove(self._filename+".bak")
        os.rename(self._filename, self._filename+".bak")
        # Save XML document.
        try:
            # ElementTree does not have a "pretty" output. So, we will use
            # minidom instead
            # TODO(Bradley): Python 3.9 adds an indent method to ElementTree to
            #                give a pretty output. Then minidom can be dropped.
            _et_indent(self._doc)
            self._doc_tree.write(self._filename, xml_declaration=True)
            # xmlstr = et.tostring(self._doc)
            # xmlstr = minidom.parseString(xmlstr).toprettyxml()
            # with open(self._filename, 'w') as fh:
            #     fh.write(xmlstr)
        except:
            mats.log.error("Failed to write default.cfg")
        return

    def configuration(self, sensor, uuid=None):
        """
        Loads the specified configuration. If no UUID is specified, loads the
        default configuration for sensor.

        .. note:: If the configuration is found, it will be loaded even if it
                  is disabled.

        :param sensor: Name of the sensor.
        :type sensor: str
        :param uuid: UUID of the desired configuration.  If None, the default
          config for the sensor will be loaded.
        :type uuid: str, optional
        :return: Requested configuration structure (CFG).
        :rtype: dict
        """
        # Select config based on the information available.
        if uuid is None:
            # No UUID specified.  Use default config for this sensor.
            if sensor not in self._default_configs:
                raise ValueError('Not default for sensor "{}"'.format(sensor))
            uuid = self._default_configs[sensor]

        # Read the selected config.
        config = read_config(uuid, self._cfg_dir)
        if not check_config(config):
            raise RuntimeError('Invalid cfg for "{}"'.format(uuid))

        # Check the sensor name, if applicable.
        if sensor != config['sensor']:
            raise RuntimeError(
                "Configuration sensor does not match given sensor.")

        if self._default_configs[sensor] == uuid:
            config.active = True

        return config

    def configurations(self, sensor, disabled_also=None):
        if disabled_also is None:
            disabled_also = False

        config_list = scan_configs(sensor, self._cfg_dir)
        # sortConfigs(configList)

        # Set active flag for default
        dft_uuids = [self._default_configs[c] for c in self._default_configs]
        for c in config_list:
            if c['Uuid'] in dft_uuids:
                c['Active'] = True
            else:
                c['Active'] = False

        if not disabled_also:
            config_list = [c for c in config_list if not c['Disabled']]
        return config_list

    def save_configuration(self, new_atrcfg, force=None, disable_parent=None):
        if force is None:
            force = False

        # Get parent UUID before limiting the chain.
        parentcfg = new_atrcfg['SourceUUID']

        if not check_config(new_atrcfg):
            raise ValueError('Invalid AtrConfig.')

        # Make sure ATRCFG file doesn't already exist in config directory
        atrcfg_fn = osp.join(self._cfg_dir, new_atrcfg['UUID'] + ".atrcfg")
        if osp.exists(atrcfg_fn):
            if force:
                # Make a backup of the atrcfg
                if osp.exists(atrcfg_fn+'.bak'):
                    os.remove(atrcfg_fn+".bak")
                os.rename(atrcfg_fn, atrcfg_fn+".bak")
            else:
                mats.log.error("Atrcfg file already exists!")
                return False

        # Look for unsaved atrcfg
        work_loc = osp.join(self._wrk_dir, new_atrcfg['UUID']+".atrcfg")
        if not osp.exists(work_loc):
            # Make sure there is a parent ATRCFG and limit the chain to 1 deep.
            if self._limit_chain(new_atrcfg):
                mats.log.error("Missing atrcfg. Unable to save.")
                return False

        # Before writing the config, make sure we have all the dependency files.
        for dep in new_atrcfg['dependency']:
            # First, check the config directory in case we are coming from a
            # parent configuration.
            dep_fn = osp.join(self._cfg_dir, dep)
            if not osp.exists(dep_fn):
                # If not, then look in the working directory instead.
                dep_fn = osp.join(self._wrk_dir, dep)
                if not osp.exists(dep_fn):
                    # If we still can't find it, then give up.
                    mats.log.error(
                        "Dependency file ({}) missing.".format(dep_fn))
                    return False

        # Write/update the configuration file.
        write_config(new_atrcfg, force=force, cfg_dir=self._cfg_dir)

        # Install unsaved atrcfg
        if osp.exists(work_loc):
            install_loc = osp.join(self._cfg_dir, atrcfg_fn)
            os.rename(work_loc, install_loc)

        # Move dependency files to config directory as needed. Also, clean up
        # any extra copies that didn't get used. (We are assuming here that if a
        # dependency with the same name already exists in the config directory,
        # that it is an exact copy. If that isn't the case, then the dependency
        # file should be renamed.)
        for dep in new_atrcfg['dependency']:
            # Check both directories for the dependency file.
            cfg_loc = osp.join(self._cfg_dir, dep)
            work_loc = osp.join(self._wrk_dir, dep)

            if osp.exists(cfg_loc):
                # It already exists in the config directory. Check for a copy in
                # the working directory and clean it out.
                if osp.exists(work_loc):
                    mats.log.info(
                        f"Dependency file '{work_loc}' is redundant "
                        f"and is being deleted.")
                    os.remove(work_loc)
            elif osp.exists(work_loc):
                # We need to move the file from the working directory.
                os.rename(work_loc, cfg_loc)

        if disable_parent:
            self.set_configuration_state(parentcfg, False)
        return True

    @property
    def write_contacts(self):
        return int(self._doc.find('writeContacts').text)

    @write_contacts.setter
    def write_contacts(self, value: int):
        self._doc.find('writeContacts').text = str(value)
        return

    @property
    def max_threads(self):
        return int(self._doc.find('maxThreads').text)

    @max_threads.setter
    def max_threads(self, value: int):
        self._doc.find('maxThreads').text = str(value)
        return

    @property
    def max_workers(self):
        """
        Max number of workers requested for concurrent files/job processing.
        """
        return int(self._doc.find('maxWorkers').text)

    @max_workers.setter
    def max_workers(self, value: int):
        self._doc.find('maxWorkers').text = str(value)
        return

    def get_option(self, name):
        ele = self._doc.find(name)
        if ele is None:
            mats.log.warn('Failed to find "{}" from config file.'.format(name))
            return None
        return ele.text

    def set_option(self, name, value, create=None):
        if create is None:
            create = False

        ele = self._doc.find(name)
        if ele is None:
            if not create:
                mats.log.error('Config field "{}" do not exist.'.format(name))
                return
            # Field does not exist, so let's add it.
            ele = et.SubElement(self._doc, name)
        ele.text = str(value)
        return

    def set_configuration_state(self, uuid: str, state: bool):
        config = read_config(uuid, self._cfg_dir)
        config['disabled'] = not state
        write_config(config, force=True, cfg_dir=self._cfg_dir)
        return

    def default_configuration(self, sensor: str, uuid: str):
        # Make sure the sensor and config match.
        config = read_config(uuid, self._cfg_dir)
        if not check_config(config):
            mats.log.error('Invalid config.')
            return False
        if not config['sensor'] == sensor:
            mats.log.error("Sensor name does not match config.")
            return False
        if not config['UUID'] == uuid:
            mats.log.error("UUID does not match config.")
            return False

        config['active'] = True
        self._default_configs[sensor] = uuid

        # Update default UUID for sensor
        doc_sensor = self._doc.findall('./system[name="{}"]'.format(sensor))
        if not doc_sensor:
            # Default sensor not found. So we need to add it.
            new_sens = et.SubElement(self._doc, 'system')
            ele = et.SubElement(new_sens, 'name')
            ele.text = sensor
            ele = et.SubElement(new_sens, 'defaultCfg')
            ele.text = uuid
        else:
            doc_sensor = doc_sensor[0]  # There should only be one
            doc_sensor.find('defaultCfg').text = uuid
        return

    def discard_configuration(self, uuid: str):
        atrcfg_fn = osp.join(self._wrk_dir, uuid+".atrcfg")
        if osp.exists(atrcfg_fn):
            os.remove(atrcfg_fn)
        return

    def atrconfig_name(self, uuid):
        # First try: UUID has its own atrcfg file
        if type(uuid) == dict:
            # Assuming 'uuid' is an ATR Configuration dict
            uuid = uuid['UUID']

        name = osp.join(self._cfg_dir, uuid+'.atrcfg')
        if osp.exists(name):
            return name

        # Next try: Get source config UUID and check for its atrcfg file.
        # # Repeat as necessary.
        while True:
            config = read_config(uuid, self._cfg_dir)
            curr = config['SourceUUID']
            if curr == '00000000-0000-0000-0000-000000000000':
                mats.log.error('Unable to find atrcfg')
                return None

            # Look for atrconfig
            name = osp.join(self._cfg_dir, curr+'.atrcfg')
            if osp.exists(name):
                break
        return name

    def refresh(self):
        self._doc_tree = et.parse(self._filename)
        self._doc = self._doc_tree.getroot()
        return

    def list_sensors(self):
        # Scan the directory and sort by sensor name/date.
        configs = scan_configs(cfg_dir=self._cfg_dir)

        # Gather stats
        sensors = []
        for cfg in configs:
            if cfg['sensor'] not in sensors:
                sensors.append(cfg['sensor'])
        return sensors

    def verify_configuration(self, uuid: str):
        # Make sure the config can be loaded.
        try:
            config = read_config(uuid, self._cfg_dir)
        except:
            return False, "Failed to read CFG file."

        # Make sure the UUID, source UUID, sensor, and threshold fields aren't
        # empty.
        if config['UUID'] is None or len(config['UUID']) == 0:
            return False, 'Config "UUID" field is empty.'
        if config['sourceUUID'] is None or len(config['sourceUUID']) == 0:
            return False, 'Config "sourceUUID" field is empty.'
        if config['sensor'] is None or len(config['sensor']) == 0:
            return False, 'Config "sensor" field is empty.'
        if config['threshold'] < 0 or config['threshold'] > 1:
            return False, 'Config "threshold" field is empty or invalid.'

        # UUIDs must match.
        if not config['UUID'] == uuid:
            return False, 'UUID does not match config "UUID" field.'

        # Make sure the ATRCFG exists and check it.
        atrcfg_name = self.atrconfig_name(uuid)
        if atrcfg_name is None:
            return False, 'ATRCFG file not found.'

        atrcfg = mats.AtrConfig()
        try:
            atrcfg.load(atrcfg_name)
        except:
            return False, 'Failed to load ATRCFG file: {}'.format(atrcfg_name)

        # TODO(Bradley): AtrConfig does not have a check. So, this cannot be
        #                done yet.
        # if not atrcfg.check():
        #     return False, 'ATRCFG file is incomplete: {}'.format(atrcfg_name)

        # Make sure all dependency files exist.
        for dep in config['dependency']:
            dep_file = osp.join(self._cfg_dir, dep)
            if not osp.exists(dep_file):
                return False, 'Missing dependency file: {}'.format(dep)
        return True, ''
