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
import math
import os
import os.path as osp
import numpy as np
import h5py
import re

import mats
import mats.filesystem
import mats.h5
import mats.log
import mats.security
import mats.uuid
import mats.time
import mats.basic
import mats.cfg


def remove_gt(arc):
    if type(arc) == str:
        fn = arc
    else:
        fn = arc.path()

    try:
        fh = h5py.File(fn, 'a')
    except (FileNotFoundError, OSError):
        mats.log.error(
            f"Unable to open archive file ({fn}).")
    if 'gt' in fh:
        del fh['gt']
    fh.close()
    return


if mats.cpp_backend:
    class Archive(mats.mc.MATS_archive):
        def __init__(self):
            super().__init__()
            
        def add_groundtruth(self, gt):
            archive_name = self.path()
            
            try:
                fh = h5py.File(archive_name, 'r+')
            except (FileNotFoundError, OSError):
                msg = "Unable to open archive file ({}) to add GT.".format(archive_name)
                mats.log.error(msg)
            img_name = mats.h5.get_string(fh, "filename")
            
            # only look at gts with same filename
            gt_filt = [x for x in gt if x['fn'] == img_name]
            
            if len(gt_filt) == 0:
                return
            
            arc_type = np.array([x['type'] for x in gt_filt])
            arc_x = np.array([x['x'] for x in gt_filt])
            arc_y = np.array([x['y'] for x in gt_filt])
            arc_num = np.array([x['num'] for x in gt_filt])
        
            mats.h5.create_array(fh, "gt/type", arc_type)
            mats.h5.create_array(fh, "gt/x", arc_x)
            mats.h5.create_array(fh, "gt/y", arc_y)
            mats.h5.create_array(fh, "gt/num", arc_num)
        
            if 'MLO' in gt_filt[0]:
                arc_mlo = np.array([x['MLO'] for x in gt_filt])
                mats.h5.create_array(fh, "gt/mlo", arc_mlo)
                
            fh.close()
            
        def add_mlo(self, gt):
            archive_name = self.path()
            try:
                fh = h5py.File(archive_name, 'r+')
            except (FileNotFoundError, OSError):
                msg = "Unable to open archive file ({}) to add MLO.".format(archive_name)
                mats.log.error(msg)
            img_name = mats.h5.get_string(fh, "filename")
            
            # don't do anything if archive gt field is empty
            arc_gt = mats.h5.get_groundtruth(fh, "gt")
            if len(arc_gt) < 1:
                return
            
            # only look at gts with same filename
            gt_filt = [x for x in gt if x['fn'] == img_name]
            
            mlo = []
            for g in arc_gt:
                x = g['x']
                y = g['y']
                gt_match = [z for z in gt_filt if z['x']==x and z['y']==y]
                if len(gt_match) != 1:
                    msg = 'More than one entry for same location'
                    mats.log.error(msg)
                    raise ValueError(msg)
                else:
                    gt_match = gt_match[0]
                mlo.append(gt_match['MLO'])
            
            mlo = np.array(mlo)
            
            mats.h5.create_array(fh, "gt/mlo", mlo)
                
            fh.close()
