import glob
import socket
import json
import numpy as np
import base64
import time
from io import BytesIO
import re
import tqdm
import yaml
import os.path as osp
import os
import cv2


def logging(msg, logfile=None):
    try:
        ts = time.clock_gettime_ns(time.CLOCK_REALTIME)
    except AttributeError:
        # Windows doesn't have 'clock_gettime_ns'
        ts = time.monotonic_ns()

    if len(msg) > 2000:
        print(f'{ts}({len(msg)}): {msg[:500]}...{msg[-500:]}')
    else:
        print(f'{ts}: {msg}')

    if logfile is not None:
        with open(logfile, 'a') as fp:
            fp.write(f'{ts}: {msg}\n')
    return


def example_atr_detect():
    return {
        "frame_id": 1713,
        "frame_misb_meta": {
            "frame_center_latitude": 30.509953722623475,
            "frame_center_longitude": -86.58931215550734,
            "offset_corner_latitude_1": 3.068457009547387e-05,
            "offset_corner_latitude_2": -1.7098402413040503e-05,
            "offset_corner_latitude_3": -3.091688640211032e-05,
            "offset_corner_latitude_4": 1.725825243781287e-05,
            "offset_corner_longitude_1": 3.2613078957410835e-06,
            "offset_corner_longitude_2": 2.9570315518867574e-05,
            "offset_corner_longitude_3": -3.2859975220844717e-06,
            "offset_corner_longitude_4": -2.984678565098875e-05,
            "time_stamp": 1679002768156348
        },
        "name": ["Object 1", "Object 2", "Clutter"],
        "class_id": [1, 2, 8],
        "confidence": [0.7, 0.5, 0.4],
        "bbox_coordinates": [[0, 120, 25, 145], [156, 481, 170, 495],
                             [1067, 927, 1117, 977]],
        "chip": ["", "", ""]
    }


def js_image_decode(img, nr, nc, depth):
    """
    Convert serialized raw image to YUV (UYVY) numpy array.

    :param img: Serialized raw image string.
    :type img: str
    :param nr: Number of rows in image.
    :type nr: int
    :param nc: Number of columns in image.
    :type nc: int
    :param depth: Number of channels for serialized raw image
    :type depth: int
    :return: BGR numpy array
    :rtype: numpy.array
    """
    img = base64.b64decode(img)
    img = np.frombuffer(img, np.uint8)
    img = img.reshape(nr, nc, depth)
    return img


def js_image_encode(img):
    """
    Convert serialized raw image to BGR numpy array.

    :param img: YUV numpy array.
    :type img: numpy.array
    :return: Serialized numpy array.
    :rtype: str
    """
    if isinstance(img, np.ndarray):
        img = base64.b64encode(img.tobytes()).decode('UTF-8')
    elif isinstance(img, BytesIO):
        img = base64.b64encode(img.getvalue()).decode('UTF-8')
    else:
        raise TypeError(type(img))
    return img


def json_stream_server(json_file, host=None, port=None, logfile=None):
    if host is None:
        host = socket.gethostname()
    if port is None:
        port = 5556

    sock = socket.socket()
    sock.bind((host, port))
    sock.listen(5)

    # while not shutdown_flag:
    #     conn, addr = sock.accept()
    #     print(f'CONNECT: {addr}')
    #     conn.send(b'SENDING DATA...')
    #     conn.close()

    with open(json_file, 'r') as fh:
        logging('Loading file...', logfile)
        data = fh.read()
        # fh.seek(0, 2)
        # fsize = fh.tell()
        # fh.seek(0, 0)

    logging('Locating frames...', logfile)
    frames = re.split('} *{', data)
    frames[0] += '}'
    frames[-1] = '{' + frames[-1]
    for ix in range(len(frames)):
        if frames[ix][0] != '{':
            frames[ix] = '{' + frames[ix]
        if frames[ix][-1] != '}':
            frames[ix] += '}'

    logging('Frames loaded...', logfile)
    for frame in tqdm.tqdm(frames):
        logging(f'Frame ready {len(frame)}.', logfile)
        conn, addr = sock.accept()
        logging(f'CONNECT: {addr}', logfile)
        conn.send(frame.encode('utf-8'))
        logging(f'Frame sent: {frame[0:20]}', logfile)
        conn.close()

    logging('Stopping', logfile)
    return


