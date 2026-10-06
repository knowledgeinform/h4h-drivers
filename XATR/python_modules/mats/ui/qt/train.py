# -*- coding: utf-8 -*-
"""
Created on Wed Jul 18 16:31:26 2018

@author: ONR_NSWCPCD_COIN
"""

import os
import pickle

from PyQt5.QtWidgets import (
    QMainWindow, QAction, QFileDialog, QLabel, QGridLayout, QStackedWidget,
    QComboBox, QGroupBox, QWidget, QPushButton, QHBoxLayout, QVBoxLayout,
    QMenuBar, QScrollArea, QCheckBox, QLineEdit)
from PyQt5.QtGui import (QIcon, QFont)
from PyQt5.QtCore import (QDir, QThread, pyqtSlot, pyqtSignal)

from matsui.qt.common import (DirDialog, Keys)

class TrainMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Initialize components
        self.initUI()

    def initUI(self):
        self.mainwidget = TrainMainWidget(self)
        self.setCentralWidget(self.mainwidget)

        self.setWindowTitle('XATR Training GUI')
        self.show()
        
class TrainMainWidget(QWidget):
    # Popup that allows selection of multiple input datasets
    def __init__(self, parent):
        super().__init__()

        self.mainwidget = parent

        self.kod = []
        self.io_list = []

        self.initUI()

    def initUI(self):
        self.menubar = QMenuBar(self)

#        # Save and Load
#        config_menu = self.menubar.addMenu('&Config')
#        save_config_action = QAction('Save Config', self)
#        load_config_action = QAction('Load Config', self)
#        save_config_action.triggered.connect(self.save_config)
#        load_config_action.triggered.connect(self.load_config)
#        config_menu.addAction(load_config_action)
#        config_menu.addAction(save_config_action)
#
#        # Debug
#        debug_menu = self.menubar.addMenu('&Debug')
#        print_sources_action = QAction('Print Sources', self)
#        print_sources_action.triggered.connect(self.print_sources)
#        debug_menu.addAction(print_sources_action)

        grid = QGridLayout()
        
        add_button = QPushButton('Add Archive Directories')
        add_button.clicked.connect(self.add_dirs)

        applyButton = QPushButton("Apply")
        applyButton.clicked.connect(self.press_apply)
        
        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.press_cancel)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(cancelButton)
        hbox.addWidget(applyButton)

        grid.addWidget(self.menubar, 0, 0)
        grid.addWidget(self.create_params_group(), 1, 0)
        grid.addWidget(add_button, 2, 0)
        grid.addWidget(self.create_source_group(), 3, 0)
        grid.addLayout(hbox, 4, 0)

        self.setLayout(grid)

        self.setGeometry(300, 300, 1250, 675)

        self.setWindowTitle('Batch Input')
        self.show()

        print('end initUI')

#    def save_config(self):
#        fname = QFileDialog.getSaveFileName(
#            self, 'Save Batch Config File', os.getcwd(), '*.batchcfg')[0]
#
#        # if statement handles 'cancel'
#        if fname != '':
#
#            self.remove_blank_widgets()
#
#            if os.path.splitext(fname)[1] != '.batchcfg':
#                fname += '.batchcfg'
#
#            print(fname)
#            pickle.dump(self.io_list, open(fname, 'wb'))
#
#    def load_config(self):
#        fname = QFileDialog.getOpenFileName(
#            self, 'Select ground truth file', os.getcwd(), '*.batchcfg')[0]
#
#        # if statement handles 'cancel'
#        if fname != '':
#            self.reset_widgets()
#            tmp_io_list = pickle.load(open(fname, 'rb'))
#            for io in tmp_io_list:
#                if len(io) == 2:
#                    io += [False]
#                self.addWidget(io_settings=io)

    def print_sources(self):
        print('--------------------------------')
        for io in reversed(self.io_list):
            print(io)
        print('--------------------------------')

    def reset_widgets(self):
        for idx, io in reversed(list(enumerate(self.io_list))):
            self.io_list.pop(idx)
            ws = self.kod.pop(idx)
            for widget in ws:
                widget.deleteLater()

    def create_params_group(self):
        groupBox = QGroupBox(' Sampling Parameters')

        self.p_epoch_size = QLineEdit('asdf')
        self.p_batch_size = QLineEdit('fda')

        grid = QGridLayout()
        grid.addWidget(QLabel('Epoch size:'), 0, 0)
        grid.addWidget(self.p_epoch_size, 0, 1)
        grid.addWidget(QLabel('Batch size:'), 1, 0)
        grid.addWidget(self.p_batch_size, 1, 1)

        # self.add_button.setObjectName('Add Button')
        # self.remove_button.setObjectName('Remove Button')

#        self.add_button.clicked.connect(self.add_dirs)
#        self.remove_button.clicked.connect(self.remove_all_widgets)
#        self.check_all_button.clicked.connect(self.check_all_gts)

        groupBox.setLayout(grid)

        return groupBox

    def create_source_group(self):
        self.scrollWidget = QGroupBox('Contact Archive Directories')
        
        self.scrollLayout = QVBoxLayout()
        self.scrollLayout.addStretch(1)
        self.scrollLayout.setSpacing(0)

        self.scrollWidget.setLayout(self.scrollLayout)

        # scroll area
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollWidget)

        return self.scrollArea

    def add_dirs(self):
        dir_list = ''
        dir_dialog = DirDialog(self, 'Select directory', '/home/Data/SSAM2')
        if dir_dialog.exec_():
            dir_list = dir_dialog.get_dirlist()

        if dir_list != '':
            print(dir_list)
            for d in dir_list:
                self.addWidget(io_settings=[d, None, False])

    def addWidget(self, *args, **kwargs):
        io_settings = kwargs.get('io_settings', None)

        # define buttons
        source_button = QPushButton('Source Directory')
