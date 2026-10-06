import json
import math
import os.path as osp
import base64
import re

import tqdm
import yaml
from cv2 import cvtColor, imwrite, COLOR_YUV2BGR_UYVY
import numpy as np
from tqdm import trange

from glob import glob


def _parse_frame(obj):
    obj = json.loads(obj)
    trim_data = False

    if 'raw_image' not in obj:
        print('!! Missing raw_image.')
        obj['raw_image'] = None
        return obj

    nr = obj['image_rows']
    nc = obj['image_cols']
    img = base64.b64decode(obj['raw_image'])
    img = np.frombuffer(img, np.uint8)

    if 'depth' in obj:
        depth = obj['depth']
    else:
        print(f'Missing depth field.')
        depth = int(img.shape[0] / (nr*nc))
        print(f'  - Estimated depth is {depth}')

    if 'conversion_flag' in obj:
        cs = obj['conversion_flag']
    else:
        print('Missing conversion_flag.')
        if depth == 2:
            print('  - Guessing YUV format.')
            cs = 108
        elif depth == 3:
            print('  - Guessing YUV 3 data has extra frame.')
            cs = 108
            trim_data = True
        else:
            raise ValueError(f'Unknown raw_image format with {depth} channels.')

    if trim_data:
        img = img[0:nr*nc*2]
        depth = 2
    img = img.reshape(nr, nc, depth)

    if cs == 108:
        img = cvtColor(img, COLOR_YUV2BGR_UYVY)
    elif cs is not None:
        raise ValueError(f'Unhandled "conversion_flag" value ({cs})')
    obj['raw_image'] = img

    return obj


def find_frames(fh):
    fh.seek(0, 2)
    fsize = fh.tell()
    fh.seek(0, 0)

    brace_counter = 0
    frame_start = -1
    frames = []
    for k in trange(fsize):
        c = fh.read(1)
        if c == '{':
            if brace_counter == 0:
                frame_start = fh.tell()
            brace_counter += 1
        if c == '}':
            brace_counter -= 1

        if brace_counter > 0:
            continue

        # We should have a full frame here
        sz = fh.tell() - frame_start
        if sz < 5:
            # Drop frame
            continue
        frames.append((frame_start, sz))
    return frames


def index_file(fn):
    with open(fn, 'r') as fh:
        raw = fh.read()

    brace_counter = 0
    ix0 = 0
    frames = []
    for k in enumerate(raw):
        if k[1] == '{':
            brace_counter += 1
        if k[1] == '}':
            brace_counter -= 1

        if brace_counter > 0:
            continue

        frames.append((ix0, k[0]))
        ix0 = k[0]+1
    return frames, raw


def extract_images(fn, out_dir):
    """
    Extract raw image frames from Nibbler JSON data stream.

    :param fn: Filename of Nibbler JSON file.
    :type fn: str
    :param out_dir: Path to output directory.
    :type out_dir: str
    :return: None
    """
    try:
        with open(fn, 'r') as fh:
            fh.seek(0, 2)
            fsize = fh.tell()
            fh.seek(0, 0)

            brace_counter = 0
            frame = ''
            for k in trange(fsize):
                c = fh.read(1)
                if c == '{':
                    brace_counter += 1
                if c == '}':
                    brace_counter -= 1

                frame += c
                if brace_counter > 0:
                    continue

                # We should have a full frame here
                if len(frame) < 5:
                    frame = ''
                    continue
                obj = _parse_frame(frame)

                img_fn = osp.join(out_dir, f'frame{obj["frame_id"]:04}.png')
                meta_fn = osp.join(out_dir, f'meta{obj["frame_id"]:04}.json')
                meta = obj['frame_misb_meta']

                imwrite(img_fn, obj['raw_image'])
                with open(meta_fn, 'w') as jh:
                    json.dump({
                        'frame_id': obj['frame_id'],
                        'frame_center': [meta['frame_center_latitude'],
                                         meta['frame_center_longitude']],
                        'frame_offset': {
                            'corner1': [meta['offset_corner_latitude_1'],
                                        meta['offset_corner_longitude_1']],
                            'corner2': [meta['offset_corner_latitude_2'],
                                        meta['offset_corner_longitude_2']],
                            'corner3': [meta['offset_corner_latitude_3'],
                                        meta['offset_corner_longitude_3']],
                            'corner4': [meta['offset_corner_latitude_4'],
                                        meta['offset_corner_longitude_4']]
                        },
                        'time_stamp': meta['time_stamp'],
                        'image_size': [obj['image_rows'], obj['image_cols']],
                    }, jh)
                frame = ''  # reset frame contents
    except:
        print(f'Failed processing {fn}')
    return