else:
    class Archive:
        """
        Archive is an interface for %MATS Archive files, which contain raw ATR
        output from the processing of a file. Archive files do not contain any
        file sensor data, but contain navigation, time, size, and resolution
        information. They also contain ATR contact information (before
        threshold).
        """

        def __init__(self):
            self._filename = None
            self._side = None
            self._config = None
            self._hash = None
            self._version = None

            self._location = mats.filesystem.mats_working_dir()
            self._location = osp.join(self._location, "archive")

        def clear(self):
            self._filename = None
            self._side = None
            self._config = None
            self._hash = None
            self._version = None

        def load(self, filename):
            """
            Loads a MATS Archive file.

            Parameters
            ----------
            filename : str
                Filename or ID of Archive file to load.

            Returns
            -------
            bool
                Returns True on success.
            """
            # Clear the MATS_archive object.
            self.clear()

            if osp.exists(filename):
                fn = filename
            else:
                # Check if filename is an id
                fn = osp.join(self._location, filename + '.h5')

                if not osp.exists(fn):
                    msg = "Missing archive file ({}).".format(fn)
                    raise FileNotFoundError(msg)

            self._filename = fn
            try:
                fh = h5py.File(self._filename, 'r')
            except (FileNotFoundError, OSError):
                msg = f'Failure opening archive ({self._filename}).'
                mats.log.error(msg)
                self._filename = None
                raise OSError(msg)

            self._side = mats.h5.get_string(fh, 'side')
            self._config = mats.h5.get_string(fh, 'config')
            self._hash = mats.h5.get_string(fh, 'hash')
            self._version = mats.h5.get_string(fh, 'version')
            fh.close()
            return True

        def location(self, loc):
            """
            Sets default search location for archives, which is used by load to
            allow loading by id instead of file path.

            Parameters
            ----------
            loc : str
                Desired location for searching for archives.
            """
            if not osp.exists(loc):
                msg = 'Location does not exist ({}).'.format(loc)
                raise FileNotFoundError(msg)
            self._location = loc
            return

        @property
        def path(self):
            """
            Full file path to archive.
            """
            return self._filename

        @path.setter
        def path(self, fn):
            raise AttributeError('Setting file path not allowed.')

        @property
        def side(self):
            """
            Side for archive.
            """
            return self._side

        @side.setter
        def side(self, s):
            raise AttributeError('Setting side not allowed.')

        @property
        def input_hash(self):
            """
            Input data file checksum for archive.
            """
            return self._hash

        @input_hash.setter
        def input_hash(self, s):
            raise AttributeError('Setting input hash not allowed.')

        @property
        def config(self):
            """
            Configuration UUID of archive.
            """
            return self._config

        @config.setter
        def config(self, s):
            raise AttributeError('Setting configuration ID not allowed.')

        @property
        def version(self):
            """
            Version of archive (MATS version when archive was created).
            """
            return self._version

        @version.setter
        def version(self, v):
            raise AttributeError('Setting version not allowed.')

        def __gt_filter(self, filename, gt):
            file_fn = mats.filesystem.file_basename(filename)
            gt_good = []
            for g in gt:
                gt_fn = mats.filesystem.file_basename(g['fn'])
                if file_fn == gt_fn and self.side == g['side']:
                    gt_good.append(g)
            return gt_good

        def contact(self):
            """
            Contacts contained in archive.
            """
            if self._filename is None:
                raise FileNotFoundError('Archive file not loaded.')

            try:
                fh = h5py.File(self._filename, 'r')
            except (FileNotFoundError, OSError):
                msg = "Unable to open archive file ({}).".format(self._filename)
                mats.log.error(msg)
                return mats.ContactList()

            if 'contacts' in fh:
                con = mats.h5.get_mats_contact_list(fh, "contacts")
            else:
                # Contact-related data may not exist in the file if the original
                #   contact list being saved was empty
                con = mats.ContactList()
            fh.close()

            return con

        def ecdata(self):
            """
            Extra contact data contained in archive.
            """
            if self._filename is None:
                raise FileNotFoundError('Archive file not loaded.')

            try:
                fh = h5py.File(self._filename, 'r')
            except (FileNotFoundError, OSError):
                msg = "Unable to open archive file ({}).".format(self._filename)
                mats.log.error(msg)
                return mats.EcdataList()

            if 'ecdata' in fh:
                ecd = mats.h5.get_mats_ecdata_list(fh, "ecdata")
            else:
                # Ecdata-related data may not exist in the file if the original
                #   ecdata list being saved was empty
                ecd = mats.EcdataList()
            fh.close()
            return ecd

        def groundtruth(self):
            """
            Groundtruth data contained in archive.
            """
            if self._filename is None:
                raise FileNotFoundError('Archive file not loaded.')

            try:
                fh = h5py.File(self._filename, 'r')
            except (FileNotFoundError, OSError):
                msg = "Unable to open archive file ({}).".format(self._filename)
                mats.log.error(msg)
                return []

            fn = mats.h5.get_string(fh, "filename")
            gt = mats.h5.get_groundtruth(fh, "gt")
            
            fh.close()

            # Put the filename and side information into the groundtruth vector.
            for g in gt:
                g['fn'] = fn
                g['side'] = self._side
            return gt

        def add_contacts(self, con):
            """
            Adds contacts to archive. Contacts can only be added once.

            Parameters
            ----------
            con : mats.ContactList
                List of contacts to be added to archive.
            """
            if self._filename is None:
                raise FileNotFoundError('Archive file not loaded.')

            try:
                fh = h5py.File(self._filename, 'r+')
            except (FileNotFoundError, OSError):
                msg = "Unable to open archive file ({}).".format(self._filename)
                mats.log.error(msg)
                raise RuntimeError(msg)

            if mats.h5.create_mats_contact_list(fh, "contacts", con) == 1:
                raise RuntimeError("Failed to update contact list.")
            fh.close()
            return

        def update_contacts(self, con):
            """
            Updates contact information contained in an archive. This function
            will not create new contacts in an archive. The updated contacts
            must have matching UUIDs to the existing contacts.

            Notes
            -----
            See mats.h5.update_mats_contact() for which fields can be updated.

            Parameters
            ----------
            con : mats.ContactList
                List of contacts with updated information that needs to be saved
                to the archive.

            Returns
            -------
            bool
                Returns True on success.
            """
            if self._filename is None:
                raise FileNotFoundError('Archive file not loaded.')

            try:
                fh = h5py.File(self._filename, 'r+')
            except (FileNotFoundError, OSError):
                msg = "Unable to open archive file ({}).".format(self._filename)
                mats.log.error(msg)
                raise RuntimeError(msg)

            if not mats.h5.update_mats_contact_list(fh, "contacts", con):
                raise RuntimeError("Failed to update contact list.")
            fh.close()
            return

        def add_ecdata(self, ecd):
            """
            Adds extra contact data to archive. Extra contact data can only be
            added once.

            Parameters
            ----------
            ecd : mats.EcdataList
                List of extra contact data to be added to archive.
            """
            if self._filename is None:
                raise FileNotFoundError('Archive file not loaded.')

            try:
                fh = h5py.File(self._filename, 'r+')
            except (FileNotFoundError, OSError):
                msg = "Unable to open archive file ({}).".format(self._filename)
                mats.log.error(msg)
                raise RuntimeError(msg)

            if mats.h5.create_mats_ecdata_list(fh, "ecdata", ecd) == 1:
                raise RuntimeError("Failed to create ecdata list.")
            fh.close()
            return

        def update_ecdata(self, ecd):
            """
            Updates ecdata information contained in an archive. This function
            will not create new ecdata in an archive.

            Notes
            -----
            Currently no ecdata fields are updatable.

            Parameters
            ----------
            ecd : mats.EcdataList
                List of ecdata with updated information that needs to be saved
                to the archive.

            Returns
            -------
            Returns True on success.
            """
            if self._filename is None:
                raise FileNotFoundError('Archive file not loaded.')

            try:
                fh = h5py.File(self._filename, 'r+')
            except (FileNotFoundError, OSError):
                msg = "Unable to open archive file ({}).".format(self._filename)
                mats.log.error(msg)
                raise RuntimeError(msg)

            # TODO: Look at implementing update_mats_ecdata_list.
            # if not mats.h5.update_mats_ecdata_list(fh, "contacts", ecd):
            #     raise RuntimeError("Failed to update ecdata list.")
            fh.close()
            return

        def add_groundtruth(self, gt):
            """
            Adds ground truth information to archive. Only ground truth for
            corresponding archive input data is added to archive.

            Parameters
            ----------
            gt : list
                Ground truth vector.
            """
            # TODO(Bradley): Add implementation.
            return

        def update_groundtruth(self, gt):
            """
            Updates groundtruth information contained in an archive.

            If existing groundtruth is empty, it is filled in with the given
            groundtruth. If only num and type changes in groundtruth are
            detected, then the information is updated. Otherwise, old
            groundtruth is moved to new group 'gt#', where # is the next
            available number starting with 0, and new groundtruth is added.

            Parameters
            ----------
            gt : list
                Groundtruth data with updates or groundtruth data to replace
                existing.

            Returns
            -------
            bool
                Returns True on success.
            """
            if self._filename is None:
                raise FileNotFoundError('Archive file not loaded.')

            try:
                fh = h5py.File(self._filename, 'r+')
            except (FileNotFoundError, OSError):
                msg = "Unable to open archive file ({}).".format(self._filename)
                mats.log.error(msg)
                raise RuntimeError(msg)

            if 'gt' not in fh:
                gh = fh.create_group('gt')
                gh.close()
            gt_existing = mats.h5.get_groundtruth(fh, "gt")

            # Use only GTs that match input filename and side.
            fn = mats.h5.get_string(fh, "filename")
            gt_good = self.__gt_filter(fn, gt)

            # If existing groundtruth group is empty, just write the groundtruth
            # there.
            if not gt_existing:
                return mats.h5.create_groundtruth(fh, "gt", gt_good)

            # If we get here then there apparently is groundtruth for the
            # archive. So, first we need to determine if the new groundtruth is
            # different from the old. If it's not different, we are done.
            if len(gt_existing) == len(gt_good):
                # Try to match x / y entries.
                gt_match = True
                for g in gt_existing:
                    m = [v for v in gt_good
                         if v['x'] == g['x'] and v['y'] == g['y']]
                    if m is None:
                        gt_match = False
                        break

                if gt_match:
                    # Groundtruth x / y match. Update to save any changes to num
                    # and type.
                    return mats.h5.update_groundtruth(fh, "gt", gt_good)

            # No match. Move existing GT to a new backup group.
            k = 0
            while True:
                gt_grp = f"gt{k}"
                if gt_grp not in fh:
                    break
                k += 1

            if not mats.h5.move_groundtruth(fh, "gt", gt_grp):
                mats.log.error('Failed backup gt group move.')
                return False

            # Save the updated GT in 'gt' group.
            return mats.h5.create_groundtruth(fh, "gt", gt_good)

        def add_timing(self, ts):
            """
            Adds or updates ATR processing time value in archive. Processing
            time is for a single input.

            Parameters
            ----------
            ts : float
                ATR processing time (seconds).
            """
            # TODO(Bradley): Add implementation.
            return

        def timing(self):
            """
            Get ATR processing time value from archive. Processing time is for a
            single input.

            Returns
            -------
            ts : float
                ATR processing time (seconds).
            """
            # TODO(Bradley): Add implementation.
            return

        def input(self):
            """
            Returns mats.Struct with archived input information. Archived
            input information does not contain any sensor data, but contains
            size and resolution information for sensor data.
            """
            if self._filename is None:
                raise FileNotFoundError('Archive file not loaded.')

            try:
                fh = h5py.File(self._filename, 'r')
            except (FileNotFoundError, OSError):
                msg = "Unable to open archive file ({}).".format(self._filename)
                mats.log.error(msg)
                return mats.ContactList()

            out = mats.Struct()
            out['filename'] = mats.h5.get_string(fh, 'filename')
            out['sensor'] = mats.h5.get_string(fh, 'sensor')
            out['side'] = mats.h5.get_string(fh, 'side')

            # Convert sweetspot back to 0-indexing.
            try:
                sweetspot = mats.h5.get_array(fh, "sweetspot")
                if sweetspot[0] > 0:
                    sweetspot[0] -= 1
                if sweetspot[1] > 0:
                    sweetspot[1] -= 1
            except:
                msg = "Failed read of sweetspot ({}).".format(self._filename)
                mats.log.error(msg)
                sweetspot = np.array([0, 0])
            out['sweetspot'] = sweetspot

            data_names = mats.h5.get_string_list(fh, 'sensor_data_names')
            if 'data' in fh:
                sensor_data = mats.Struct()
                for dname in data_names:
                    if dname not in fh['data']:
                        mats.log.warn('Missing sensor data.')
                        continue
                    sdata = fh['data'][dname]

                    data_info = mats.Struct()
                    data_info['anum'] = mats.h5.get_value(sdata, 'anum')
                    data_info['cnum'] = mats.h5.get_value(sdata, 'cnum')
                    data_info['ares'] = mats.h5.get_value(sdata, 'ares')
                    data_info['cres'] = mats.h5.get_value(sdata, 'cres')
                    sensor_data[dname] = data_info
                out["data"] = sensor_data

            out['lat'] = mats.h5.get_array(fh, "lat")
            out['lon'] = mats.h5.get_array(fh, "long")
            out['time'] = mats.h5.get_array(fh, "time")
            out['heading'] = mats.h5.get_array(fh, "heading")
            out['alt'] = mats.h5.get_array(fh, "alt")
            out['depth'] = mats.h5.get_array(fh, "depth")

            # Convert heading from radians to degrees.
            if out['heading'] is not None:
                out['heading'] *= 180.0 / np.pi

            fh.close()
            return out