def json_stream_writer(remote, port, outdir):
    if not osp.exists(outdir):
        os.mkdir(outdir)
    while True:
        data = get_json_frame(remote, port)
        if data is None:
            time.sleep(0.03)
            continue
        img_fn = f"frame{data['frame_id']:05}.png"
        img = cv2.cvtColor(data['raw_image'], data['conversion_flag'])
        cv2.imwrite(osp.join(outdir, img_fn), img)
        del data['raw_image']

        meta_fn = f"meta{data['frame_id']:05}.json"
        with open(meta_fn, 'w') as fh:
            yaml.safe_dump(data, fh)
    return


def json_atr_server(host=None, port=None, logfile=None):
    if host is None:
        host = socket.gethostname()
    if port is None:
        port = 8080

    sock = socket.socket()
    sock.bind((host, port))
    sock.listen(10)

    while True:
        conn, addr = sock.accept()
        logging(f'CONNECT: {addr}', logfile)

        data = b''
        while True:
            buf = conn.recv(4096)
            if not buf:
                break
            data += buf
            # if len(buf) < 4096:
            #     break
        conn.close()
        # data = json.loads(data)
        logging(data, logfile)
    logging('Stopping', logfile)
    return


def get_json_frame(addr, port=None):
    if port is None:
        port = 5556
    sock = socket.socket()
    sock.connect((addr, port))

    data = b''
    try:
        while True:
            buf = sock.recv(4096)
            data += buf
            if len(buf) == 0:
                break
            buf = b''
    except socket.timeout:
        pass
    finally:
        sock.close()

    if len(data) == 0:
        print('No data received.')
        return None

    data_copy = data
    try:
        data = json.loads(data)
        data['raw_image'] = js_image_decode(
            data['raw_image'],
            data['image_rows'],
            data['image_cols'],
            data['depth'])
    except Exception:
        print(data_copy)
        raise
    return data


def push_json_atr(con, addr, port=None):
    """

    :param con: ATR detections to send.
    :type con: dict
    :param addr: Sigma server address
    :type addr: str
    :param port: Sigma server port for ATR detections
    :type port: int
    :return:
    """
    if port is None:
        port = 8080
    sock = socket.socket()
    sock.connect((addr, port))

    c = con  # .copy()
    for ix in range(len(c['chip'])):
        c['chip'][ix] = js_image_encode(c['chip'][ix])
    msg = json.dumps(c)

    sock.send(msg.encode('utf-8'))
    sock.close()
    return


def load_sigma_results(fn):
    """
    Load ATR contact results from file (JSON file with concatenated Sigma JSON
    detection messages).
    :param fn:
    :return:
    """
    times = []
    results = []
    failed = 0
    with open(fn, 'r') as fh:
        logging('Loading file...')
        for msg in fh:
            msg = msg.lstrip("'b\'")
            msg = msg.rstrip("\'\n")

            try:
                msg = json.loads(msg)
            except:
                failed += 1
                # print(f'Failed Parse: {msg}')
                continue
            results.append(msg)
    print(f'Number of incomplete messages: {failed}\n')
    return results


def load_json_results(fn):
    """
    Load ATR contact results from file (JSON file with concatenated Sigma JSON
    detection messages).

    :param fn:
    :return:
    """
    times = []
    results = []
    tot = 0
    failed = 0
    with open(fn, 'r') as fh:
        logging('Loading file...')
        for line in fh:
            try:
                parts = line.split(': ', 1)
            except:
                print('error')

            if len(parts) != 2:
                continue
            if 'CONNECT' in parts[1]:
                continue
            msg = parts[1].lstrip("'b\'")
            msg = msg.rstrip("\'\n")

            tot += 1
            try:
                msg = json.loads(msg)
            except:
                failed += 1
                # print(f'Failed Parse: {msg}')
                continue
            times.append(parts[0])
            results.append(msg)
    print(f'Total Frames: {tot}, Number of incomplete messages: {failed}\n')
    return times, results


