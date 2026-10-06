import os
from os.path import isdir, join
# import numpy as np
# from math import floor
from mats.report import _load_json, _cum_sum
import sklearn.metrics
from collections import Counter
import matplotlib.pyplot as plt
from mats.report.latex import LatexDoc


class ConfigReport:
    def __init__(self):
        self.filename = 'PerfReport.tex'
        self._save_location = '.'
        self.atrcfg = ''
        self.report_datetime = ''
        self.datasets = None
        self.data = {}

    def _check_dataset(self, dataset):
        if not dataset:
            dataset = self.datasets
        elif isinstance(dataset, str):
            dataset = [dataset]
        return dataset

    def save_location(self, loc=None):
        if not loc:
            return self._save_location
        self._save_location = loc

    def cfg(self):
        return self.atrcfg

    """
    Collect mission information for a MATS archive folder.

    Output is a dictionary with the following fields:
      mission_time: Total vehicle collection time for processed data.
      mission_area: Total area processed by ATR.
      num_images: Number of files processed (Port/Stbd are counted separately).
    """
    def mission_stats(self, dataset=None):
        dataset = self._check_dataset(dataset)

        mission_time = 0
        mission_area = 0
        num_images = 0
        for d in dataset:
            num_images += self.data[d]['perf']['NumberFiles']
            mission_time += self.data[d]['perf']['MissionTime']
            mission_area += self.data[d]['perf']['MissionArea']

        info = {
            'name': dataset,
            'mission_time': mission_time,
            'mission_area': mission_area*2.91553e-7,
            'num_images': num_images
        }
        return info

    def processing_time(self, dataset=None):
        dataset = self._check_dataset(dataset)

        num_files = 0
        total_time = 0

        for d in dataset:
            num_files += self.data[d]['perf']['NumberFiles']
            total_time += self.data[d]['perf']['ProcessingTime']
        per_file_time = total_time/num_files
        return total_time, per_file_time

    """
    Collect detection information from perf_report.json file.

    Folder is assumed to contain archive files and perf_report.json file.
    Returns dictionary with the following fields:
       TotalGt: Total number of groundtruth opportunities associated with
                archive files in the folder.
      MissedGt: Number of undetected groundtruth associated with archive files.
            Pd: Probability of detection.
    """
    def detection_stats(self, dataset=None):
        dataset = self._check_dataset(dataset)

        total_gt = 0
        missed_gt = 0
        for d in dataset:
            if self.data[d]['perf']['TotalGt'] <= 0:
                print(f'!! Empty GT for {d}.')
                continue
            total_gt += self.data[d]['perf']['TotalGt']
            missed_gt += len(self.data[d]['perf']['Detector']['MissedTargets'])

        if total_gt > 0:
            pd = (total_gt - missed_gt)/total_gt
        else:
            pd = -1
        return {'TotalGt': total_gt, 'MissedGt': missed_gt, 'Pd': pd}

    def roc_curve(self, dataset=None):
        dataset = self._check_dataset(dataset)

        gt = []
        conf = []
        tot_gt = 0
        info = {'tar': 0, 'ntar': 0}
        for d in dataset:
            con = self.data[d]['perf']['Contacts']
            tot_gt += self.data[d]['perf']['TotalGt']
            con_gt = [x['Gt'] for x in con]
            cntr = Counter(con_gt)
            info['tar'] += cntr[True]
            info['ntar'] += cntr[False]
            gt.extend(con_gt)
            conf.extend([x['Conf'] for x in con])

        fpr, tpr, thres = sklearn.metrics.roc_curve(gt, conf)
        tpr *= info['tar']/tot_gt
        return tpr, fpr, thres, info
    
    def range_curve(self, dataset=None, y_unit=None, range_bins=None,
                    thresh=None):
        dataset = self._check_dataset(dataset)
        
        if not y_unit:
            y_unit = 'PdPc'
        if not thresh:
            thresh = self.data[self.datasets[0]]['perf']['Threshold']
        
        raise NotImplementedError("Not implemented yet.")
        # rng = []
        # yval = []
        # tot_gt = 0
        # for d in dataset:
        #     con = self.data[d]['perf']['Contacts']
        #     tot_gt += self.data[d]['perf']['TotalGt']
        #     rng.extend([x['Range'] for x in con])
        #     con = self.data[d]['perf']['Contacts']
        #     tot_gt += self.data[d]['perf']['TotalGt']
        #     con_gt = [x['Gt'] for x in con]
        #     cntr = Counter(con_gt)
        #     info['tar'] += cntr[True]
        #     info['ntar'] += cntr[False]
        #     gt.extend(con_gt)
        #     conf.extend([x['Conf'] for x in con])
        
    def contacts(self, dataset=None):
        dataset = self._check_dataset(dataset)
        
        con = []
        for d in dataset:
            con.extend([x for x in self.data[d]['perf']['Contacts']])
        return con
    
    def PD(self, dataset=None):
        dataset = self._check_dataset(dataset)
        
        tot_gt = 0
        num_dets = 0
        for d in dataset:
            con = self.data[d]['perf']['Contacts']
            num_dets += len([x for x in con if x['Gt']])
            tot_gt += self.data[d]['perf']['TotalGt']
        return num_dets/tot_gt

    def perf(self, thresh, dataset=None):
        dataset = self._check_dataset(dataset)
        
        tot_dets = 0
        tot_gt = 0
        num_dets = 0
        for d in dataset:
            con = self.data[d]['perf']['Contacts']
            con = [x for x in con if x['Conf'] > thresh]
            tot_gt += self.data[d]['perf']['TotalGt']
            tot_dets += len(con)
            num_dets += len([x for x in con if x['Gt']])
        # print('Total GT: '+str(tot_gt))
        return {'TP': num_dets/tot_gt, 'FP': tot_dets - num_dets}

    def display_perf(self, thresh, dataset=None, per_dataset=None):
        if not per_dataset:
            per_dataset = False

        info = self.perf(thresh, dataset)
        print('                  PDPC    FA')
        print('----------------------------')
        print('Overall      {: 2.2f} {: 5d}'.format(
            info['TP'] * 100, info['FP']))
        if per_dataset:
            for dset in self.datasets:
                info = self.perf(thresh, dset)
                print('{} {: 2.2f} {: 5d}'.format(
                    dset.ljust(38), info['TP'] * 100, info['FP']
                ))
        return

    def display_roc(self, dataset=None, title=None, x_unit=None):
        pdpc, fa, thresh, info = self.roc_curve(dataset)
        if not x_unit:
            x_unit = 'percent'

        if x_unit == 'image':
            stats = self.mission_stats(dataset)
            fa = [x*info['ntar']/stats['num_images'] for x in fa]
        elif x_unit == 'nm2':
            stats = self.mission_stats(dataset)
            fa = [x*info['ntar']/stats['mission_area']/4 for x in fa]

        plt.clf()
        plt.plot(fa, pdpc)
        plt.ylabel('PdPc (%)')
        if x_unit == 'image':
            plt.xlabel('False Alarms (per image)')
        elif x_unit == 'nm2':
            plt.xlabel('False Alarms (per nm^2)')
        else:
            plt.xlabel('False Alarms (percent)')
        if title:
            plt.title(title)
        plt.ylim([0, 1])
        plt.xlim([0, fa[-1]])
        plt.grid(True)

    def add_datasets(self, folder):
        parts = folder.split(os.sep)
        self.atrcfg = parts[-1]
        self.report_datetime = parts[-2]

        folders = [
            f for f in os.listdir(folder) if (
                (not f[0] == '.') and isdir(join(folder, f))
            )
        ]
        datanames = []

        for d in folders:
            try:
                js = _load_json(join(folder, d, 'perf_report.json'))
            except FileNotFoundError:
                print('!! Missing perf_report file for {}'.format(d))
                continue

            info = {
                'name': d,
                'location': folder,
                'perf': js
            }
            if info['perf']['TotalGt'] == 0:
                print('!! Empty GT for {}. Skipping dataset.'.format(d))
                continue
            self.data[d] = info
            datanames.append(d)

        if self.datasets:
            self.datasets.extend(datanames)
        else:
            self.datasets = datanames
        self.datasets = sorted(self.datasets)

    def generate(self):
        doc = LatexDoc()
        doc.save_location = self._save_location
        doc.add_package('inputenc', 'utf8')
        doc.add_package('graphicx')
        doc.add_package('booktabs')
        doc.add_package('fullpage')
        doc.add_package('multicol')

        # Information about data in report
        print("Collecting mission information...")
        doc.add_section('Report Contents')
        doc.add(f'ATR Configuration: {self.atrcfg}\\newline\n')
        doc.add(f'Report Date/Time: {self.report_datetime}\n')

        total_images = 0
        mission_stats = []
        items = []
        for dn in self.datasets:
            print(dn)
            stats = self.mission_stats(dn)
            total_images += stats['num_images']
            mission_stats.append(stats)
            line = (
                '{{\\bf {}}}\\newline\n'
                'Duration - ${:.4}$hrs, '
                'Area - ${:.4}$nm2, '
                'Images - {}\n'.format(
                    dn,
                    stats['mission_time']/60,
                    stats['mission_area'],
                    stats['num_images']
                )
            )
            items.append(line)
        doc.add_itemize(items)

        # Overall performance
        print("Calculating overall performance...")
        doc.add('\\pagebreak\n')
        doc.add_section('Overall Performance')

        # doc.generate('perf_report.tex')
        det_info = self.detection_stats()
        pt = self.processing_time()

        total_pdpc, total_fa, total_thres, total_con = self.roc_curve()
        fa = [x*total_con['ntar']/total_images for x in total_fa]

        doc.add('\\begin{multicols}{2}\n \\noindent ')
        doc.add((
            'Total processing time: ${:.4}$hrs\\newline\n'
            'Mean processing time (per file): ${:.4}$s\\newline\n'
            'Number of groundtruth targets: {}\\newline\n'
            'Probability of detection: {}\\newline\n'
            'Number of undetected groundtruth targets: {}\\newline\n'
            'Number of targets: {}\\newline\n'
            'Number of non-targets: {}\\newline\n'
        ).format(
            pt[0]/60.0/60.0, pt[1], det_info['TotalGt'],
            det_info['Pd'], det_info['MissedGt'], total_con['tar'],
            total_con['ntar']))
        doc.add('\\columnbreak')
        doc.add_roc_table(total_pdpc, fa, total_thres)
        doc.add('\\end{multicols}\n')

        fig_name = self.atrcfg+'-overall-roc.png'
        doc.add_roc_plot(total_pdpc, fa, fig_name, 'Overall Performance')

        # Preformance on each dataset
        for mission in mission_stats:
            dn = mission['name'][0]
            print(mission)
            print("Calculating "+dn+" performance...")
            doc.pagebreak()
            doc.add_section(dn)

            det_info = self.detection_stats(dn)
            pt = self.processing_time(dn)
            pdpc, fa, thres, con = self.roc_curve(dn)
            fa = [x*con['ntar']/mission['num_images'] for x in fa]

            doc.add('\\begin{multicols}{2}\n \\noindent ')
            doc.add((
                'Total processing time: ${:.4}$hrs\\newline\n'
                'Mean processing time (per file): ${:.4}$s\\newline\n'
                'Number of groundtruth targets: {}\\newline\n'
                'Probability of detection: {}\\newline\n'
                'Number of undetected groundtruth targets: {}\\newline\n'
                'Number of targets: {}\\newline\n'
                'Number of non-targets: {}\\newline\n'
            ).format(
                pt[0]/60.0/60.0, pt[1], det_info['TotalGt'], det_info['Pd'],
                det_info['MissedGt'], con['tar'], con['ntar']
            ))
            doc.add('\\columnbreak')
            doc.add_roc_table(pdpc, fa, thres)
            doc.add('\\end{multicols}\n')

            fig_name = self.atrcfg+'-'+dn+'-roc.png'
            doc.add_roc_plot(pdpc, fa, fig_name, dn)

        # Finalize Latex document
        doc.generate(self.filename)
