import os.path as osp
import numpy as np
import pandas as pd
from warnings import warn
from mats.report import _load_json


def _find_bin(bins, val):
    if val < bins[0]:
        raise ValueError('Value less than find bin starting value.')

    for k in range(1, len(bins)):
        if val < bins[k]:
            return k-1
    return k


def _detection_stats(data):
    if not isinstance(data, list):
        raise ValueError('data needs to be a list of missions perf reports.')

    total_gt = 0
    missed_gt = 0
    pd = 0
    for d in data:
        if d['TotalGt'] <= 0:
            continue
        total_gt += d['TotalGt']
        missed_gt += len(d['Detector']['MissedTargets'])

    if total_gt > 0:
        pd = (total_gt - missed_gt)/total_gt
    else:
        pd = -1
    return {'TotalGt': total_gt, 'MissedGt': missed_gt, 'Pd': pd}


def _confusion_matrix(data, thres):
    if not isinstance(data, list):
        raise ValueError('data needs to be a list of missions perf reports.')

    ttp = 0  # Total True Positives
    ttn = 0  # Total True Negatives
    ntp = 0  # Number True Positives
    nfp = 0  # Number False Positives
    for d in data:
        gt = np.array([c['Gt'] for c in d['Contacts']])
        conf = np.array([c['Conf'] for c in d['Contacts']])
        num_pos = sum(gt)  # Number of positive contacts
        nn = len(gt) - num_pos  # Number of negative contacts

        # Repeated positive calls should be put in the prune list for
        # perf_report. So the following shouldn't happen.
        if d['TotalGt'] < num_pos:
            warn('More target contacts than GT.')

        ttp += num_pos
        ttn += nn
        ntp += sum(conf[gt] > thres)
        nfp += sum(conf[~gt] > thres)
    info = {
        'TTP': ttp,
        'TTN': ttn,
        'NTP': ntp,
        'NFP': nfp,
        'NFN': ttp - ntp,
        'NTN': ttn - nfp
    }
    return info


def _cross_track_detection(data, thres, nbin=10, max_range=35):
    if not isinstance(data, list):
        raise ValueError('data needs to be a list of missions perf reports.')
    bins = np.arange(0, max_range, max_range/nbin)
    ct_table = np.zeros((4, nbin))  # Rows: Num Pos, Num Neg, Pos Det, Neg Det
    for d in data:
        gt = np.array([c['Gt'] for c in d['Contacts']])
        conf = np.array([c['Conf'] for c in d['Contacts']])
        rng = np.array([c['Range'] for c in d['Contacts']])

        for k in range(len(gt)):
            ix = _find_bin(bins, rng[k])
            if gt[k]:
                ct_table[0,ix] += 1
                if conf[k] > thres:
                    ct_table[2,ix] += 1
            else:
                ct_table[1,ix] += 1
                if conf[k] > thres:
                    ct_table[3,ix] += 1
    return ct_table


def _mission_stats(data):
    if not isinstance(data, list):
        raise ValueError('data needs to be a list of missions perf reports.')

    mission_time = 0
    mission_area = 0
    num_images = 0
    for d in data:
        num_images += d['NumberFiles']
        mission_time += d['MissionTime']
        mission_area += d['MissionArea']

    info = {
        'MissionTime': mission_time,
        'MissionArea': mission_area*2.91553e-7,
        'NumberFiles': num_images,
        'NumberMissions': len(data)
    }
    return info


def _processing_stats(data):
    if not isinstance(data, list):
        raise ValueError('data needs to be a list of missions perf reports.')

    num_files = 0
    total_time = 0
    for d in data:
        num_files += d['NumberFiles']
        total_time += d['ProcessingTime']
    per_file_time = total_time/num_files
    return (total_time, per_file_time)


