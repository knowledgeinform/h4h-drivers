from torch.utils.data import Dataset, Subset, Sampler, RandomSampler, DataLoader, BatchSampler, random_split
from typing import List
from glob import glob
import os.path as osp
import mats
import math
import numpy as np
from tqdm import tqdm
from scipy.interpolate import RegularGridInterpolator

def stack_snippets(ecd, bands):
    snip_list = []
    ref_snip = ecd.snippet(bands[0])
    ref_anum, ref_cnum = ref_snip.size()
    print(f'reference band {bands[0]} is {ref_anum}x{ref_cnum}')
    print(f'  ares = {ref_snip.ares}')
    print(f'  cres = {ref_snip.cres}')
    ref_r = ref_snip.ares * np.linspace(0, ref_anum - 1, ref_anum)
    ref_c = ref_snip.cres * np.linspace(0, ref_cnum - 1, ref_cnum)
    grid_r, grid_c = np.meshgrid(ref_r, ref_c, indexing='ij')

    for q, b in enumerate(bands):
        if q == 0:
            # This is the reference band that other bands will be resized to
            img_q = ecd.snippet(b).abs
        else:
            snip_q = ecd.snippet(b)
            anum_q, cnum_q = snip_q.size()
            print(f'band {q} {b} is {anum_q}x{cnum_q}')
            print(f'  ares = {snip_q.ares}')
            print(f'  cres = {snip_q.cres}')
            if anum_q == ref_anum and cnum_q == ref_cnum:
                # This band is the same size as the reference band
                img_q = snip_q.abs
            else:
                r_q = snip_q.ares * np.linspace(0, anum_q - 1, anum_q)
                c_q = snip_q.cres * np.linspace(0, cnum_q - 1, cnum_q)
                interp = RegularGridInterpolator((r_q, c_q), snip_q.abs)
                img_q = interp((grid_r, grid_c))
                print(f'new shape = {img_q.shape}')
        snip_list.append(img_q.astype(np.float32))
    img = np.stack(snip_list, axis=0)
    return img


class ArchiveDataset(Dataset):
    def __init__(self, archive_dir, bands=None, mode=None,
                 transform=None, target_transform=None):
        fns = glob(osp.join(archive_dir, '*.h5'))
        self.contacts = []
        if bands:
            self.bands = bands
        else:
            # Default to original behavior
            # (NOTE: Ideally we would always pass in the band strings, but it is
            #   unclear to me what code originally used this class, so I'm recording
            #   the original band strings here. -DK)
            self.bands = ['IMG-R', 'IMG-G', 'IMG-B']
        if mode in ['contact', 'snippet', 'features', 'uuid']:
            self.mode = mode
        else:
            self.mode = 'snippet'
        self.arc = mats.Archive()
        self.transform = transform
        self.target_transform = target_transform

        print('Scanning Archives...')
        for fn in tqdm(fns):
            self.arc.load(fn)
            cons = self.arc.contact()
            for con in cons:
                self.contacts.append({
                    'fn': fn,
                    'uuid': con.uuid,
                    'type': con.type
                })
        print('Dataset loaded')
        return

    def __getitem__(self, item):
        # print(f'{item} ({type(item)})')
        if type(item) is tuple:
            index = self.find_uuid(item[0])
        else:
            index = item
        self.arc.load(self.contacts[index]['fn'])
        ecd = self.arc.ecdata(self.contacts[index]['uuid'])
        if self.mode == 'snippet':
            out = stack_snippets(ecd, self.bands)
        elif self.mode == 'uuid':
            out = self.contacts[index]['uuid']
        else:
            cons = self.arc.contact()
            for con in cons:
                if con.uuid == self.contacts[index]['uuid']:
                    if self.mode == 'features':
                        out = con.features
                    else:
                        out = (con, ecd)
                    break
            else:
                out = None
        lbl = int(np.maximum(self.contacts[index]['type'], 0)) ###
        if self.transform:
            out = self.transform(out)
        if self.target_transform:
            lbl = self.target_transform(lbl)
        return out, lbl

    def __len__(self):
        return len(self.contacts)

    def find_label(self, label):
        inds = []
        for q, c in enumerate(self.contacts):
            if c['type'] == label:
                inds.append(q)
        return inds

    def find_targets(self, subset_inds=None):
        if subset_inds:
            index_list = subset_inds
        else:
            index_list = [x for x in range(len(self.contacts))]
        inds = []
        for q in range(len(index_list)):
            if self.contacts[index_list[q]]['type'] > 0:
                inds.append(q)
        return inds

    def find_uuid(self, uuid):
        for q, c in enumerate(self.contacts):
            if c['uuid'] == uuid:
                return q
        return []