#        gt_button = QPushButton('Ground Truth')
        gt_only_checkbox = QCheckBox('GT only')

        x_button = QPushButton('')
        x_button.setIcon(QIcon('Button-Close-icon.png'))

        # set button font sizes
        tmp_font = QFont()
        tmp_font.setPointSize(8)
        source_button.setFont(tmp_font)
#        gt_button.setFont(tmp_font)

        # force source and gt_buttons to be the same size
        source_button.setMinimumSize(source_button.sizeHint())
#        gt_button.setMinimumSize(source_button.minimumSizeHint())
        x_button.setMaximumSize(source_button.minimumSizeHint())

        # button signals
        source_button.clicked.connect(self.source_button_clicked)
#        gt_button.clicked.connect(self.gt_button_clicked)
        gt_only_checkbox.stateChanged.connect(self.gt_checkbox_statechanged)
        x_button.clicked.connect(self.x_button_clicked)

        self.kod.append([source_button, x_button, gt_only_checkbox])
#        self.kod.append([source_button, gt_button, x_button, gt_only_checkbox])

        if io_settings is None:
            self.io_list.append([None, None, None])
        else:
            self.io_list.append(io_settings)
            source_button_text = self.format_button_dirtext(io_settings[0])
            source_button.setText(source_button_text)
#            # source_button.setStyleSheet("Text-align:left")
#            if io_settings[1] is not None:
#                gt_button_text = self.format_button_filetext(io_settings[1])
#                gt_button.setText(gt_button_text)
#                # gt_button.setStyleSheet("Text-align:left")
#            if io_settings[2] is not None:
#                gt_only_checkbox.setChecked(io_settings[2])

        self.hbox = QHBoxLayout()
        self.hbox.addWidget(x_button, stretch=0)
        self.hbox.addWidget(source_button, stretch=1)
#        self.hbox.addWidget(gt_button, stretch=1)
        self.hbox.addWidget(gt_only_checkbox, stretch=0)
        self.hbox.setSpacing(9)

        self.scrollLayout.insertLayout(0, self.hbox)

    def remove_blank_widgets(self):
        for idx, io in reversed(list(enumerate(self.io_list))):
            if io == [None, None]:
                self.io_list.pop(idx)
                ws = self.kod.pop(idx)
                for widget in ws:
                    widget.deleteLater()

    def remove_all_widgets(self):
        for idx, io in reversed(list(enumerate(self.io_list))):
            self.io_list.pop()
            ws = self.kod.pop()
            for widget in ws:
                widget.deleteLater()

    def check_all_gts(self):
        # Check or uncheck all "gt only" checkboxes
        if len(self.kod) > 0:
            # set the opposite of what most of the buttons are set to
            state_sum = 0
            for buttons in self.kod:
                check_button = buttons[3]
                state_sum += int(bool(check_button.isChecked()))

            new_state = not(bool(round(state_sum / len(self.kod))))

            for buttons in self.kod:
                check_button = buttons[3]
                check_button.setChecked(new_state)

    def gt_checkbox_statechanged(self, state):
        # Checkbox indicates whether gt only should be used for this dataset
        sender = self.sender()
        ws = [x for x in self.kod if x[3] == sender][0]
        idx = self.kod.index(ws)

        self.io_list[idx][2] = bool(state)

    def source_button_clicked(self):
        # Change dataset source directory
        sender = self.sender()
        ws = [x for x in self.kod if x[0] == sender][0]
        idx = self.kod.index(ws)

        dir_name = QFileDialog.getExistingDirectory(
            self, 'Select directory', '/home/Data/SSAM2')
        dir_name = QDir.toNativeSeparators(dir_name)
        # if cancel button not pressed
        if dir_name != '':
            button_text = self.format_button_dirtext(dir_name)
            sender.setText(button_text)
            self.io_list[idx][0] = dir_name
            # sender.setStyleSheet("Text-align:left")

    def gt_button_clicked(self):
        # Open dialog for selection of ground truth file
        sender = self.sender()

        ws = [x for x in self.kod if x[1] == sender][0]
        idx = self.kod.index(ws)

        fname = QFileDialog.getOpenFileName(
            self, 'Select ground truth file', self.io_list[idx][0])[0]
        fname = QDir.toNativeSeparators(fname)
        # print(fname)

        # if cancel button not pressed
        if fname != '':
            button_text = self.format_button_filetext(fname)
            sender.setText(button_text)
            self.io_list[idx][1] = fname
            # sender.setStyleSheet("Text-align:left")

    def x_button_clicked(self):
        # Remove row
        sender = self.sender()

        ws = [x for x in self.kod if x[2] == sender][0]
        idx = self.kod.index(ws)

        ws = self.kod.pop(idx)
        self.io_list.pop(idx)
        for widget in ws:
            widget.deleteLater()
        print(f'button index: {idx}')

    def format_button_filetext(self, filetext):
        fn = os.path.join(os.path.dirname(filetext), '..')
        button_text = os.path.join('...', os.path.relpath(filetext, fn))
        return button_text

    def format_button_dirtext(self, dirtext):
        button_text = '.../' + os.path.relpath(dirtext, dirtext + '/../..')
        return button_text

    def press_cancel(self):
        self.close()
        self.deleteLater()

    def press_apply(self):
        io_cfg = self.mainwidget.cfg_dict[Keys.io_batch]
        io_btn = self.mainwidget.button_dict[Keys.io_batch]
        txt = f'{len(self.io_list)} Datasets Selected'

        io_cfg['Source/GT List'] = self.io_list
        io_btn['Select Batch Input'].setText(txt)
        self.close()
        self.deleteLater()