# Mission Stats: MILCOs, MILCO OPPs, NOMBOs, NOMBO OPPs, Area, Total Missions,
#                Total Mission Run Time
# Performance: Total Calls, Duplicate Calls, Processing Time,
#              Processing Rate (min/nmi2), Hits (SP), Hits (AG), Misses (SP),
#              Misses (AG), False Alarms
#              Detection Rate (SP), Detection Rate (AG), False Alarm Density,
#              TPP, FPP
# Shape Detection (Single Pass): Shapes A,B,C Detection Rate
# ROC AUC
# Cross Track Detection Rates
# ROC
# Confidence Distribution

class AtrcfgReport:
    def __init__(self, atrcfg):
        self.filename = 'AtrcfgReport.tex'
        self._save_location = '.'
        self.atrcfg = atrcfg
        self.report_datetime = ''
        self.missions = None
        self.data = {}

    def save_location(self, loc=None):
        if not loc:
            return self._save_location
        self._save_location = loc

    def cfg(self):
        return self.atrcfg

    def add_mission(self, folder):
        name = osp.basename(folder)

        info = {
            'name': name,
            'location': folder,
            'perf': _load_json(osp.join(folder, 'perf_report.json'))
        }
        if info['perf']['TotalGt'] == 0:
            warn('!! Empty GT for {}. Skipping dataset.'.format(name))
            return
        self.data[name] = info
        if self.missions:
            self.missions.append(name)
        else:
            self.missions = [name]

    def cls_perf(self, thres):
        dsn = list(self.data.keys())
        # dsn_short = [d[:25] for d in dsn]
        dvn = ['PdPc', 'FA']
        ix = pd.MultiIndex.from_product([dsn, dvn])

        data = np.zeros((len(thres), 2*len(dsn)))
        for k in range(len(thres)):
            for j in range(len(dsn)):
                cmx = _confusion_matrix([self.data[dsn[j]]['perf']], thres[k])
                data[k, 2*j] = cmx['NTP']/cmx['TTP']
                data[k, 2*j+1] = cmx['NFP']
        pd.set_option('precision', 4)
        pd.set_option('display.max_colwidth', -1)
        pd.option_context('display.colheader_justify','right')
        tbl = pd.DataFrame(data, columns=ix, index=thres)
        print(tbl)
        return tbl

    def performance(self, display=True):
        perfs = [self.data[mission]['perf'] for mission in self.data]
        thres = perfs[0]['Threshold']

        stats = _detection_stats(perfs)
        if display:
            print('++ DETECTOR\nTotalGt: {}, MissedGt: {}, Pd: {}'.format(
                stats['TotalGt'], stats['MissedGt'], stats['Pd']))

        cmatrix = _confusion_matrix(perfs, thres)
        ct_table = _cross_track_detection(perfs, thres)

        if display:
            print('++ CLASSIFIER')
            mx = (
                '{} {}\n'
                '{} {}').format(
                cmatrix['NTP'], cmatrix['NTN'], cmatrix['NFN'], cmatrix['NFP']
            )
            print(mx)

        if not display:
            return stats

    def mission_info(self, display=True):
        perfs = [self.data[mission]['perf'] for mission in self.data]
        stats = _mission_stats(perfs)
        if display:
            print('++ MISSION INFORMATION\nMission Time: {}, Mission Area: {}, Number of Files: {}, Number of Missions: {}'.format(
                stats['MissionTime'], stats['MissionArea'],
                stats['NumberFiles'], stats['NumberMissions']))
        else:
            return stats

    def processing_info(self, display=True):
        perfs = [self.data[mission]['perf'] for mission in self.data]
        stats = _processing_stats(perfs)
        if display:
            print('++PROCESSING INFORMATION\nTotal Processing Time: {}, Avg Processing Time per File: {}'.format(
                stats[0], stats[1]))
        else:
            return stats

    # def generate(self):
    #     doc = LatexDoc()
    #     doc.add_package('inputenc', 'utf8')
    #     doc.add_package('graphicx')
    #     doc.add_package('booktabs')
    #     doc.add_package('fullpage')
    #     doc.add_package('multicol')

    #     # Information about data in report
    #     print("Collecting mission information...")
    #     doc.add_section('Report Contents')
    #     doc.add(f'ATR Configuration: {self.atrcfg}\\newline\n')
    #     doc.add(f'Report Date/Time: {self.report_datetime}\n')

    #     total_images = 0
    #     mission_stats = []
    #     items = []
    #     for dn in self.datasets:
    #         print(dn)
    #         stats = self.mission_stats(dn)
    #         total_images += stats['num_images']
    #         mission_stats.append(stats)
    #         line = (
    #             '{{\\bf {}}}\\newline\n'
    #             'Duration - ${:.4}$hrs, '
    #             'Area - ${:.4}$nm2, '
    #             'Images - {}\n'.format(
    #                 dn,
    #                 stats['mission_time']/60,
    #                 stats['mission_area'],
    #                 stats['num_images']
    #             )
    #         )
    #         items.append(line)
    #     doc.add_itemize(items)

    #     # Overall performance
    #     print("Calculating overall performance...")
    #     doc.add('\\pagebreak\n')
    #     doc.add_section('Overall Performance')

    #     # doc.generate('perf_report.tex')
    #     det_info = self.detection_stats()
    #     pt = self.processing_time()

    #     total_pdpc, total_fa, total_thres, total_con = self.roc_curve()
    #     fa = [x*total_con['ntar']/total_images for x in total_fa]

    #     doc.add('\\begin{multicols}{2}\n \\noindent ')
    #     doc.add((
    #         'Total processing time: ${:.4}$hrs\\newline\n'
    #         'Mean processing time (per file): ${:.4}$s\\newline\n'
    #         'Number of groundtruth targets: {}\\newline\n'
    #         'Probability of detection: {}\\newline\n'
    #         'Number of undetected groundtruth targets: {}\\newline\n'
    #         'Number of targets: {}\\newline\n'
    #         'Number of non-targets: {}\\newline\n'
    #     ).format(
    #         pt[0]/60.0/60.0, pt[1], det_info['TotalGt'],
    #         det_info['Pd'], det_info['MissedGt'], total_con['tar'],
    #         total_con['ntar']))
    #     doc.add('\columnbreak')
    #     doc.add_roc_table(total_pdpc, fa, total_thres)
    #     doc.add('\\end{multicols}\n')

    #     fig_name = self.atrcfg+'-overall-roc.png'
    #     doc.add_roc_plot(total_pdpc, fa, fig_name, 'Overall Performance')

    #     # Preformance on each dataset
    #     for mission in mission_stats:
    #         dn = mission['name'][0]
    #         print(mission)
    #         print("Calculating "+dn+" performance...")
    #         doc.pagebreak()
    #         doc.add_section(dn)

    #         det_info = self.detection_stats(dn)
    #         pt = self.processing_time(dn)
    #         pdpc, fa, thres, con = self.roc_curve(dn)
    #         fa = [x*con['ntar']/mission['num_images'] for x in fa]

    #         doc.add('\\begin{multicols}{2}\n \\noindent ')
    #         doc.add((
    #             'Total processing time: ${:.4}$hrs\\newline\n'
    #             'Mean processing time (per file): ${:.4}$s\\newline\n'
    #             'Number of groundtruth targets: {}\\newline\n'
    #             'Probability of detection: {}\\newline\n'
    #             'Number of undetected groundtruth targets: {}\\newline\n'
    #             'Number of targets: {}\\newline\n'
    #             'Number of non-targets: {}\\newline\n'
    #         ).format(
    #             pt[0]/60.0/60.0, pt[1], det_info['TotalGt'], det_info['Pd'],
    #             det_info['MissedGt'], con['tar'], con['ntar']
    #         ))
    #         doc.add('\columnbreak')
    #         doc.add_roc_table(pdpc, fa, thres)
    #         doc.add('\\end{multicols}\n')

    #         fig_name = self.atrcfg+'-'+dn+'-roc.png'
    #         doc.add_roc_plot(pdpc, fa, fig_name, dn)

    #     # Finalize Latex document
    #     doc.generate(self.filename)
