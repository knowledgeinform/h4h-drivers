import mats
from threading import Thread
import numpy as np
import math


def detect_eval(det, inp, result):
    result[0], result[1] = det(inp)
    return


class detFusion(mats.Detector):
    def __init__(self):
        self._dets = []
        self._method = 'majority'
        self._groups = []
        self._fusion_thresh = 2
        pass

    def configure(self, cfg):
        if 'det' in cfg:  # Should be a Cell, but a list will work in Python.
            for d in cfg['det']:
                self._dets.append({
                    'det': d, 'cfg': None, 'grp': 0, 'mod': None, 'result': [None, None], 'id': -1
                })
        else:
            raise ValueError('Configuration is missing "det" list.')

        if 'cfg' in cfg:  # Should be a Cell, but a list will work in Python.
            if len(self._dets) != len(cfg['cfg']):
                raise ValueError(
                    'Length difference between "det" and "cfg" '
                    'configurations.')
            for ix in range(len(self._dets)):
                self._dets[ix]['cfg'] = cfg['cfg'][ix]
                self._dets[ix]['id'] = ix
        else:
            raise ValueError('Configuration is missing "cfg" list.')

        if 'fusion_group' in cfg:
            if len(self._dets) != len(cfg['fusion_group']):
                raise ValueError(
                    'Length difference between "det" and "fusion_group" '
                    'configurations.')
            for ix in range(len(self._dets)):
                self._dets[ix]['grp'] = cfg['fusion_group'][ix]
        self._groups = list(set([det['grp'] for det in self._dets]))

        if 'fusion_method' in cfg:
            self._method = cfg['fusion_method']

        if 'fusion_thresh' in cfg:
            self._fusion_thresh = cfg['fusion_thresh']

        for ix in range(len(self._dets)):
            self._dets[ix]['mod'] = mats.pkg.create(self._dets[ix]['det'])
            self._dets[ix]['mod'].configure(self._dets[ix]['mod'])
        return

    def detect(self, inp):
        workers = []
        ndet = len(self._dets)

        # Start detectors
        for ix in range(ndet):
            det = self._dets[ix]['mod'].detect
            out = self._dets[ix]['result']
            th = Thread(target=detect_eval, args=(det, inp, out))
            th.start()
            workers.append(th)

        # Wait for detectors to finish
        for ix in range(ndet):
            workers[ix].join()

        # Fuse results
        con = mats.ContactList()
        ecd = mats.EcdataList()
        for group in self._groups:
            det_group = [det for det in self._dets if det['grp'] == group]

            if len(det_group) < 2:
                # No fusion necessary
                if len(det_group[0]['result'][0]) > 0:
                    con.extend(det_group[0]['result'][0])
                    ecd.extend(det_group[0]['result'][1])
            else:
                # Collect contacts for group and give to fuser.
                # for ix in range(len(det_group)):
                #     con = [{'det': ix, 'x': con.x, 'y': con.y}
                #            for con in det_group[ix]['result'][0]]
                raise NotImplementedError('Fusing contacts not implemented.')
        pass

    def _fuser(self, det):
        con = mats.ContactList()
        ecd = mats.EcdataList()

        if len(det) == 0:
            return con, ecd

        # This works by chaining detections within fusion radius together from
        # different detectors.
        ngrp = 0
        match = np.ones(len(det)) * -1
        dist = np.zeros(len(det))
        for k in range(len(det)-1):
            for j in range(1, len(det)):
                if det[k]['det'] == det[j]['det']:
                    continue

                dy2 = (det[k]['y'] - det[j]['y']) ** 2
                dx2 = (det[k]['x'] - det[j]['x']) ** 2
                d = math.sqrt(dy2 + dx2)

                # Outside fusion radius
                if d >= self._fusion_thresh:
                    continue

                if match[k] < 0 or dist[k] > d:
                    match[k] = j
                    dist[k] = d
                if match[j] < 0 or dist[j] > d:
                    match[j] = k
                    dist[j] = d
                ngrp += 1

        if ngrp == 0:
            return con, ecd

        for k in range(len(det)):
            if match[k] < 0:
                continue

            # print("Matching ")
            j = k
            x = 0.0
            y = 0.0
            s = 0.0
            cnt = 0.0
            while match[j] >= 0:
                x += det[j]['x']
                y += det[j]['y']
                s += det[j]['score']
                cnt += 1
                nxt = int(match[j])
                match[j] = -1
                j = nxt

            if cnt < self._fusion_thresh:
                continue

            c = mats.Contact()
            e = mats.Ecdata()
            c['x'] = math.floor(x/cnt)
            c['y'] = math.floor(y/cnt)
            e['detscore'] = s/cnt

            con.append(c)
            ecd.append(e)

        return con, ecd

    def train(self):
        pass
