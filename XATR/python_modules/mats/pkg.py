# DISTRIBUTION STATEMENT D. Distribution authorized to the Department of
# Defense and U.S. DoD contractors only; Administrative or Operational Use; 1
# Jan 2017. Other U.S. requests shall be referred to Naval Surface Warfare
# Center Panama City Division, ATTN: Technical Director NSWC PCD, 110 Vernon
# Ave, Panama City, FL 32407.
"""
mats.pkg
________

This submodule provides methods for registering and creating external modules.
By default, it searches the execution "packages" folder and the MATS package
directory "Python" folder for modules.
"""
import sys
import os
from os.path import isdir, join
# import abc
import inspect
import traceback
import mats.log
import mats.sensor
from .filesystem import mats_package_dir
from .mod import (
    Detector, Tracker, Classifier, Feature, Interface, Normalizer, Reader
)

__pkg_scanned__ = False
_verbose = True
_pkg_paths = [
    os.path.join(os.getcwd(), 'packages'),
    os.path.join(mats_package_dir(), 'Python')
]
_pkg_list = []
_mod_list = []
# _sns_list = []
_engines = {}


# Add PyMATS package directory to python path
for p in reversed(_pkg_paths):
    sys.path.insert(0, p)


def _parse_module_name(mod_name):
    mod_name_parts = mod_name.split('/')
    if len(mod_name_parts) > 1:
        name = mod_name_parts[1]
        pkgname = mod_name_parts[0]
    else:
        name = mod_name_parts[0]
        pkgname = None
    return pkgname, name


def _get_module_type(mod, name):
    """Determine module type in package."""
    mod_class = getattr(mod, name)
    cls_list = inspect.getmro(mod_class)
    if Detector in cls_list:
        return 'detector'
    elif Tracker in cls_list:
        return 'tracker'
    elif Feature in cls_list:
        return 'feature'
    elif Classifier in cls_list:
        return 'classifier'
    elif Reader in cls_list:
        return 'reader'
    elif Normalizer in cls_list:
        return 'normalizer'
    elif mats.sensor.Sensor in cls_list:
        return 'sensor'
    elif Interface in cls_list:
        return 'interface'
    return None


def _interface_modules(eng_name):
    """Collect module available from an interface."""
    if _verbose:
        print('Scanning interface {}...'.format(eng_name))
    mod_types = ['detector', 'tracker', 'feature', 'classifier', 'reader',
                 'normalizer', 'sensor', 'interface', 'gt-reader', 'writer']
    mod_list = []

    if not (eng_name in _engines):
        engobj = create(eng_name)
        if engobj is not None:
            _engines[eng_name] = engobj
            _engines[eng_name].scan()
        else:
            if _verbose:
                print("Failure creating interface {}.".format(eng_name))
            return mod_list
    else:
        return []

    for t in mod_types:
        mod_names = _engines[eng_name].getType(t)
        if mod_names is None:
            print(f'No modules found for {eng_name} of type {t}.')
            continue
        for name in mod_names:
            mod_info = _engines[eng_name].module(name)
            if not mod_info:
                continue
            if _verbose:
                print("{}<{}> - {}".format(name, t, ''))
            mod_list.append({
                'name': mod_info['name'],
                'type': t,
                'desc': '',
                'pkg': mod_info['package'],
                'eng': eng_name,
                'mod': []
            })

    return mod_list


def add_package_path(new_path):
    """
    Adds a directory path to the MATS package search path.

    :param new_path: File path of directory to be added.
    """
    if new_path in _pkg_paths:
        print('Path already exists.')
        return
    _pkg_paths.append(new_path)
    sys.path.insert(0, new_path)
    return


def ensure_scan():
    """
    Preforms a scan for packages if one has not already been done.
    """
    if __pkg_scanned__:
        return
    return scan()


