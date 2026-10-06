# DISTRIBUTION STATEMENT D. Distribution authorized to the Department of
# Defense and U.S. DoD contractors only; Administrative or Operational Use; 1
# Jan 2017. Other U.S. requests shall be referred to Naval Surface Warfare
# Center Panama City Division, ATTN: Technical Director NSWC PCD, 110 Vernon
# Ave, Panama City, FL 32407.
import os
import os.path as osp
import shutil
import mats
import mats.log
import mats.cfg
import mats.filesystem
import mats.security
import mats.uuid

MATSCX_ID = [0x806A9FA2, 0xE1084F3E, 0x9F4EBAC2, 0x08E47226]
MATSCX_FRAG = [0x806A9FA2, 0xE1084F3E, 0x9F4EBAC2, 0x08E47227]
MATSCX_TYPE = {
    'CFG': {'ID': 0x00000000, 'EXT': '.cfg'},
    'ATRCFG': {'ID': 0x00000001, 'EXT': '.atrcfg'},
    'DEP': {'ID': 0x00000002, 'EXT': None},
    'ARC': {'ID': 0x00000003, 'EXT': '.h5'}
}
MATSCX_TYPE_CFG = 0x00000000
MATSCX_TYPE_ATRCFG = 0x00000001
MATSCX_TYPE_DEP = 0x00000002
MATSCX_TYPE_ARC = 0x00000003
MATSCX_MAX_FILE_SIZE = 1000000000


class Node:
    def __init__(self, dtype, name):
        self.export_dir = osp.join(mats.filesystem.mats_working_dir(), 'export')
        self.file = None
        self.size = 0

        if dtype not in MATSCX_TYPE:
            raise ValueError('Unrecognized export type.')
        self.type = dtype

        if dtype == 'ATRCFG':
            # The AtrConfig name can differ from the configuration name if it
            # is inheriting from a parent configuration. Here we correct the
            # name if that is the situation.
            cfgmngr = mats.cfg.Cfg()
            filename = cfgmngr.atrconfig_name(name)
            name = osp.split(filename)[1]

        # File extension enforcement for the export
        if MATSCX_TYPE[dtype]['EXT']:
            ext = osp.splitext(name)[1]
            if not ext:
                name += MATSCX_TYPE[dtype]['EXT']
            elif ext != MATSCX_TYPE[dtype]['EXT']:
                raise ValueError('Node type is inconsistent with name.')
        self.name = name

        # Check to make sure we have the file.
        if not osp.exists(self.install_name):
            raise FileNotFoundError(f"Missing file '{self.install_name}'")
        self.size = osp.getsize(self.install_name)

        # Let make a copy in the export directory to make sure the file does
        # not change from outside influences and it gives us a copy that can be
        # modified for export.
        self.remove_export()
        shutil.copy2(self.install_name, self.export_name)

        return

    @property
    def install_name(self):
        if self.name is None:
            return None
        if self.type in ['CFG', 'ATRCFG', 'DEP']:
            return osp.join(mats.filesystem.mats_config_dir(), self.name)
        elif self.type == 'ARC':
            return osp.join(mats.filesystem.mats_working_dir(), 'archive',
                            self.name)
        mats.log.warn(f'Unrecognized node type "{self.type}"')
        return None

    @install_name.setter
    def install_name(self, value):
        raise ValueError('Setting install name is not permitted.')

    @property
    def export_name(self):
        return osp.join(self.export_dir, self.name)

    @export_name.setter
    def export_name(self, value):
        raise ValueError('Setting export name is not permitted.')

    def remove_export(self):
        if osp.exists(self.export_name):
            mats.log.warn(f'Deleting existing export "{self.export_name}"')
            os.remove(self.export_name)
        return

    def rename_export(self, name):
        # TODO: Implement
        pass

    def export(self, fh):
        """
            Write MATS export node to a file.

            Parameters
            ----------
            fh : file-like
                File object to use for writing.

            Returns
            -------
            bool
                Returns True on success.
            """
        buffer_size = 160
        if not osp.exists(self.export_name):
            mats.log.error(f"Missing file '{self.name}'")
            return False

        try:
            nfh = open(self.export_name, 'rb')
        except (OSError, FileNotFoundError):
            mats.log.error(f"Unable to open file ({self.name}).")
            return False

        # Write file type, name, and size
        fh.write(MATSCX_TYPE[self.type]['ID'].to_bytes(4, byteorder='little',
                                                       signed=False))
        name_len = len(self.name)
        fh.write(name_len.to_bytes(4, byteorder='little', signed=False))
        fh.write(self.name.encode('utf-8'))
        fh.write(self.size.to_bytes(4, byteorder='little', signed=False))

        # Start write file to stream and computing checksum
        chksum = mats.security.sha1_hash(self.export_name)
        while True:
            buffer = nfh.read(buffer_size)
            if not buffer:
                break
            fh.write(buffer)
        nfh.close()

        chksum = int(chksum, 16).to_bytes(20, byteorder='little', signed=False)
        fh.write(chksum[::-1])
        return True


