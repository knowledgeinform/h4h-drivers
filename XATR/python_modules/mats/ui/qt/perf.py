import os
try:
    import tabulate
    TABULATE = True
except ModuleNotFoundError:
    TABULATE = False
import pandas as pd

from PyQt5.QtWidgets import (
    QMenuBar, QGridLayout, QGroupBox, QPushButton, QLabel, QHBoxLayout,
    QVBoxLayout, QWidget, QScrollArea, QCheckBox, QComboBox)
from PyQt5.QtGui import (QFont)
from mats.ui.qt.common import (ATRDoubleSpinBox, DirDialog, ARCHIVE_ROOT)

from mats.core import load_json


class PerfReportComparePopup(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.mainwidget = parent
        self.kod2 = []
        self.initUI()

    def initUI(self):
        self.menubar = QMenuBar(self)

        grid = QGridLayout()

        grid.addWidget(self.create_create_group(), 0, 0)
        grid.addLayout(self.create_file_group(), 1, 0)
        grid.addLayout(self.create_control_group(), 2, 0)
        grid.addWidget(self.create_start_widget(), 3, 0)
        # grid.setRowStretch(4, 1)

        self.setLayout(grid)

        self.setGeometry(300, 300, 400, 600)
        self.setWindowTitle('Compare perf report')
        self.show()

    def create_create_group(self):
        groupBox = QGroupBox('')
        grid = QGridLayout()

        self.thresh_spinbox = ATRDoubleSpinBox()
        self.thresh_spinbox.setMaximum(1)
        self.thresh_spinbox.setDecimals(10)
        self.thresh_spinbox.setSingleStep(0.01)
        self.thresh_spinbox.setValue(0.5)

        self.gen_perf_button = QPushButton('Create Perf Reports')
        self.gen_perf_button.pressed.connect(self.gen_perf)

        grid.addWidget(QLabel('Class Thresh'), 0, 0)
        grid.addWidget(self.thresh_spinbox, 0, 1)
        grid.addWidget(self.gen_perf_button, 1, 0, 1, 2)

        groupBox.setLayout(grid)
        return groupBox

    def create_file_group(self):
        add_archive_dir_button = QPushButton('Add Archive Dir')
        remove_archive_dir_button = QPushButton('Remove Archive Dir')

        add_archive_dir_button.pressed.connect(self.add_dirs)
        remove_archive_dir_button.pressed.connect(self.remove_checked_dirs)

        header_hbox = QHBoxLayout()
        header_hbox.addWidget(add_archive_dir_button)
        header_hbox.addWidget(remove_archive_dir_button)

        # header_hbox.setContentsMargins(5, 11, 0, 0)

        self.scrollLayout2 = QVBoxLayout()
        self.scrollLayout2.addStretch(1)
        self.scrollLayout2.setSpacing(0)

        # scroll area widget contents
        scrollWidget = QWidget()
        scrollWidget.setLayout(self.scrollLayout2)

        # scroll area
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(scrollWidget)

        outer_vbox = QVBoxLayout()
        outer_vbox.addLayout(header_hbox)
        outer_vbox.addWidget(scrollArea)
        outer_vbox.setSpacing(0)

        # return self.scrollArea
        return outer_vbox

    def create_control_group(self):
        grid = QGridLayout()

        self.value_dropdown = QComboBox()
        self.value_dropdown.addItems(
            ['Pd', 'Pd+Gt', 'Pc', 'Pc+Gt', 'PdPc', 'Det. FA', 'Cls. FA'])
        # value_dropdown.currentIndexChanged[str].connect(self.)

        grid.addWidget(QLabel('Value to compare'), 0, 0)
        grid.addWidget(self.value_dropdown, 0, 1)

        return grid

    def create_start_widget(self):
        self.startButton = QPushButton("Plot")

        self.startButton.clicked.connect(self.start_button_clicked)

        hbox = QHBoxLayout()

        hbox.addWidget(self.startButton)

        start_widget = QWidget(self)
        start_widget.setLayout(hbox)

        return start_widget

    def gen_perf(self):
        root_dir_names = []
        dir_names = []

        for buttons in self.kod2:
            root_dir_names.append(buttons[0].property('file_name'))

        for root_dir_name in root_dir_names:
            dir_names += [x[0] for x in os.walk(root_dir_name)]

        thresh_value = self.thresh_spinbox.value()
        for out_dir in dir_names:
            command = '$XATR_ROOT/bin/mats_perf_report -t ' + str(thresh_value) + ' ' + out_dir
            print(command)
            os.system(command)
            print('Generated Perf Report ' + out_dir)

    def add_dirs(self):
        dir_list = ''
        dir_dialog = DirDialog(self, 'Select directory', ARCHIVE_ROOT)
        if dir_dialog.exec_():
            dir_list = dir_dialog.get_dirlist()

        if dir_list != '':
            # print(dir_list)
            for d in dir_list:
                self.add_dir_widget(d, True)

    def remove_checked_dirs(self):
        for idx, buttons in reversed(list(enumerate(self.kod2))):
            dir_checkbox = buttons[1]

            if dir_checkbox.isChecked() is True:
                ws = self.kod2.pop(idx)
                for widget in ws:
                    widget.deleteLater()

    def add_dir_widget(self, file_name, checkbox_setting):
        # define buttons
        file_label = QLabel(file_name)
        file_checkbox = QCheckBox()

        # set button font sizes
        tmp_font = QFont()
        tmp_font.setPointSize(8)
        file_label.setFont(tmp_font)

        self.kod2.append([file_label, file_checkbox])

        file_label.setProperty('file_name', file_name)
        # dir_label = self.format_button_dirtext(io_settings[0])
        file_label.setText(file_name)
        file_checkbox.setChecked(checkbox_setting)

        self.hbox = QHBoxLayout()
        self.hbox.addWidget(file_checkbox, stretch=0)
        self.hbox.addWidget(file_label, stretch=1)
        self.hbox.setSpacing(7)

        self.scrollLayout2.insertLayout(0, self.hbox)

    def start_button_clicked(self):
        dir_names = []

        table_dict = {}

        for buttons in self.kod2:
            dir_names.append(buttons[0].property('file_name'))

        self.selected_stat = self.value_dropdown.currentText()

        for dir_name in dir_names:
            for root, _, filelist in os.walk(dir_name, topdown=False):
                for fname in filelist:
                    if fname == 'perf_report.json':
                        dataset_name = os.path.split(root)[1]
                        root_name = os.path.split(os.path.split(root)[0])[1]
                        fullpath = root + '/' + fname

                        stats = load_json(fullpath)

                        total_gt = stats['TotalGt']

                        Pd = stats['Detector']['Pd']
                        det_missed = stats['Detector']['NumberMissedTargets']

                        Pc = stats['Classifier']['Pc']
                        cls_missed = stats['Classifier']['NumberMissedTargets']

                        if self.selected_stat == 'Pd':
                            table_stat = Pd
                        elif self.selected_stat == 'Pd+Gt':
                            Pdstr = '%.5f' % Pd
                            Pdstr += f'  ({(total_gt - det_missed)}/{total_gt})'
                            table_stat = Pdstr
                        elif self.selected_stat == 'Pc':
                            table_stat = Pc
                        elif self.selected_stat == 'Pc+Gt':
                            Pcstr = '%.5f' % Pc
                            Pcstr += f'  ({(total_gt - det_missed - cls_missed)}/{total_gt - det_missed})'
                            table_stat = Pcstr
                        elif self.selected_stat == 'PdPc':
                            table_stat = stats['PdPc']
                        elif self.selected_stat == 'Det. FA':
                            table_stat = stats['Detector']['FalseAlarms']
                        elif self.selected_stat == 'Cls. FA':
                            table_stat = stats['Classifier']['FalseAlarms']

                        if root_name not in table_dict:
                            table_dict[root_name] = {}

                        table_dict[root_name][dataset_name] = table_stat

        self.print_table(table_dict)

    def print_table(self, table_dict):
        print('')
        print(f'*** {self.selected_stat} ***')
        df = pd.DataFrame(table_dict)
        df.fillna(0, inplace=True)
        # print(df)
        if TABULATE:
            print(tabulate(df, headers='keys', tablefmt='psql'))
        else:
            print('<< MISSING Python tabulate module >>')
