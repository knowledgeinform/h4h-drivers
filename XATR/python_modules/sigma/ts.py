import subprocess as sub
import os.path as osp
import json
from tqdm import trange

import klvdata


def num_frames(fn):
    result = sub.run([
            'ffprobe', '-v', '0', '-select_streams', 'v:0', '-count_frames',
            '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0', fn
        ],
        capture_output=True)
    # Attempt to get output
    try:
        result = int(result.stdout.split(b'\n')[0])
    except:
        result = None

    return result


def extract_frame(fn, num, out_dir):
    out_fn = osp.join(out_dir, f'frame{num:04}.jpg')
    vfilter = r"select=eq(n\,{})".format(num)
    cmd = f"ffmpeg -y -v 0 -i \"{fn}\" -vf \"{vfilter}\" -vframes 1 {out_fn}"
    result = sub.run(cmd, shell=True)
    return result


def extract_klv(fn, out_dir):
    klv_fn = osp.splitext(fn)[0] + '.klv'
    if not osp.exists(klv_fn):
        print('Extracting KLV data...')
        cmd = f'ffmpeg -i \"{fn}\" -map 0:1 -codec copy -f data \"{klv_fn}\"'
        sub.run(cmd, shell=True)
        if not osp.exists(klv_fn):
            raise RuntimeError('Failed extraction of KLV data.')

    with open(klv_fn, 'rb') as fh:
        fid = 0
        for packet in klvdata.StreamParser(fh.read()):
            md = packet.MetadataList()
            data = {}
            for k in md:
                data[md[k][0]] = md[k][3]

            meta_fn = osp.join(out_dir, f'meta{fid:04}.json')
            with open(meta_fn, 'w') as jh:
                jobj = json.dumps(data, indent=2)
                jh.write(jobj)
            fid += 1
    return


def extract_images(fn, out_dir):
    """
    Extract raw image frames from Nibbler JSON data stream.

    :param fn: Filename of Nibbler JSON file.
    :type fn: str
    :param out_dir: Path to output directory.
    :type out_dir: str
    :return: None
    """
    nframes = num_frames(fn)

    if nframes is None or nframes == 0:
        print(f'!! {fn} has no frames.')
        return

    for k in trange(nframes):
        if osp.exists(osp.join(out_dir, f'frame{k:05}.jpg')):
            continue
        extract_frame(fn, k, out_dir)

    # Extract KLV data
    try:
        extract_klv(fn, out_dir)
    except RuntimeError:
        print(f'No KLV data for {fn}.')

    return
