import mats
import mats.log
import os.path as osp
import numpy as np
from glob import glob
from PIL import Image


class rdrPIL(mats.Reader):
    def __init__(self):
        self.filetype = 'jpg'

    def isValid(self, fn):
        status = True

        if not osp.exists(fn):
            return False

        try:
            img = Image.open(fn, 'r')
            img.close()
        except:
            return False

        return status

    def read(self, file_path):
        inp = []

        # Check if file is a valid MSHDF file
        if not self.isValid(file_path):
            mats.log.error("JPEG file does not exist or is invalid.")
            raise FileExistsError('JPEG file does not exist or is invalid.')

        try:
            img = Image.open(file_path, 'r')
        except:
            mats.log.error('Failed to open JPEG file.')
            raise FileExistsError('Failed to open JPEG file.')

        if img.mode != 'RGB' and img.mode != 'RGBA':
            mats.log.warn(
                f'Converting image ({file_path}) to RGB (from {img.mode})')
            img = img.convert('RGB')
        img_data = np.array(img)
        img.close()

        inp.append(mats.Input())
        inp[0]['filename'] = osp.basename(file_path)
        inp[0]['sensor'] = "Image-RGB"
        inp[0].add_data("IMG-R")
        inp[0].add_data("IMG-G")
        inp[0].add_data("IMG-B")

        inp[0].data('IMG-R')['data'] = img_data[:, :, 0].astype('float32')/255
        inp[0].data('IMG-R')['ares'] = 1
        inp[0].data('IMG-R')['cres'] = 1
        inp[0].data('IMG-G')['data'] = img_data[:, :, 1].astype('float32')/255
        inp[0].data('IMG-G')['ares'] = 1
        inp[0].data('IMG-G')['cres'] = 1
        inp[0].data('IMG-B')['data'] = img_data[:, :, 2].astype('float32')/255
        inp[0].data('IMG-B')['ares'] = 1
        inp[0].data('IMG-B')['cres'] = 1

        return inp

    def scan(self, folder):
        files = []
        tmp = glob(osp.join(folder, '**', '*.'+self.filetype), recursive=True)
        for fn in tmp:
            if osp.isdir(fn):
                mats.log.warn(f'Directory with file extension ({fn}).')
                continue

            ext = osp.splitext(fn)[1][1:]
            if not ext == self.filetype:
                continue
            files.append(fn)
        return files

    def configure(self, cfg):
        return True