def scan():
    """Scan MATS Package folder for packages."""
    global __pkg_scanned__
    files = []
    for pkg_path in _pkg_paths:
        try:
            files.extend([f for f in os.listdir(pkg_path)
                          if isdir(join(pkg_path, f))])
        except FileNotFoundError:
            pass

    # Find and load packages
    for pkgname in files:
        if [pkg for pkg in _pkg_list if pkg['name'] == pkgname]:
            continue
        try:
            pkgmod = __import__(pkgname)
            if pkgmod is not None:
                _pkg_list.append({'name': pkgname, 'mod': pkgmod})
                print("Loaded {}.".format(pkgname))
        except:
            msg = traceback.format_exc()
            mats.log.warn('Failed loading Python module "'+pkgname+'": '+msg)
            print("Failure loading {}.".format(pkgname))

    # Generate list of modules from packages
    # TODO: Sensor modules really should not be added to _mod_list, but they
    # are for Python sensor modules.
    for pkg in _pkg_list:
        for k in pkg['mod'].descriptions_:
            mod_name = k
            mod_type = _get_module_type(pkg['mod'], k)
            mod_desc = pkg['mod'].descriptions_[k]
            if [m for m in _mod_list if m['name'] == mod_name and
                                        m['pkg'] == pkg['name']]:
                continue
            _mod_list.append({
                'name': mod_name,
                'type': mod_type,
                'desc': mod_desc,
                'pkg': pkg['name'],
                'eng': 'python',
                'mod': []
            })
            if _verbose:
                print(f"{mod_name}<{mod_type}> - {mod_desc}")

            if mod_type == 'interface':
                mods = _interface_modules(mod_name)
                if mods:
                    _mod_list.extend(mods)

    # Create secondary modules
    # TODO: Add blacklisting so we can avoid loading modules that
    #       aren't complete. For now, MATS_MCR is hard-coded out.
    engs = [mod for mod in _mod_list if mod['type'] == 'interface'
            and mod['name'] not in ['MATS_MCR', 'MATS_Python']]
    for eng in engs:
        try:
            mods = _interface_modules(eng['name'])
        except RuntimeError:
            mods = None
        if mods:
            _mod_list.extend(mods)

    # Load sensor modules
    sns = [s['name'] for s in _mod_list if s['type'] == 'sensor']
    for s in sns:
        snsobj = create(s)
        if snsobj is None:
            continue
        if [m for m in mats.sensor._sns_list if m.name == snsobj.name]:
            # Only add new sensors
            continue
        mats.sensor._sns_list.append(snsobj)

    __pkg_scanned__ = True
    return


def find(mod_name):
    """
    Find known instances of MATS modules with a given name.

    :param mod_name: Name of module to search for.  Format may be either
        "<module name>" or "<package name>/<module name>".
    :type mod_name: str

    :returns: List of module information entries
    :rtype: list of dict
    """
    pkgname, name = _parse_module_name(mod_name)

    # Filter module list if a package name was given.
    if pkgname:
        mats_pkgs = set([m['pkg'] for m in _mod_list])

        if pkgname not in mats_pkgs:
            # Account for differences caused by different operating systems
            if sys.platform.startswith('win'):
                if not pkgname.endswith('.dll'):
                    pkgname = f'{pkgname}.dll'
            elif sys.platform.startswith('linux'):
                if not pkgname.endswith('.so'):
                    pkgname = f'lib{pkgname}.so'
        mod_list = [m for m in _mod_list if m['pkg'] == pkgname]
    else:
        mod_list = _mod_list

    # Find the module.
    mod = [m for m in mod_list if m['name'] == name]
    if mod:
        return mod
    return None


def create(mod_name):
    """
    Creates a MATS module.

    :param mod_name: Name of module to create.
    :type mod_name: str
    :return: MATS module.
    :rtype: Object
    """
    mod = find(mod_name)
    if mod is None:
        raise ValueError(f'Module "{mod_name}" not found.')

    # We use the first found module
    mod = mod[0]
    name = mod['name']
    pkgname = mod['pkg']

    # Create module
    if mod['eng'] == 'python':
        try:
            # print('Creating Python Module: ', name)
            pkg = [pkg for pkg in _pkg_list if pkg['name'] == pkgname][0]
            mod = getattr(pkg['mod'], name)
        except:
            raise ValueError(f'Failure creating module "{name}."')
        mod = mod()
    else:
        if not (mod['eng'] in _engines):
            raise RuntimeError(f'Module {name} engine not found.')
        mod = _engines[mod['eng']].create(mod['type'], mod['name'])

    return mod


def print_module_list():
    """Print list of found modules."""
    print('----\nModules:')
    for m in _mod_list:
        print(f"  {join(m['pkg'], m['name'])} [{m['type']}]")


def get_type(mod_type):
    """
    Return list of available modules of given type. Some module types are:
    interface, sensor, reader, normalizer, detector, classifier, feature

    :param mod_type: Name of module type.
    :type mod_type: str
    :return: List of modules of requested type.
    :rtype: list
    """
    mod_list = [m for m in _mod_list if m['type'] == mod_type]
    return sorted(list(set([m['pkg'] + os.sep + m['name'] for m in mod_list])))


def module_info(mod_name):
    """
    Returns list of module information for requested module.

    :param mod_name: Name of module.
    :type mod_name: str
    :return: List of information for modules with requested name.
    :rtype: list
    """
    mod = find(mod_name)
    return [{
        'name': m['name'],
        'type': m['type'],
        'package': m['pkg'],
        'engine': m['eng']} for m in mod]
