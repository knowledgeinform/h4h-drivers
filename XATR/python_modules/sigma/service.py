#! /usr/bin/env python3

import mats
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
import time
import json

import sigma
import os.path as osp
from collections import deque


def image2input(img, name=None):
    """Read image data into a mats Input object

    Parameters
    ----------
        img: ndarray or str
            Image data either as a numpy array or a filename. Image files
            will be opened and converted into numpy arrays before being
            read into the mats Input object. Arrays should be in RGB order.

        name: str
            Image name, to be used as filename of the Input object. If None
            and img is a str then the value of img will be used. If img is
            a ndarray, the hexadecimal representation of the absolute value
            of the hashed array will be used.
    """
    if isinstance(img, np.ndarray):
        if name is None:
            name = '{:X}'.format(abs(hash(img.tostring())))
    elif isinstance(img, str):
        if name is None:
            name = img
        with Image.open(img) as im:
            img = np.array(im)
    else:
        raise TypeError("img type must be ndarray or str")

    channel_dict = {'IMG-R': 0, 'IMG-G': 1, 'IMG-B': 2}

    inp = mats.Input()
    inp.filename = name
    inp.sensor = 'Image-RGB'

    for channel, idx in channel_dict.items():
        inp.add_data(channel)
        pnt = inp.data(channel)
        pnt.precision = 'FLOAT'
        pnt.allocate_data(*img[:, :, idx].shape, False)
        pnt.load_data((img[:, :, idx] / 255).astype(np.float32))
        pnt.storage = 'ROW_MAJOR'

    return inp


def _get_frame(addr, port):
    ts0 = time.clock_gettime_ns(time.CLOCK_REALTIME)
    data = sigma.get_json_frame(addr, port)
    if data is None:
        return None, None, None
    frame = f"frame{data['frame_id']}"
    img = cv2.cvtColor(data['raw_image'], data['conversion_flag'])

    inp = image2input(img, frame)
    ts1 = time.clock_gettime_ns(time.CLOCK_REALTIME)
    print(f"Receive Data: {(ts1 - ts0) / 1e9}s")

    frame_id = data['frame_id']
    frame_meta = data['frame_misb_meta']
    return frame_id, frame_meta, inp


def _con_name(con, names):
    if names is None:
        return str(con.type)
    try:
        name = names[con.type]
    except KeyError:
        name = str(con.type)
    return name


def _bbox(con):
    center = np.array([int(con.x), int(con.y)])
    half_extent = np.array(con.features[2] // 2, con.features[3] // 2)
    tl = (*(center - half_extent).astype(int),)  # Top Left
    br = (*(center + half_extent).astype(int),)  # Bottom Right
    return [int(tl[0]), int(tl[1]), int(br[0]), int(br[1])]


def _make_chip(ecd: mats.Ecdata):
    try:
        chip = np.stack(
            (ecd.snippet('IMG-R').data, ecd.snippet('IMG-G').data,
             ecd.snippet('IMG-B').data),
            axis=2
        )
        chip = (chip * 255).astype(np.uint8)

        buff = BytesIO()
        Image.fromarray(chip).save(buff, format="JPEG")
        return buff
    except:
        print('Failed to generate chip for detection.')
        pass
    return None


def process_sigma(xpipe, sigma_cfg, names=None):
    sleep_time = 3
    sleep_max_iter = 20
    sleep_counter = 0
    frame_info = deque()
    iserver = (sigma_cfg['rawframe_server'], sigma_cfg['rawframe_port'])
    oserver = (sigma_cfg['atr_detection_server'],
               sigma_cfg['atr_detection_port'])
    print(f"Raw Frames: {iserver[0]}:{iserver[1]}")
    print(f"ATR Detections: {oserver[0]}:{oserver[1]}")

    while sleep_counter < sleep_max_iter:
        frame_id, frame_meta, inp = _get_frame(iserver[0], iserver[1])

        if frame_id is not None:
            frame_info.append((frame_id, inp.filename, frame_meta))
            xpipe.queue(inp)

        while True:
            result = xpipe.results()
            # print(result)
            if result is None:
                break
            if len(frame_info) == 0:
                print('!! No meta for detections.')
                break

            frame = result[0].filename
            meta = []
            while len(frame_info) > 0:
                if frame_info[0][1] == frame:
                    meta = frame_info[0]
                    frame_info.popleft()
                    break
                frame_info.popleft()

            con = result[1][0]
            ecd = result[1][1]
            sigma_detect = {
                'frame_id': meta[0],
                'frame_misb_meta': meta[2],
                'name': [_con_name(c, names) for c in con],
                'class_id': [c.type for c in con],
                'confidence': [c.classconf for c in con],
                'bbox_coordinates': [_bbox(c) for c in con],
                'chip': [_make_chip(e) for e in ecd],
            }

            # Push sigma
            ts0 = time.clock_gettime_ns(time.CLOCK_REALTIME)
            sigma.push_json_atr(sigma_detect, oserver[0], oserver[1])
            ts1 = time.clock_gettime_ns(time.CLOCK_REALTIME)
            print(f"Send frame: {(ts1 - ts0)/1e9}s")

        if len(frame_info) == 0 and frame_id is None:
            sleep_counter += 1
            print(f'({sleep_counter}) Waiting for {sleep_time} seconds.')
            time.sleep(sleep_time)
    return

