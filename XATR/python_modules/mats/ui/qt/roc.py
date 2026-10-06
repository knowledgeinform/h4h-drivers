import os
import numpy as np
import matplotlib.pyplot as plt
import sklearn.metrics

from PyQt5.QtWidgets import (QWidget, QGridLayout, QGroupBox, QLabel)
from PyQt5.QtWidgets import (QVBoxLayout, QComboBox, QPushButton, QCheckBox)
from PyQt5.QtWidgets import (QScrollArea, QHBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from mats.ui.qt.common import (DirDialog, ARCHIVE_ROOT)

from mats.core import load_json


class ROCPopup(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.kod = []

        self.mainwidget = parent
        self.initUI()

    def initUI(self):
        grid = QGridLayout()

        grid.addWidget(self.create_config_group(), 0, 0)
        grid.addWidget(self.create_dir_group(), 1, 0)
        grid.addLayout(self.create_plot_group(), 2, 0)

        self.setLayout(grid)

        self.setGeometry(300, 300, 400, 600)

        self.setWindowTitle('ROC')
        self.show()

    def create_config_group(self):
        groupBox = QGroupBox('Configuration')

        vbox = QVBoxLayout()
        grid = QGridLayout()

        self.score_type_label = QLabel('Score Type')
        self.graph_type_label = QLabel('Graph Type')
        self.class_units_label = QLabel('Class. Units')

        self.score_type_dropdown = QComboBox(self)
        self.graph_type_dropdown = QComboBox(self)
        self.class_units_dropdown = QComboBox(self)

        self.score_type_dropdown.addItems(
            ['Classifier Confidence', 'Detector Confidence'])
        self.graph_type_dropdown.addItems(['Final ROC'])
        self.class_units_dropdown.addItems(
            ['Percentage', 'False alarms/image'])

        self.add_dir_button = QPushButton('Add Directories')

        self.compare_batch_checkbox = QCheckBox('Compare Batch')

        grid.addWidget(self.score_type_label, 0, 0)
        grid.addWidget(self.graph_type_label, 1, 0)
        grid.addWidget(self.class_units_label, 2, 0)

        grid.addWidget(self.score_type_dropdown, 0, 1)
        grid.addWidget(self.graph_type_dropdown, 1, 1)
        grid.addWidget(self.class_units_dropdown, 2, 1)
        grid.addWidget(self.compare_batch_checkbox, 3, 1)

        vbox.addLayout(grid)
        vbox.addWidget(self.add_dir_button)

        # self.add_button.setObjectName('Add Button')
        # self.remove_button.setObjectName('Remove Button')

        self.add_dir_button.clicked.connect(self.add_dirs)
        # self.remove_button.clicked.connect(self.remove_all_widgets)
        # self.check_all_button.clicked.connect(self.check_all_gts)

        groupBox.setLayout(vbox)

        return groupBox

    def create_dir_group(self):
        self.scrollLayout = QVBoxLayout()
        self.scrollLayout.addStretch(1)
        self.scrollLayout.setAlignment(Qt.AlignTop)

        # scroll area widget contents
        self.scrollWidget = QGroupBox('Included Directories')
        self.scrollWidget.setLayout(self.scrollLayout)

        # scroll area
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollWidget)

        return self.scrollArea

    def create_plot_group(self):
        hbox = QHBoxLayout()

        self.remove_button = QPushButton('Remove Checked')
        self.plot_button = QPushButton('Plot Checked')

        self.remove_button.clicked.connect(self.remove_checked_widgets)
        self.plot_button.clicked.connect(self.plot_checked_widgets)

        hbox.addWidget(self.remove_button)
        hbox.addWidget(self.plot_button)

        return hbox

    def add_dirs(self):
        dir_list = ''
        dir_dialog = DirDialog(self, 'Select directory', ARCHIVE_ROOT)
        if dir_dialog.exec_():
            dir_list = dir_dialog.get_dirlist()

        if dir_list != '':
            # print(dir_list)
            for d in dir_list:
                self.add_widget(d, True)

    def add_widget(self, arc_dir, checkbox_setting):
        # define buttons
        dir_label = QLabel()
        dir_checkbox = QCheckBox()

        # set button font sizes
        tmp_font = QFont()
        tmp_font.setPointSize(8)
        dir_label.setFont(tmp_font)

        self.kod.append([dir_label, dir_checkbox])

        dir_label.setProperty('arc_dir', arc_dir)
        # dir_label = self.format_button_dirtext(io_settings[0])
        dir_label.setText(arc_dir)
        dir_checkbox.setChecked(checkbox_setting)

        self.hbox = QHBoxLayout()
        self.hbox.addWidget(dir_checkbox, stretch=0)
        self.hbox.addWidget(dir_label, stretch=1)

        self.scrollLayout.insertLayout(0, self.hbox)

    def remove_checked_widgets(self):
        for idx, buttons in reversed(list(enumerate(self.kod))):
            dir_checkbox = buttons[1]

            if dir_checkbox.isChecked() is True:
                ws = self.kod.pop(idx)
                for widget in ws:
                    widget.deleteLater()

    def plot_checked_widgets(self):
        dirs_to_plot = []

        for buttons in self.kod:
            dir_label = buttons[0]
            dir_checkbox = buttons[1]

            if dir_checkbox.isChecked() is True:
                dirs_to_plot.append(dir_label.property('arc_dir'))

        print(dirs_to_plot)

        if self.compare_batch_checkbox.isChecked() is False:
            self.plot_rocs(dirs_to_plot)
        else:
            self.plot_batch_rocs(dirs_to_plot)

    def plot_rocs(self, dirs_to_plot):
        legend = []
        plt.figure()
        for arc_dir in dirs_to_plot:
            stats = load_json(os.path.join(arc_dir, 'perf_report.json'))
            gt = np.array([x['Gt'] for x in stats['Contacts']])
            det_conf = np.array([x['Detscore'] for x in stats['Contacts']])
            cls_conf = np.array([x['Conf'] for x in stats['Contacts']])

            score_type = self.score_type_dropdown.currentText()
            if score_type == 'Detector Confidence':
                title = 'Detector ROC'
                conf = det_conf
            elif score_type == 'Classifier Confidence':
                title = 'Classifier ROC'
                conf = cls_conf

            fpr, tpr, _ = sklearn.metrics.roc_curve(gt, conf)

            # this is required because contacts for missed targets are not
            # included in contact list
            max_tpr = stats['Detector']['Pd']
            tpr *= max_tpr

            xlabel = 'FPR'
            ylabel = 'TPR'

            # rescale FPR
            if self.class_units_dropdown.currentText() == 'False alarms/image':
                fpr = fpr * np.sum(gt == 0) / stats['NumberFiles']
                xlabel = 'False alarms/image'

            print('plotting')
            plt.plot(fpr, tpr)

            legend += [self.format_dirtext(arc_dir)]

        plt.title(title)
        plt.legend(legend)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid('on')

        plt.show()

    def plot_batch_rocs(self, dirs_to_plot):
        curves_dict = {}

        for dir_name in dirs_to_plot:
            for root, _, filelist in os.walk(dir_name, topdown=False):
                for fname in filelist:
                    if fname == 'perf_report.json':
                        dataset_name = os.path.split(root)[1]
                        root_name = os.path.split(os.path.split(root)[0])[1]
                        fullpath = root + '/' + fname

                        stats = load_json(fullpath)
                        gt = np.array([x['Gt'] for x in stats['Contacts']])
                        det_conf = np.array(
                            [x['Detscore'] for x in stats['Contacts']])
                        cls_conf = np.array(
                            [x['Conf'] for x in stats['Contacts']])

                        score_type = self.score_type_dropdown.currentText()
                        if score_type == 'Detector Confidence':
                            title = 'Detector ROC'
                            conf = det_conf
                        elif score_type == 'Classifier Confidence':
                            title = 'Classifier ROC'
                            conf = cls_conf

                        fpr, tpr, _ = sklearn.metrics.roc_curve(gt, conf)

                        # this is required because contacts for missed targets
                        # are not included in contact list
                        max_tpr = stats['Detector']['Pd']
                        tpr *= max_tpr

                        xlabel = 'FPR'
                        ylabel = 'TPR'

                        # rescale FPR
                        class_units = self.class_units_dropdown.currentText()
                        if class_units == 'False alarms/image':
                            fpr = fpr * np.sum(gt == 0) / stats['NumberFiles']
                            xlabel = 'False alarms/image'

                        if root_name not in curves_dict:
                            curves_dict[root_name] = {}

                        curves_dict[root_name][dataset_name] = [fpr, tpr, root]

        legend = []
        line_types = ['-', '--', '-.', ':']

        plt.figure()
        for ii, root_key in enumerate(curves_dict):
            plt.gca().set_color_cycle(None)
            line_type = line_types[ii % 4]
            for data_key in curves_dict[root_key]:
                fpr, tpr, rootpath = curves_dict[root_key][data_key]
                legend += [self.format_dirtext(rootpath)]

                plt.plot(fpr, tpr, line_type)
        plt.title(title)
        plt.legend(legend)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid('on')
        plt.show()

    def format_dirtext(self, dirtext):
        formatted_text = '.../' + os.path.relpath(dirtext, dirtext + '/../..')
        return formatted_text
