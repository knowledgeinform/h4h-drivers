# -*- coding: utf-8 -*-
"""
Created on Wed May 26 16:06:29 2021

@author: user
"""
import os.path as osp
from glob import glob
# import math
import mats.log
from mats import Archive
from mats.perf.report import PerfReport
from mats.perf.perf_summary import ArchiveSummary
from mats.perf.contact_summary import ContactSummary
from multiprocessing import Pool
from tqdm.contrib.concurrent import process_map
from tqdm import tqdm

def archive_summary(filename, verbose=None):
    if verbose is None:
        verbose = False

    if verbose:
        print(f"Parsing {filename}...")
    try:
        perf = ArchiveSummary(filename)
    except RuntimeError:
        mats.log.error(f"Failure loading {filename}.")
        return None

    return dict(perf)


def report(arc_folder, thresh=None, verbose=None, class_info=False, class_labels=None, n_workers=20):
    mats.pkg.ensure_scan()
    
    arc = Archive()
    rep = PerfReport(class_info=class_info, class_labels=class_labels)

    if thresh is None:
        thresh = 0.5
    if verbose is None:
        verbose = False

    arc.location(arc_folder)
    print(f'Searching for files in {arc_folder}...')
    files = glob(arc_folder + '/**/*.h5', recursive=True)
    print(f'Sorting {len(files)}, files...')
    files.sort()
    
    print(f'Processing {len(files)}, files...')
    #pool = Pool(20)
    #result = pool.map(archive_summary, files)
    if n_workers > 1:
        result = process_map(archive_summary, files, max_workers=n_workers, chunksize=1, tqdm_class=tqdm)
    else:
        result = []
        for filename in tqdm(files):
            tmp = archive_summary(filename)
            result.append(tmp)
            
    for r in result:
        rep.add_archive(r)
    rep.Threshold = thresh

    if verbose:
        print("Performance:")
        print("Tp: {}".format(rep.Tp))
        print("Pd: {}".format(rep.Pd))
        print("Pc: {}".format(rep.Pc))
        print("PdPc: {}".format(rep.PdPc))
        print("Total Gt: {}".format(rep.TotalGt))
        print("Detector Missed Targets: {}".format(
            len(rep.DetectorMissedTargets)))
        print("Classifier Missed Targets: {}".format(
            len(rep.ClassifierMissedTargets)))
        print("Number of contacts: {}".format(len(rep.Contacts)))

    # Write report to file.
    # std::string outfn = infile;
    # mats::file_path(outfn, "perf_report.json");
    # write_report(outfn, report);
    return rep


    
    