def extract_images2(fn, out_dir):
    """
    Extract raw image frames from Nibbler JSON data stream.

    :param fn: Filename of Nibbler JSON file.
    :type fn: str
    :param out_dir: Path to output directory.
    :type out_dir: str
    :return: None
    """
    jsf = JsonStreamFile(fn)

    lbl = f"Extracting frames for {osp.basename(fn)}"
    for f in tqdm.trange(jsf.nframes, desc=lbl):
        if jsf.frame_size(f) < 5:
            continue
        obj = jsf.frame(f)
        try:
            obj = _parse_frame(obj)
        except Exception as e:
            print(f'Failure parsing {fn} frame {f}')
            continue

        img_fn = osp.join(out_dir, f'frame{obj["frame_id"]:04}.png')
        meta_fn = osp.join(out_dir, f'meta{obj["frame_id"]:04}.json')
        meta = obj['frame_misb_meta']

        imwrite(img_fn, obj['raw_image'])

        try:
            with open(meta_fn, 'w') as jh:
                json.dump({
                    'frame_id': obj['frame_id'],
                    'frame_center': [meta['frame_center_latitude'],
                                     meta['frame_center_longitude']],
                    'frame_offset': {
                        'corner1': [meta['offset_corner_latitude_1'],
                                    meta['offset_corner_longitude_1']],
                        'corner2': [meta['offset_corner_latitude_2'],
                                    meta['offset_corner_longitude_2']],
                        'corner3': [meta['offset_corner_latitude_3'],
                                    meta['offset_corner_longitude_3']],
                        'corner4': [meta['offset_corner_latitude_4'],
                                    meta['offset_corner_longitude_4']]
                    },
                    'time_stamp': meta['time_stamp'],
                    'image_size': [obj['image_rows'], obj['image_cols']],
                }, jh)
        except:
            print(f'Failure writing meta for {fn} frame {f}')
    print(f"Finished {fn}")
    return


class JsonStreamFile:
    def __init__(self, fn):
        self.fn = fn
        self.idx = []
        self._fh = None
        self._fsize = None
        self._index_file()
        return

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return

    @property
    def size(self):
        if self._fsize is not None:
            return self._fsize
        if self._fh is None:
            self.open()
        self._fh.seek(0, 2)
        self._fsize = self._fh.tell()
        self._fh.seek(0, 0)
        return self._fsize

    @property
    def nframes(self):
        return len(self.idx)

    def _index_file(self, bit_size=None):
        if bit_size is None:
            bit_size = int(2e+9)  # 1GB
        idx_fn = osp.splitext(self.fn)[0]+'.idx'
        if osp.exists(idx_fn):
            with open(idx_fn, 'r') as fh:
                try:
                    idx_info = yaml.safe_load(fh)
                except:
                    print(f'!! Failure loading index file {idx_fn}')
                self.idx = idx_info['frames']
            return

        if self._fh is None:
            self.open()
        self._fh.seek(0, 0)

        ix0 = 0
        brace_counter = 0
        lbl = f'Indexing {osp.basename(self.fn)}'
        for pos in trange(math.ceil(self.size/bit_size), desc=lbl):
            buff = self._fh.read(bit_size)
            for m in re.finditer(r'}{', buff):
                idx = pos*bit_size + m.start()
                self.idx.append((ix0, idx))
                ix0 = idx + 1
            # for k in range(len(buff)):
            #     if buff[k] == '{':
            #         brace_counter += 1
            #     if buff[k] == '}':
            #         brace_counter -= 1
            #     if brace_counter > 0:
            #         continue
            #     idx = pos*bit_size + k
            #     self.idx.append((ix0, idx))
            #     ix0 = idx + 1

        with open(idx_fn, 'w') as fh:
            yaml.safe_dump({'frames': self.idx}, fh)
        return

    def open(self):
        if self._fh is not None:
            return
        self._fh = open(self.fn, 'r')
        return

    def close(self):
        if self._fh is None:
            return
        self._fh.close()
        return

    def frame_size(self, num):
        idx = self.idx[num]
        return idx[1]-idx[0]+1

    def frame(self, num):
        idx = self.idx[num]
        if self._fh is None:
            self.open()
        self._fh.seek(idx[0], 0)
        data = self._fh.read(idx[1]-idx[0]+1)
        return data