def load_sigma_results(fn):
    """
    Load ATR contact results from file (JSON file with concatenated Sigma JSON
    detection messages).

    :param fn:
    :return:
    """
    times = []
    results = []
    failed = 0
    with open(fn, 'r') as fh:
        logging('Loading file...')
        for msg in fh:
            msg = msg.lstrip("'b\'")
            msg = msg.rstrip("\'\n")

            try:
                msg = json.loads(msg)
            except:
                failed += 1
                # print(f'Failed Parse: {msg}')
                continue
            results.append(msg)
    print(f'Number of incomplete messages: {failed}\n')
    return results


def detections2yml(results, yml_filename, save_chips=None):
    """
    Convert Sigma detections to CSO YAML format.

    :param results: Sigma detections
    :param yml_filename: Output CSO YAML filename
    :return:
    """
    if save_chips is None:
        save_chips = False
    if isinstance(results, str):
        results = load_sigma_results(results)
    
    yml_dir = osp.dirname(yml_filename)
    cons = []
    for det in results:
        if not isinstance(det, dict):
            continue
        print(det)

        name_label = 'name'
        if name_label not in det:
            name_label = 'names'

        if isinstance(det['frame_id'], str):
            print(det['frame_id'])
            det['frame_id'] = int(det['frame_id'])

        frame = f"image{det['frame_id']:05}.png"
        for ix in range(len(det[name_label])):
            # if det['confidence'][ix] == 0:
            #     print('!! Dropping zero conf contact.')
            #     continue
            bbox = det['bbox_coordinates'][ix]
            x = (bbox[2] + bbox[0]) / 2
            y = (bbox[3] + bbox[1]) / 2
            w = bbox[2] - bbox[0] + 1
            h = bbox[3] - bbox[1] + 1

            cons.append({
                'Filename': frame,
                'Type': det[name_label][ix].rstrip(),
                'Position': [x, y],
                'Dimension': [w, h],
                'Confidence': det['confidence'][ix]
            })
            if save_chips:
                fid = det['frame_id']
                conf = round(det['confidence'][ix]*100)
                ctype = det['names'][ix]
                chip_basename = f"image{fid:05}-{ix:02}-{ctype}-{conf}.jpg"
                chip_fn = osp.join(yml_dir, chip_basename)
                with open(chip_fn, 'bw') as fh:
                    fh.write(base64.b64decode(det['chip'][ix]))

    with open(yml_filename, 'w', encoding='utf-8') as fh:
        yaml.safe_dump(cons, fh)
    return


def convert_detections(results_dir):
    """
    Converts directory of Sigma detection to CSO YAML format.

    Args:
        results_dir: Directory with Sigma detection results.

    Returns:
        None
    """
    if not osp.exists(results_dir):
        raise FileNotFoundError(f'Results directory does not exist ({results_dir}).')
    if not osp.isdir(results_dir):
        raise NotADirectoryError(f'Results directory is not a directory ({results_dir}).')
    fns = glob.glob(osp.join(results_dir, '*.txt'))

    for fn in fns:
        fn_base = osp.splitext(osp.basename(fn))[0]
        times, results = load_json_results(fn)

        msk = ['frame_id' in r for r in results]
        times = [t for (t, m) in zip(times, msk) if m]
        results = [r for (r, m) in zip(results, msk) if m]

        detections2yml(results, osp.join(results_dir, fn_base+'.yml'))
        fps = len(results) / ((int(times[-1]) - int(times[0])) * 1e-9)  # Assumes nanosecond timestamps
        print(f'Average FPS: {fps}')
    return
