# DISTRIBUTION STATEMENT D. Distribution authorized to the Department of
# Defense and U.S. DoD contractors only; Administrative or Operational Use; 1
# Jan 2017. Other U.S. requests shall be referred to Naval Surface Warfare
# Center Panama City Division, ATTN: Technical Director NSWC PCD, 110 Vernon
# Ave, Panama City, FL 32407.
import h5py
import numpy as np
from glob import glob
import os.path as osp
import cartopy
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

from mats.core import gt_read


typeNav = np.dtype([
    ('Yaw',np.float64), ('Pitch',np.float64), ('Roll',np.float64),
    ('Depth',np.float64), ('Altitude',np.float64), ('SoundSpeed',np.float64),
    ('Latitude',np.float64), ('Longitude',np.float64)
])


typeTime = np.dtype([
    ('Year',np.uint32), ('Month',np.uint32), ('Day',np.uint32),
    ('Hour',np.uint32), ('Minute',np.uint32), ('DecimalSec', np.float32),
    ('DaylightSavings',np.uint8), ('LocalOffset', np.float32)
])


typeChan = np.dtype([
    ('Range',np.float32), ('RangeDelay',np.float32), ('Frequency',np.float64),
    ('AlongTrackResolution',np.float64), ('AcrossTrackResolution',np.float64),
    ('SlantRange',np.float64), ('ChannelType',np.int32),
    ('MotionCorrected',np.uint8)
])


# Assumed file extension for MSHDF files
mshdf_ext = '.h5'


def get_time(fn):
    isOpened = True
    if isinstance(fn, h5py._hl.files.File):
        f = fn
        isOpened = False
    else:
        f = h5py.File(fn, 'r')

    t = np.array(f['Platform']['Time'], dtype=typeTime)

    if isOpened:
        f.close()

    return t


def get_nav(fn):
    isOpened = True
    if isinstance(fn, h5py._hl.files.File):
        f = fn
        isOpened = False
    else:
        f = h5py.File(fn, 'r')
    nav = np.array(f['Platform']['Navigation'], dtype=typeNav)

    if isOpened:
        f.close()

    return nav


def get_channel_info(fn):
    isOpened = True
    if isinstance(fn, h5py._hl.files.File):
        f = fn
        isOpened = False
    else:
        f = h5py.File(fn, 'r')
    
    chan = np.array(f['Sonar']['Sensor1']['Data1']['ChannelInfo'],
                    dtype=typeChan)
    
    if isOpened:
        f.close()
    return chan


def get_ping_data(fn, side=None):
    isOpened = True
    if isinstance(fn, h5py._hl.files.File):
        f = fn
        isOpened = False
    else:
        f = h5py.File(fn, 'r')
    
    if isinstance(side, str):
        if side == 'PORT':
            side = 1
        elif side == 'STBD':
            side = 2
        else:
            raise ValueError('Unknown side value')

    dset = f['Sonar']['Sensor1']['Data1']
    if side is None:
        data = dset['PingData']
    else:
        chan_msk = dset['ChannelInfo']['ChannelType'] == side
    
    return


def gen_dataset_map(fn):
    fileList = glob(osp.join(fn,'*'+mshdf_ext))
    # ll = []
    pad = 0.005
    mnLon = 180
    mxLon = -180
    mnLat = 90
    mxLat = -90
    
    ax = plt.axes(projection=ccrs.PlateCarree())
    for filename in fileList:
        nav = get_nav(filename)
        ax.plot(nav['Longitude'], nav['Latitude'], 'b')
        
        mnLon = min(mnLon, np.min(nav['Longitude']))
        mnLat = min(mnLat, np.min(nav['Latitude']))
        mxLon = max(mxLon, np.max(nav['Longitude']))
        mxLat = max(mxLat, np.max(nav['Latitude']))
        #ll.append({'lat': nav['Latitude'], 'lon': nav['Longitude']})

    ax.set_extent([mnLon-pad, mxLon+pad, mnLat-pad, mxLat+pad])
    ax.add_feature(cartopy.feature.OCEAN)
    ax.gridlines(draw_labels=True)


def show_data(fn):
    isOpened = True
    if isinstance(fn, h5py._hl.files.File):
        f = fn
        isOpened = False
    else:
        f = h5py.File(fn, 'r')
    
    pdata = np.array(f['Sonar']['Sensor1']['Data1']['PingData'])
    pdata /= np.mean(pdata)
    pdata = np.clip(pdata, 0, 16)
    
    plt.figure()
    plt.imshow(pdata, cmap='pink')
    
    if isOpened:
        f.close()
    
    return


def get_dataset_gt_snippets(mission_folder, gtfn=None, snip_size=None):
    if gtfn is None:
        # Use mission folder name for gtfn and assume it is in mission folder
        gtfn = osp.split(mission_folder)[1]
        gtfn = osp.join(mission_folder, gtfn+'.txt')[1]
    
    print(gtfn)
    if not osp.exists(gtfn):
        raise FileNotFoundError('Missing GT file ({})'.format(gtfn))
    gt_list = gt_read(gtfn)
    gt_list = sorted(gt_list, key = lambda i: i['fn'])
    
    fn = None
    for gt in gt_list:
        #if not fn == gt['fn']:
         #   
        print(gt)
    
    return