#! /usr/bin/env python3
"""
XATR Image Pipeline - xatr_image_pipeline.py

Pipeline to process image data with PyMATS modules

Created Jul 13 2022
chase.m.bishman.civ@us.navy.mil NSWC PCD (X12)
"""

import argparse
import os
import threading

import numpy as np
from pathlib import Path
from PIL import Image
import warnings
from collections import deque
import mats

# import sys
# sys.path.append("/build/pymats")
# print(sys.path)


# Import custom lacex pymats detectors
# TODO integrate these detectors into mats so mats.pkg can be used

# Supported image formats
IMG_FORMATS = ['.png', '.jpg', '.jpeg', '.tif', '.tiff']


class XatrTask(threading.Thread):
    def __init__(self, func, inp):
        super(XatrTask, self).__init__()
        self.running = False
        self.func = func
        self.inp = inp
        self.result = None
        return

    def run(self):
        self.running = True
        try:
            self.result = self.func(self.inp)
        except Exception as err:
            print(err)
            print(f'Failure processing file {self.inp.filename}')
        self.running = False
        return


class XatrImagePipeline(mats.Interface):
    """Class for running image data through an XATR pipeline
    """
    def __init__(self):
        self._name = 'stmRlacImageRgb'
        self.det = None
        self.cls = None
        self.max_jobs = 10
        self._jobs = deque()
        self._results = deque()

    def engine(self):
        return self._name

    def scan(self):
        mats.pkg.scan()
        return

    def getType(self, mod_type):
        return mats.pkg.get_type(mod_type)

    def module(self, mod_name):
        mods = mats.pkg.module_info(mod_name)
        if not mods or len(mods) == 0:
            return None

        if len(mods) > 1:
            mats.log.info(f'More than one package "{mod_name}" found.')
        return mods[0]

    def create(self, mod_type, mod_name):
        return mats.pkg.create(mod_name)

    def configure(self, cfg: mats.AtrConfig):
        if cfg.detector:
            self.det = self.create('detector', cfg.detector)
            self.det.configure(cfg.det_cfg)
        else:
            self.det = None
            raise ModuleNotFoundError(
                f"Could not find the detector: {cfg.detector}")

        if cfg.classifier:
            self.cls = self.create('classifer', cfg.classifier)
            self.cls.configure(cfg.cls_cfg)
        else:
            self.cls = None
            warnings.warn("Classifier is not provide. Detections will not be "
                          "classified.")
        return

    def process(self, inp):
        # Detect targets
        con, ecd = self.det.detect(inp)
        for ix in range(len(con)):
            mats.core.detsub_contact_fill(inp, con[ix], ecd[ix])

        # Clasify contacts
        self.cls.classify(con, ecd)

        return con, ecd

    def queue(self, inp: mats.Input):
        # Clear out existing jobs
        if len(self._jobs) > 0:
            while not self._jobs[0].running:
                job = self._jobs[0]
                self._jobs.popleft()
                self._results.append((job.inp, job.result))

        # Add new task
        if len(self._jobs) < self.max_jobs:
            job = XatrTask(self.process, inp)
            job.run()
            self._jobs.append(job)
            return
        print(f'Dropping: {inp.filename}')
        return

    def results(self):
        if len(self._jobs) > 0:
            while not self._jobs[0].running:
                job = self._jobs[0]
                self._jobs.popleft()
                self._results.append((job.inp, job.result))
                if len(self._jobs) == 0:
                    break
        if len(self._results) == 0:
            return None
        job = self._results[0]
        self._results.popleft()
        return job
