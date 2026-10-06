# DISTRIBUTION STATEMENT D. Distribution authorized to the Department of
# Defense and U.S. DoD contractors only; Administrative or Operational Use; 1
# Jan 2017. Other U.S. requests shall be referred to Naval Surface Warfare
# Center Panama City Division, ATTN: Technical Director NSWC PCD, 110 Vernon
# Ave, Panama City, FL 32407.

import os
import os.path as osp
import yaml  # Used for mats.yml config file

__mats_config_file = osp.join(os.getcwd(), 'mats.yml')
sys_config = {}


def __sys_config_init():
    global sys_config
    yml_updates = False
    if osp.exists(__mats_config_file):
        with open(__mats_config_file, 'r') as fh:
            sys_config = yaml.safe_load(fh)
    else:
        sys_config = {
            'gt_type_encoding': {},
            'xatr_install_dir': None,
            'xatr_working_dir': None
        }
        yml_updates = True

    if type(sys_config['gt_type_encoding']) == list:
        raise ValueError('Invalid "mats.yml" file.')

    # Add default GT type encoding if not present.
    if 'Default' not in sys_config['gt_type_encoding']:
        try:
            sys_config['gt_type_encoding']['Default'] = {
                'mlo': ['UNKNOWN'],
                'mno': ['UNKNOWN']
            }
        except:
            print('???')
        yml_updates = True

    if yml_updates:
        print("!! Saving MATS system config to 'mats.yml'")
        with open(__mats_config_file, 'w') as fh:
            yaml.dump(sys_config, fh, default_flow_style=False)
    return


def sys_config_save():
    with open(__mats_config_file, 'w') as fh:
        yaml.dump(sys_config, fh)


# Initialize system config
__sys_config_init()


# MATS Objects ----------------------------------------------------------------
from .mod import (  # noqa: W0611
    Detector, Feature, Classifier, Reader, Normalizer, Interface, Tracker
)

import mats.filesystem  # noqa: E402
import mats.log  # noqa: E402

try:
    import PyMATS_core as mc

    if sys_config.get('xatr_install_dir', None) is not None:
        mc.mats_install_dir(sys_config['xatr_install_dir'])
    if sys_config.get('xatr_working_dir', None) is not None:
        mc.mats_working_dir(sys_config['xatr_working_dir'])
    cpp_backend = True
    print('Using PyMATS_core backend')
except ModuleNotFoundError:
    mc = None
    cpp_backend = False
    print('Using Python backend')

# Setup main MATS data structures
from ._core.data import Data  # noqa: E402
from ._core.struct import Struct  # noqa: E402
from ._core.cell import Cell  # noqa: E402
from ._core.archive import Archive, Archiver, remove_gt  # noqa: E402
from ._core.input import Input  # noqa: E402
from ._core.dconfig import DConfig  # noqa: E402
from ._core.cconfig import CConfig  # noqa: E402
from ._core.atrcfg import AtrConfig  # noqa: E402
from ._core.contact import Contact, ContactList  # noqa: E402
from ._core.ecdata import Ecdata, EcdataList  # noqa: E402


def __getattr__(name):
    if name == '_cpp_backend':
        print(f"Change '_cpp_backend' to 'cpp_backend'.")
        return cpp_backend


import mats.pkg  # noqa: E402
from .core import *  # noqa: W0611,W0401

# from .atr import configure, process, retrain

# This stuff needs to be removed
if cpp_backend:
    # Module Encryption / Decryption -----------------------------------------
    from PyMATS_core import load_keys

    # MATS Functions ---------------------------------------------------------
    # C++ MATS_basic
    from PyMATS_core import (  # noqa: W0611
        round, bwlabel, regionprops, find_highlight,
        img_ring_stats
    )

    # C++ MATS_error
    from PyMATS_core import (
        mats_error_enable, mats_error_disable, mats_error_report_level,
        mats_log)  # noqa: W0611

    # C++ MATS
    from PyMATS_core import (mats_contacts_to_xmlfile)  # noqa: W0611


def get_mats_version():
    if cpp_backend:
        return mc.get_mats_version()
    # TODO(Bradley): Probably should add a version file to read for a
    #  plausible version number.
    return 'xx.xx.xx'
