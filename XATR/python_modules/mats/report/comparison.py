import os
from mats.report import ConfigReport
from mats.report import _latex_sanitize
from mats.report.latex import LatexDoc
import matplotlib.pyplot as plt


class ComparisonReport:
    def __init__(self):
        self.filename = 'CompReport.tex'
        self.save_location = '.'
        self.datasets = None
        self.cfg = {}
        self.data = {}

    def _check_dataset(self, dataset):
        if not dataset:
            dataset = self.datasets
        elif isinstance(dataset, str):
            dataset = [dataset]
        return dataset

    def _update_datasets(self):
        for cfg_name in self.cfg:
            cfg = self.cfg[cfg_name]

            if not self.datasets:
                self.datasets = cfg.datasets
                for dn in self.datasets:
                    self.data[dn] = cfg.mission_stats(dn)
                continue
            new_datasets = []
            for dn in cfg.datasets:
                if dn not in self.datasets:
                    print(" !! Missing {} for other configuration.".format(dn))
                    continue
                stats = cfg.mission_stats(dn)
                if not self.data[dn]['num_images'] == stats['num_images']:
                    print(" !! Differing number of images for {}.".format(dn))
                    continue
                new_datasets.append(dn)
            self.datasets = new_datasets

    def _report_info(self, cfg_name, datasets=None):
        if not datasets:
            datasets = self.datasets
        if isinstance(datasets, str):
            datasets = [datasets]

        det = self.cfg[cfg_name].detection_stats(datasets)
        pt = self.cfg[cfg_name].processing_time(datasets)

        total_images = 0
        for dn in datasets:
            total_images += self.data[dn]['num_images']

        pdpc, fa, thres, con = self.cfg[cfg_name].roc_curve(datasets)
        fa_img = [x*con['ntar']/total_images for x in fa]

        out = {}
        out['total_process_time'] = pt[0]/60.0/60.0
        out['time_per_image'] = pt[1]
        out['num_gt'] = det['TotalGt']
        out['missed_gt'] = det['MissedGt']
        out['pd'] = det['Pd']
        out['num_targets'] = con['tar']
        out['num_ntargets'] = con['ntar']

        out['roc'] = {}
        out['roc']['pdpc'] = pdpc
        out['roc']['fa'] = fa
        out['roc']['fa_img'] = fa_img
        out['roc']['thres'] = thres
        # print(out)

        return out

    def perf(self, thresh, dataset=None):
        dataset = self._check_dataset(dataset)

        info = {}
        
        if isinstance(thresh, list):
            if not len(thresh) == len(self.cfg):
                raise ValueError('Length of thresh must equal number of cfg.')
            for cfgname in enumerate(self.cfg):
                t = thresh[cfgname[0]]
                info[cfgname[1]] = self.cfg[cfgname[1]].perf(t, dataset)
        else:
            for cfgname in self.cfg:
                info[cfgname] = self.cfg[cfgname].perf(thresh, dataset)
        return info

    def roc_curve(self, dataset=None, x_unit=None):
        dataset = self._check_dataset(dataset)

        if not x_unit:
            x_unit = 'percent'

        data = {}
        for cname in self.cfg:
            cfg = self.cfg[cname]
            pdpc, fa, thresh, info = cfg.roc_curve(dataset)

            if x_unit == 'image':
                stats = cfg.mission_stats(dataset)
                fa = [x*info['ntar']/stats['num_images'] for x in fa]
            elif x_unit == 'nm2':
                stats = cfg.mission_stats(dataset)
                fa = [x*info['ntar']/stats['mission_area']/4 for x in fa]

            data[cfg.atrcfg] = {
                'Name': cname,
                'PdPc': pdpc,
                'FA': fa,
                'Threshold': thresh
            }
        return data

    def display_perf(self, thresh, dataset=None, per_dataset=None):
        if not per_dataset:
            per_dataset = False
        
        info = self.perf(thresh, dataset)
        print('Configuration                            PDPC    FA')
        print('---------------------------------------------------')
        if per_dataset:
            print('Overall')
        for cfg in info:
            print('  {} {: 2.2f} {: 5d}'.format(
                cfg.ljust(38), info[cfg]['TP']*100, info[cfg]['FP']
            ))
        
        if per_dataset:
            for dset in self.datasets:
                info = self.perf(thresh, dset)
                print('{}'.format(dset))
                for cfg in info:
                    print('  {} {: 2.2f} {: 5d}'.format(
                        cfg.ljust(38), info[cfg]['TP']*100, info[cfg]['FP']
                    ))

    def display_roc(self, dataset=None, title=None, x_unit=None):
        if not x_unit:
            x_unit = 'percent'
        info = self.roc_curve(dataset, x_unit)

        plt.clf()
        for cname in info:
            plt.plot(info[cname]['FA'], info[cname]['PdPc'], label=cname)

        plt.ylabel('PdPc (%)')
        if x_unit == 'image':
            plt.xlabel('False Alarms (per image)')
        elif x_unit == 'nm2':
            plt.xlabel('False Alarms (per nm^2)')
        else:
            plt.xlabel('False Alarms (percent)')
        if title:
            plt.title(title)
        #plt.ylim([0, 1])
        #plt.xlim([0, fa[-1]])
        plt.grid(True)
        plt.legend()
    
    def display_fac(self, dataset=None, title=None, y_unit=None):
        if not y_unit:
            y_unit = 'percent'
        info = self.roc_curve(dataset, y_unit)

        plt.clf()
        for cname in info:
            plt.plot(info[cname]['Threshold'], info[cname]['FA'], label=cname)

        plt.xlabel('Threshold')
        if y_unit == 'image':
            plt.ylabel('False Alarms (per image)')
        elif y_unit == 'nm2':
            plt.ylabel('False Alarms (per nm^2)')
        else:
            plt.ylabel('False Alarms (percent)')
        if title:
            plt.title(title)
        #plt.ylim([0, 1])
        plt.xlim([0, 1])
        plt.grid(True)
        plt.legend()
    
    def display_poc(self, dataset=None, title=None):
        info = self.roc_curve(dataset)

        plt.clf()
        for cname in info:
            plt.plot(info[cname]['Threshold'], info[cname]['PdPc'], label=cname)

        plt.xlabel('Threshold')
        plt.ylabel('PdPc (%)')
        if title:
            plt.title(title)
        plt.ylim([0, 1])
        plt.xlim([0, 1])
        plt.grid(True)
        plt.legend()

    def add_config_folder(self, folder):
        parts = folder.split(os.sep)
        cfg_name = parts[-1]

        self.cfg[cfg_name] = ConfigReport()
        self.cfg[cfg_name].add_datasets(folder)
        print(f'Adding config: {cfg_name}')
        self._update_datasets()

    def generate(self):
        doc = LatexDoc()
        doc.save_location = self.save_location
        doc.add_package('inputenc', 'utf8')
        doc.add_package('graphicx')
        doc.add_package('booktabs')
        doc.add_package('fullpage')
        doc.add_package('multicol')

        print("Collecting mission information...")
        doc.add_section('Report Contents')
        for cfg_name in self.cfg:
            atrcfg = self.cfg[cfg_name].atrcfg
            report_datetime = self.cfg[cfg_name].report_datetime
            print('  '+atrcfg)
            doc.add('ATR Configuration 1: {0} ({1})\\newline\n'.format(
                atrcfg, report_datetime
            ))

        # Report Mission information
        total_images = 0
        items = []
        for dn in self.datasets:
            # print(dn)
            stats = self.data[dn]
            total_images += stats['num_images']

            line = (
                '{{\\bf {}}}\\newline\n'
                'Duration - ${:.4}$hrs, '
                'Area - ${:.4}$nm2, '
                'Images - {}\n'.format(
                    _latex_sanitize(dn),
                    stats['mission_time']/60,
                    stats['mission_area'],
                    stats['num_images']
                )
            )
            items.append(line)
        doc.add_itemize(items)

        # Overall performance
        print("Calculating overall performance...")
        doc.pagebreak()
        doc.add_section('Overall Performance')
        info = []
        for cfg_name in self.cfg:
            info.append(self._report_info(cfg_name))

        doc.add((
            '\\begin{{multicols}}{{2}}\n \\noindent '
            '\\noindent \\begin{{tabular}}{{lcc}}\n'
            '     & Config 1 & Config 2 \\\\\n'
            '\\toprule\n'
            'Processing time & ${:.4}$hrs & ${:.4}$hrs \\\\\n'
            'Processing time (per file) & ${:.4}$s & ${:.4}$s \\\\\n'
            'Probability of detection & {:.4} & {:.4} \\\\\n'
            'Groundtruth targets & {} & {} \\\\\n'
            'Undetected groundtruth & {} & {} \\\\\n'
            'Number of targets & {} & {} \\\\\n'
            'Number of non-targets & {} & {} \\\\\n'
            '\\end{{tabular}}\n'
            '\\columnbreak'
            '\\noindent'
        ).format(
            info[0]['total_process_time'], info[1]['total_process_time'],
            info[0]['time_per_image'], info[1]['time_per_image'],
            info[0]['pd'], info[1]['pd'],
            info[0]['num_gt'], info[1]['num_gt'],
            info[0]['missed_gt'], info[1]['missed_gt'],
            info[0]['num_targets'], info[1]['num_targets'],
            info[0]['num_ntargets'], info[1]['num_ntargets']
        ))
        #doc.add_comp_roc_table([info[0]['roc'], info[1]['roc']])
        doc.add_comp_roc_table(self.cfg, self.roc_curve(x_unit='nm2'))
        doc.add('\\end{multicols}\n')

        fig_name = ''
        for cfg_name in self.cfg:
            fig_name += cfg_name+'-'
        fig_name += 'overall-roc.png'
        doc.add_comp_roc_plot(
            [info[0]['roc'], info[1]['roc']], fig_name, 'Overall Performance')

        # Preformance on each dataset
        for dn in self.datasets:
            print("Calculating "+dn+" performance...")
            info = []
            for cfg_name in self.cfg:
                info.append(self._report_info(cfg_name, dn))

            doc.pagebreak()
            doc.add_section(_latex_sanitize(dn))

            doc.add((
                '\\begin{{multicols}}{{2}}\n'
                '\\noindent \\begin{{tabular}}{{lcc}}\n'
                '     & Config 1 & Config 2 \\\\\n'
                '\\toprule\n'
                'Processing time & ${:.4}$hrs & ${:.4}$hrs \\\\\n'
                'Processing time (per file) & ${:.4}$s & ${:.4}$s \\\\\n'
                'Probability of detection & {:.4} & {:.4} \\\\\n'
                'Groundtruth targets & {} & {} \\\\\n'
                'Undetected groundtruth & {} & {} \\\\\n'
                'Number of targets & {} & {} \\\\\n'
                'Number of non-targets & {} & {} \\\\\n'
                '\\end{{tabular}}\n'
                '\\columnbreak'
                '\\noindent'
            ).format(
                info[0]['total_process_time'], info[1]['total_process_time'],
                info[0]['time_per_image'], info[1]['time_per_image'],
                info[0]['pd'], info[1]['pd'],
                info[0]['num_gt'], info[1]['num_gt'],
                info[0]['missed_gt'], info[1]['missed_gt'],
                info[0]['num_targets'], info[1]['num_targets'],
                info[0]['num_ntargets'], info[1]['num_ntargets']
            ))
            doc.add_comp_roc_table(self.cfg, self.roc_curve(dn, x_unit='nm2'))
            doc.add('\\end{multicols}\n')

            fig_name = ''
            for cfg_name in self.cfg:
                fig_name += cfg_name+'-'
            fig_name += dn+'-roc.png'
            doc.add_comp_roc_plot(
                [info[0]['roc'], info[1]['roc']], fig_name, dn)

        # Finalize Latex document
        doc.generate(self.filename)