def _gen_node(dtype, name):
    node = {
        'type': dtype,
        'name': name,
        'file': '',
        'size': 0
    }

    filename = name
    if dtype == MATSCX_TYPE_CFG:
        node['name'] = name+".cfg"
        filename = osp.join(mats.filesystem.mats_config_dir(), node['name'])
    elif dtype == MATSCX_TYPE_ATRCFG:
        pass
        # TODO(Bradley): I don't think we have a cfg manager yet.
        # MATS_cfg cfgmngr;
        # std::string atrcfgPath;
        # filename = cfgmngr.atrconfigName(name.c_str());
        # file_parts(filename.c_str(), atrcfgPath, node.name);
    elif dtype == MATSCX_TYPE_DEP:
        filename = osp.join(mats.filesystem.mats_config_dir(), name)
    elif dtype == MATSCX_TYPE_ARC:
        node['name'] = name + '.h5'
        filename = osp.join(mats.filesystem.mats_working_dir(), 'archive',
                            node['name'])

    if not osp.exists(filename):
        mats.log.error("Missing file '{}'".format(filename))
        return None
    node['file'] = filename
    node['size'] = osp.getsize(filename)

    return node


class ComponentExport:
    """
    A container for information to be exported.
    """
    def __init__(self):
        self.compression = False
        self.tmpdir = osp.join(mats.filesystem.mats_working_dir(), 'export')
        self._mcxPath = ''
        self._mcxBasename = ''
        self._exportPath = ''
        self._id = ''
        self._atrcfgName = ''
        self._component = []
        
        if not osp.isdir(self.tmpdir):
            try:
                os.mkdir(self.tmpdir)
            except OSError:
                mats.log.error(
                    f'Failure creating export directory ({self.tmpdir})')
                self.tmpdir = None

    def add_config(self, cfg_uuid, arc_export=None):
        src_uuid = cfg_uuid
        
        config = mats.cfg.read_config(src_uuid)
        if config is None or not mats.cfg.check_config(config):
            mats.log.error(f'Failure loading configuration {src_uuid}')
            return False

        try:
            node = Node('CFG', src_uuid)
        except (ValueError, FileNotFoundError):
            mats.log.error(
                f"Failed FileNode generation for CFG '{src_uuid}'")
            return False

        # For exported configurations we set the source to
        # 00000000-0000-0000-0000-000000000000, because we do not export
        # source configurations. The atrconfig file must be renamed to match.
        if not config['sourceUUID'] == "00000000-0000-0000-0000-000000000000":
            config['sourceUUID'] = "00000000-0000-0000-0000-000000000000"
            cfg_copy = osp.join(self._exportPath, node.name)
            mats.cfg.write_config(config, cfg_copy, force=True)
            node.file = cfg_copy
        self._component.append(node)

        # Add ATRCFG
        try:
            node = Node('ATRCFG', src_uuid)
            self._component.append(node)
        except (ValueError, FileNotFoundError):
            mats.log.error(
                f"Failed FileNode generation for ATRCFG '{src_uuid}'")
            return False
        if node.name != src_uuid+'.atrcfg':
            node.rename_export(src_uuid+'.atrcfg')

        # Add dependencies
        for dep in config['dependency']:
            try:
                node = Node('DEP', dep)
                self._component.append(node)
            except (ValueError, FileNotFoundError):
                mats.log.warn(
                    f"Failed FileNode generation for Dependency '{dep}'")

        # TODO(Bradley): Enable export of archive files
        # if arc_export:
        #     cfgmngr = mats.cfg.Cfg()
        #     atrcfg = mats.Archive()
        #     atrcfg_name = cfgmngr.atrconfig_name(cfg_uuid)
        #
        #     atrcfg.load(atrcfg_name)
        #     arc_list = archive_list(atrcfg)
        #     for arc in arc_list:
        #         try:
        #             node = Node('ARC', arc)
        #             self._component.append(node)
        #         except (ValueError, FileNotFoundError):
        #             mats.log.warn(
        #                 f"Failed FileNode generation for Archive '{arc}'.")
        return True

    def generate(self, filename: str, progress_bar: bool = None):
        fid = mats.uuid.uuid_generator()
        num_frags = 0
        exports = []

        if filename is None:
            raise ValueError('Missing or empty filename.')
        fh = open(filename, "wb")

        mcx_path, mcx_basename = osp.split(filename)
        mcx_basename = osp.splitext(mcx_basename)[0]
        frag_basename = osp.join(mcx_path, mcx_basename)
        exports.append(filename)

        # First we write matscxId
        cxid = b''.join(
            [x.to_bytes(4, byteorder='little', signed=False)
             for x in MATSCX_ID])
        fh.write(cxid)

        # Write export id to help identify fragments
        fh.write(fid.encode('utf-8'))

        # Total number of components
        num_comp = len(self._component)
        fh.write(num_comp.to_bytes(8, byteorder='little', signed=False))

        # Number of fragments (update later)
        frag_pos = fh.tell()
        fh.write(num_frags.to_bytes(4, byteorder='little', signed=False))

        # Start exporting components
        # if (progressBar) progress(0, numComp-1);
        for comp in self._component:
            curr_pos = fh.tell()
            if curr_pos + comp.size > MATSCX_MAX_FILE_SIZE:
                # Create new fragment
                fh.close()
                num_frags += 1
                frag_name = f'{frag_basename}-{num_frags}.matscx'

                fh = open(frag_name, "wb")
                cxid = b''.join(
                    [x.to_bytes(4, byteorder='little', signed=False)
                     for x in MATSCX_FRAG])
                fh.write(cxid)
                fh.write(fid.encode('utf-8'))
                exports.append(frag_name)
            mats.log.info(f"EXPORTING: {comp.name}[{comp.size}]")
            if not comp.export(fh):
                mats.log.error(f"Failed export of '{comp.file}'")
            # if (progressBar) progress(k, numComp-1);
        fh.close()

        # Update the number for fragments
        if num_frags > 0:
            try:
                fh = open(filename, "r+b")
                fh.seek(frag_pos, 0)
                fh.write(
                    num_frags.to_bytes(4, byteorder='little', signed=False))
                fh.close()
            except (FileNotFoundError, OSError):
                mats.log.error(
                    f"Failed to update number of fragments for {filename}.")
        return
    
    def file_import(filename, force, progressBar = False):
        pass

    def _update_path(fullname):
        pass
    
    def _node_install_path(node):
        pass

    def _extract_file(fid, node):
        pass

    def _open_frag(fragNum, mode):
        pass


def matscx_check_id(id, ver=0):
    pass


def matscx_check_compressed(filename):
    pass