# A variant of BatchSampler that distributes targets across all batches
#   as evenly as possible
class TargetBalancedBatchSampler(Sampler[List[int]]):
    def __init__(self, data, batch_size, drop_last=None):
        num_batches = len(data) // batch_size
        if type(drop_last) is bool and not drop_last:
            if len(data) != num_batches * batch_size:
                # Add an extra partial batch for the remaining items
                self._partial_batch_size = len(data) - num_batches * batch_size
                num_batches += 1
        else:
            self._partial_batch_size = None
        self.batches = [[] for _ in range(num_batches)]
        self.batch_size = batch_size
        self._create_batches(data)

    def __iter__(self):
        yield from self.batches

    def __len__(self):
        return len(self.batches)

    def _create_batches(self, data):
        samp = iter(RandomSampler(data))
        # Determine which items contain targets
        if isinstance(data, Subset):
            target_inds = data.dataset.find_targets(data.indices)
        else:
            target_inds = data.find_targets()
        # Distribute the target images as evenly as possible among the batches
        cnt = 0
        for n in range(self.batch_size):
            for b in range(len(self.batches)):
                if self._partial_batch_size:
                    if b == len(self.batches) - 1 and len(self.batches[b]) >= self._partial_batch_size:
                        # Final batch of leftovers is full
                        continue
                if cnt < len(target_inds):
                    # Add a target
                    self.batches[b].append(target_inds[cnt])
                else:
                    # Add a non-target
                    index = next(samp)
                    # Ensure that it's not a target
                    while index in target_inds:
                        # print(f'skipping {index}')
                        index = next(samp)
                    self.batches[b].append(index)
                cnt += 1


class DataLoaderCreator:
    def __init__(self, data_dir):
        self.data_dir = data_dir

    def create(self, batch_size, bands=None, mode=None,
               balance_targets=None, use_all=None,
               data_split=None):
        data_opts = {'bands': bands, 'mode': mode}
        samp_opts = {'batch_size': batch_size,
                     'drop_last': not use_all}
        data = ArchiveDataset(self.data_dir, **data_opts)

        if data_split and check_split_weights(data_split):
            split_weights = [data_split['train'], data_split['test']]
            train_set, test_set = random_split(data, split_weights)
            train_loader = create_loader(train_set, balance_targets, samp_opts)
            test_loader = create_loader(test_set, balance_targets, samp_opts)
            return train_loader, test_loader
        else:
            return create_loader(data, balance_targets, samp_opts)


def create_loader(data, balance_targets, samp_opts):
    if type(balance_targets) is bool and balance_targets:
        sampler = TargetBalancedBatchSampler(data, **samp_opts)
    else:
        sampler = BatchSampler(RandomSampler(data), **samp_opts)

    loader = DataLoader(data, batch_sampler=sampler)
    return loader


def check_split_weights(split_opts):
    subsets = ['train', 'test']
    for x in subsets:
        if x not in split_opts:
            return False
        if not (0 < split_opts[x] < 1):
            return False
    if sum([split_opts[x] for x in subsets]) - 1 > 1e-6:
        return False
    return True