if mats.cpp_backend:
    class Archiver(mats.mc.MATS_archiver):
        def __init__(self):
            super().__init__()
else:
    class Archiver:
        """
        An archive is a record of the ATR result for a particular input file and
        configuration. An archiver is a manager of that information. The
        archiver operates out of a designated file system location (by default
        this location is the archive folder located in the %MATS working
        directory). Archives are written to and loaded from this location by
        default. The archiver also creates a text file at this location for
        associating a file SHA1 hash with an archive.
        """

        def __init__(self):
            self._filename_format = 'uuid'
            self._location = None
            self._arcdb = None

            loc = mats.filesystem.mats_working_dir()
            loc = osp.join(loc, 'archive')
            self.location(loc)
            return

        def archive_path(self):
            return self._arcdb

        def options(self, opt):
            """
            Set advanced options for Archiver.

            Parameters
            ----------
            opt : mats.Struct
                Options structure containing option and value pairs.
            """
            if "filename_format" in opt:
                if not type(opt["filename_format"]) == str:
                    mats.log.warn("Invalid 'filename_format' value type.")
                if opt["filename_format"] in ['uuid', 'filename']:
                    self._filename_format = opt["filename_format"]
                else:
                    mats.log.warn("Unknown 'filename_format' value.")
            return

        def location(self, loc):
            """
            Sets the default location used by the archiver.

            Parameters
            ----------
            loc : str
                Filesystem directory for archives.
            """
            try:
                if not os.path.exists(loc):
                    os.mkdir(loc)
            except PermissionError:
                mats.log.error("Failure creating or accessing given location.")
                return
            self._location = loc
            self._arcdb = osp.join(loc, 'archive.txt')
            return

        def find(self, cfg, inp, file_hash=None, version=None):
            """
            Searches archives for an archive that corresponds to the given input
            and configuration (and, optionally, version).

            Parameters
            ----------
            cfg : dict or str
                ATR Configuration (dict) used to process data or the
                ATR configuration ID (str).
            inp : mats.Input
                Data processed.
            file_hash : str, optional
                SHA1 hash of input data file.
            version : str, optional
                MATS version for archive.

            Returns
            -------
            Name of the first matching archive, if it exists. Otherwise, returns
            None.
            """
            if type(cfg) == dict:
                if not mats.cfg.check_config(cfg):
                    raise ValueError('Invalid ATR Configuration.')
                cfg_id = cfg['Uuid']
            else:
                cfg_id = cfg  # Assuming 'cfg' is a string

            arc = Archive()
            arc.location(self._location)

            if file_hash is None:
                file_hash = mats.security.sha1_hash(inp['filename'])
                if len(file_hash) == 0:
                    msg = f"Unable to calculate file hash ({inp['filename']})."
                    mats.log.error(msg)
                    return None

            entries = self._db_find(file_hash)
            if not entries:
                return None  # No possible archives found

            for entry in entries:
                if not arc.load(entry):
                    mats.log.warn(f"Failed load of archive ({entry}).")
                    continue

                if arc.side == inp['side'] and arc.config == cfg_id:
                    if version and arc.version != version:  # Wrong version
                        continue
                    return entry
            return None

        def create(self, cfg, inp, overwrite=False):
            """
            Creates an archive for given configuration and input data.

            If an archive with the same input already exists, the groundtruth
            will be pulled from the existing archive and added to the new one.

            If an archive with the same input, config, and version already
            exists, it will be overwritten.

            If an archive with the same input and config, but older version,
            exists, the behavior depends on the @p overwrite flag. If true, a
            matching archive with older version will be overwritten with the new
            archive. If false, the older archive will be left in place, and the
            new archive will be added. This flag is optional and defaults to
            false.

            Parameters
            ----------
            cfg : mats.AtrConfig or str
                Configuration used to process data.
            inp : mats.Input
                Data processed.
            overwrite : bool, optional
                Flag to overwrite older matching archive.

            Returns
            -------
            str
                Returns the name of the new archive on success. Returns an empty
                string on failure.
            """
            if type(cfg) is str:
                cfg_uuid = cfg
            else:
                cfg_uuid = cfg['Uuid']
            # Compute file hash
            file_hash = mats.security.sha1_hash(inp['filename'])
            if len(file_hash) == 0:
                mats.log.error(f"Unable to calculate file hash "
                               "({inp['filename']})")

            # Only use file name, not including path, for writing to archive.
            path_to, filename = osp.split(inp['filename'])

            # Find existing groundtruth, if any.
            gt = self._gt_find(inp, file_hash)

            # Check if archive exists
            file_id = self.find(cfg, inp, file_hash, mats.get_mats_version())
            if file_id is None:
                # No exact match
                if overwrite:
                    # Overwrite existing archive, even if it's a different
                    # version
                    file_id = self.find(cfg, inp, file_hash)

            if file_id is None:
                if self._filename_format == 'uuid':
                    file_id = mats.uuid.uuid_generator()
            else:
                dt = mats.time.datenow()
                fn_base = mats.filesystem.file_basename(filename)
                dsec = round(dt['dsecond'])
                arc_fn = f"{fn_base}-{inp['side']}-{dt['year']}{dt['month']}" \
                         f"{dt['day']}-{dt['hour']}{dt['minute']}{dsec}"
                file_id = arc_fn

            # Create archive name
            arc_fn = osp.join(self._location, file_id + '.h5')

            # Create archive
            try:
                if os.path.exists(arc_fn):
                    fh = h5py.File(arc_fn, 'r+')
                else:
                    fh = h5py.File(arc_fn, 'w')
            except (FileNotFoundError, OSError):
                mats.log.error(f"Failure creating archive file ({arc_fn}).")
                return None

            # New sweetspot array for 1 - indexing.
            new_sweetspot = np.array(inp['sweetspot']) + 1

            # Input information
            mats.h5.create_string(fh, "filename", filename)
            mats.h5.create_string(fh, "sensor", inp['sensor'])
            mats.h5.create_string(fh, "side", inp['side'])
            mats.h5.create_array(fh, "sweetspot", new_sweetspot)

            data_names = inp['data_names']
            mats.h5.create_string_list(fh, "sensor_data_names", data_names)
            try:
                gh = fh.create_group('data')
                for dn in data_names:
                    sgh = gh.create_group(dn)
                    data = inp.data(dn)
                    mats.h5.create_value(sgh, "anum", data.anum)
                    mats.h5.create_value(sgh, "cnum", data.cnum)
                    mats.h5.create_value(sgh, "ares", data.ares)
                    mats.h5.create_value(sgh, "cres", data.cres)
            except ValueError:
                mats.log.warn('Failed to create Archive data group')

            # Create new heading array for heading in radians, within[0, 2*pi).
            heading = np.mod(inp['heading'], 360.0) * math.pi / 180.0
            mats.h5.create_array(fh, "lat", inp['lat'])
            mats.h5.create_array(fh, "lon", inp['lon'])
            mats.h5.create_array(fh, "heading", heading)
            mats.h5.create_array(fh, "time", inp['time'])
            mats.h5.create_array(fh, "alt", inp['height'])
            mats.h5.create_array(fh, "depth", inp['depth'])

            # Configuration information
            mats.h5.create_string(fh, "hash", file_hash)
            mats.h5.create_string(fh, "config", cfg_uuid)
            mats.h5.create_string(fh, "version", mats.get_mats_version())

            # Add existing groundtruth.
            if len(gt) > 0:
                mats.h5.create_gt_list(fh, "gt", gt)
            fh.close()

            # Add listing to database file
            self._db_add(file_id, file_hash)
            return file_id

        def import_archive(self, filename):
            """
            Imports an archive file (copies archive file to archiver location
            and adds input/archive association to archive list).
            """
            # TODO: Implement Archiver archive import.
            raise NotImplementedError('Not implemented yet')

        def archive_list(self):
            """
            Returns a list of archive IDs as recorded in the database file.

            Returns
            -------
            list
                List of archive names.
            """
            # TODO: Implement Archiver archive list retrieval.
            hex_template = lambda x: f'[0-9a-fA-F]{{{x}}}'
            hash_re = re.compile(hex_template(40))
            uuid_re = re.compile('-'.join([hex_template(x) for x in [8, 4, 4, 4, 12]]))
            archive_ids = []
            try:
                with open(self._arcdb, 'r') as f:
                    for line in f:
                        tokens = line.rstrip('\n').split(' ')
                        if len(tokens) < 2:
                            continue
                        if hash_re.fullmatch(tokens[0]) and uuid_re.fullmatch(tokens[1]):
                            archive_ids.append(tokens[1])
                return archive_ids
            except:
                return []

        def _db_add(self, file_id, file_hash):
            """
            Add an entry (hash and UUID) to the database file.  (Only adds the
            entry if it doesn't already exist.)

            Parameters
            ----------
            file_id : str
                UUID of the archive.
            file_hash : str
                SHA1 hash of the input data file.

            Returns
            -------
            bool
                True if added.
            """
            # Check if entry(hash + ID) already exists
            entries = self._db_find(file_hash)
            for entry in entries:
                if entry == file_id:
                    return False
            with open(self._arcdb, 'a') as fh:
                fh.write(f'{file_hash} {file_id}\n')
            return True

        def _db_find(self, in_hash):
            """
            Find all entries in the database file with the given hash.

            Parameters
            ----------
            in_hash : str
                SHA1 hash of the input data file.

            Returns
            -------
            list
                Returns a list of the entry UUIDs.
            """
            entries = []
            if not os.path.exists(self._arcdb):
                return []
            with open(self._arcdb) as fh:
                while True:
                    line = fh.readline(256)
                    if not line:
                        break
                    arc_hash, arc_id = line.split(maxsplit=2)
                    if arc_hash == in_hash:
                        entries.append(arc_id)
            return entries

        def _gt_find(self, inp, in_hash):
            """
            Given an input and its hash, try to find an existing groundtruth
            vector for the input using existing archive files.

            Parameters
            ----------
            inp : mats.Input
                MATS Input data.
            in_hash : str
                SHA1 hash of input data file.

            Returns
            -------
            list[dict]
                Returns a groundtruth vector (empty if none found).
            """
            arc = Archive()
            arc.location = self._location

            # Find any archive files that match this input hash and side.
            entries = self._db_find(in_hash)
            gt_files = []
            for entry in entries:
                try:
                    arc.load(entry)
                except (FileNotFoundError, OSError):
                    continue
                if arc.side == inp['side']:
                    gt_files.append(entry)

            if len(gt_files) == 0:
                return []

            # Sort the files by time modified.
            # times.resize(GTfiles.size());
            # for (k = 0; k < GTfiles.size(); k ++) {
            #     tempstr = location_;
            #     mats::file_path(tempstr, GTfiles[k]);
            #     tempstr += ".h5";
            #     times[k] = mats::file_mod_time(tempstr.c_str());
            # }
            # mats::sort_with_indices( & times, & indices);

            # Check each file(newest first) for non - empty groundtruth vector.
            # for (k = 0; k < GTfiles.size(); k++) {
            #     tempstr = GTfiles[indices[GTfiles.size() - 1 - k]]; // archive ID
            #     if (arc.load(tempstr.c_str()) > 0) {
            #         continue;
            #     }
            #     GT = arc.groundtruth();
            #     if (GT.size() > 0) {
            #         std::stringstream msg;
            #         msg << "Using groundtruth from archive '" << tempstr << "'.";
            #         mats_log(MATS_MSG, msg.str().c_str());
            #         break;
            #     }
            # }
            # return GT;
