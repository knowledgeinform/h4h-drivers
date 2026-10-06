import os
import os.path as osp
import pickle
import glob
# import multiprocessing as mp
import threading
from collections import deque
import time
import math
from mats.uuid import uuid_generator
import mats.gt


from PyQt5.QtWidgets import (
    QMainWindow, QAction, QFileDialog, QLabel, QGridLayout, QStackedWidget,
    QComboBox, QGroupBox, QWidget, QPushButton, QHBoxLayout, QVBoxLayout,
    QMenuBar, QScrollArea, QCheckBox, QDesktopWidget, QSplashScreen)
from PyQt5.QtGui import (QIcon, QFont, QPixmap)
from PyQt5.QtCore import (QDir, QThread, pyqtSlot, pyqtSignal, Qt)

import mats.ui
from mats.ui.qt.roc import ROCPopup
from mats.ui.qt.cls_trainer import ClassifierTrainerPopup
from mats.ui.qt.snippet_viewer import SnippetViewerPopup
from mats.ui.qt.perf import PerfReportComparePopup
from mats.ui.qt.common import (
    ATRProgressBar, ATRDoubleSpinBox, ListWidgetPopup, DirDialog, Keys,
    ARCHIVE_ROOT)

from timeit import default_timer as timer

import mats
import mats.core
import mats.atr
import mats.sensor
import mats.pkg
import mats.log


# Find GUI icon directory
_matsui_dir = os.path.abspath(os.path.join(__file__, '..', '..'))
_matsui_icon_dir = osp.join(_matsui_dir, 'icons')


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.batchmode = False
        self.errorlog_flag = True
        self.initUI()

    def initUI(self):
        refresh_icon = osp.join(_matsui_icon_dir,
                                'outline_cached_black_24dp.png')

        # Actions

        # Exit
        exitAct = QAction(QIcon('Button-Close-icon.png'), 'Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(self.close)

        # Config actions
        save_config_action = QAction('Save Config', self)
        save_config_action.triggered.connect(self.save_config)
        load_config_action = QAction('Load Config', self)
        load_config_action.triggered.connect(self.load_config)

        # Refresh
        refreshAct = QAction(QIcon(refresh_icon), 'refresh', self)
        refreshAct.setStatusTip('Refresh Packages')
        refreshAct.triggered.connect(self.refresh_packages)

        # Options
        batchAct = QAction('Batch Mode', self, checkable=True)
        batchAct.setStatusTip('Load Multiple Datasets')
        batchAct.setChecked(self.batchmode)
        batchAct.triggered.connect(self.toggle_batchmode)

        errorLogAct = QAction('Error Logging', self, checkable=True)
        errorLogAct.setStatusTip('Enable/Disable error logging for MATS_C')
        errorLogAct.setChecked(self.errorlog_flag)
        errorLogAct.triggered.connect(self.toggle_errorlog)
        self.toggle_errorlog(self.errorlog_flag)

        # Tools
        rocAct = QAction('Generate ROC Curve', self)
        rocAct.setStatusTip('Generate ROC curves from "archive files"')
        rocAct.triggered.connect(self.generate_roc_popup)

        clsTrain = QAction('Classifier Trainer', self)
        clsTrain.setStatusTip('Open Classifier Trainer tool')
        clsTrain.triggered.connect(self.open_classifier_trainer)

        atrcfg_splitterAct = QAction('Atrconfig Splitter', self)
        atrcfg_splitterAct.setStatusTip(
            'Split atrconfig file into dconfig and cconfig files')
        atrcfg_splitterAct.triggered.connect(self.atrcfg_splitter)

        snippetViewerAct = QAction('Snippet Browser', self)
        snippetViewerAct.setStatusTip('View snippets')
        snippetViewerAct.triggered.connect(self.open_snippet_viewer)

        perfCompareAct = QAction('Compare Perf Reports', self)
        perfCompareAct.setStatusTip('Compare perf report stats')
        perfCompareAct.triggered.connect(self.open_perf_report_compare)

        # Debug
        printfilesAct = QAction('Print Files', self)
        printfilesAct.triggered.connect(self.print_files)

        printioAct = QAction('Print I/O Settings', self)
        printioAct.triggered.connect(self.print_io)

        printiobatchAct = QAction('Print I/O Batch Settings', self)
        printiobatchAct.triggered.connect(self.print_iobatch)

        printatrAct = QAction('Print ATR Settings', self)
        printatrAct.triggered.connect(self.print_atr)

        # Status Bar
        self.statusbar = self.statusBar()

        # Menu Bar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)

        configMenu = menubar.addMenu('&Config')
        configMenu.addAction(load_config_action)
        configMenu.addAction(save_config_action)

        optionsMenu = menubar.addMenu('&Options')
        optionsMenu.addAction(batchAct)
        optionsMenu.addAction(errorLogAct)

        refreshmenu = menubar.addMenu('&Refresh')
        refreshmenu.addAction(refreshAct)

        toolsMenu = menubar.addMenu('&Tools')
        toolsMenu.addAction(atrcfg_splitterAct)
        toolsMenu.addAction(clsTrain)
        toolsMenu.addAction(rocAct)
        toolsMenu.addAction(snippetViewerAct)
        toolsMenu.addAction(perfCompareAct)

        debugmenu = menubar.addMenu('Debug')
        debugmenu.addAction(printfilesAct)
        debugmenu.addAction(printioAct)
        debugmenu.addAction(printiobatchAct)
        debugmenu.addAction(printatrAct)

        # Tool Bar
        toolbar = self.addToolBar('Toolbar')
        # toolbar.addAction(exitAct)
        toolbar.addAction(refreshAct)

        self.mainwidget = MainWidget(self)
        self.setCentralWidget(self.mainwidget)
        
        screen = QDesktopWidget().availableGeometry()
        win_width = 350
        win_height = 250
        self.setGeometry(screen.width()/2-win_width,
                         screen.height()/2-win_height, win_width, win_height)
        self.setWindowTitle('Main window')
        self.setWindowIcon(QIcon(osp.join(_matsui_icon_dir, 'MATS.png')))
        
        self.loadSplash()

        self.show()
    
    def loadSplash(self):
        splash = QSplashScreen(QPixmap(osp.join(_matsui_icon_dir,
                                                'MATS-Splash.png')))
        splash.setWindowFlags(
            Qt.Window | Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint)

        # By default, SplashScreen will be in the center of the screen.
        # You can move it to a specific location if you want:
        # splash.move(10,10)
        splash.show()
        splash.showMessage(
            '<h2 style="color:white;">Scanning for MATS Modules...</h2>',
            Qt.AlignBottom | Qt.AlignHCenter, Qt.white)
        mats.pkg.scan()
        splash.showMessage(
            '<h2 style="color:white;">Updating Module Lists...</h2>',
            Qt.AlignBottom | Qt.AlignHCenter, Qt.white)
        self.mainwidget.update_mats_lists()
        time.sleep(2)
        splash.showMessage(
            '<h2 style="color:white;">Refreshing UI...</h2>',
            Qt.AlignBottom | Qt.AlignHCenter, Qt.white)
        self.mainwidget.refresh_all_dropdowns()
        time.sleep(2)
        splash.showMessage(
            '<h2 style="color:white;">Enjoy</h2>',
            Qt.AlignBottom | Qt.AlignHCenter, Qt.white)
        time.sleep(2)
        splash.close()

    def save_config(self):
        self.mainwidget.save_config()

    def load_config(self):
        self.mainwidget.load_config()

    def refresh_packages(self):
        mats.pkg.scan()
        self.mainwidget.update_mats_lists()
        self.mainwidget.refresh_all_dropdowns()

    def toggle_batchmode(self, state):
        self.batchmode = state
        self.mainwidget.update_stack_groups()

    def toggle_errorlog(self, state):
        self.errorlog_flag = state

        print(f'errorlog_flag = {self.errorlog_flag}')

        if state is True:
            mats.mats_error_enable('mats_error_log.txt')
            print('error logging enabled')
        elif state is False:
            print('error logging disabled')
            mats.mats_error_disable()

    def generate_roc_popup(self):
        self.roc_popup = ROCPopup(self)

    def open_classifier_trainer(self):
        self.classifier_trainer = ClassifierTrainerPopup(self)

    def open_snippet_viewer(self):
        self.snippet_viewer = SnippetViewerPopup(self)

    def atrcfg_splitter(self):
        atrcfg = mats.AtrConfig()

        fname = QFileDialog.getOpenFileName(
            self, 'Select atrcfg file', atrcfg['config_dir'])[0]
        fname = QDir.toNativeSeparators(fname)
        print(f'Splitting {fname}...')

        atrcfg.load(fname)

        fname_noext = os.path.splitext(fname)[0]
        atrcfg.cconfig(fname_noext + '.cconfig')
        atrcfg.dconfig(fname_noext + '.dconfig')
        # split_atrcfg(fname)

    def open_perf_report_compare(self):
        self.perf_compare_popup = PerfReportComparePopup(self)

    def print_files(self):
        print('--------------------------------')
        for filename in self.mainwidget.selected_datafiles:
            print(filename)
        print('--------------------------------')

    def print_io(self):
        print('--------------------------------')
        cfg_dict = self.mainwidget.cfg_dict
        for key in cfg_dict[Keys.io]:
            print(f'{key}:  {cfg_dict[Keys.io][key]}')
        print('--------------------------------')

    def print_iobatch(self):
        cfg_dict = self.mainwidget.cfg_dict
        for key in cfg_dict[Keys.io_batch]:
            print(f'{key}:  {cfg_dict[Keys.io_batch][key]}')

    def print_atr(self):
        print('--------------------------------')
        cfg_dict = self.mainwidget.cfg_dict
        for key in cfg_dict[Keys.modules]:
            print(f'{key}:  {cfg_dict[Keys.modules][key]}')
        print('--------------------------------')

    def closeEvent(self, *args, **kwargs):
        super(QMainWindow, self).closeEvent(*args, **kwargs)
        self.mainwidget.task_manager.quit()


class MainWidget(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.mainwindow = parent
        self.progressBar = None  # Created later
        
        self.source_filelist = []
        self.selected_datafiles = []

        # Dictionaries containing I/O and module settings
        self.cfg_dict = {}

        self.cfg_dict[Keys.io] = {}

        self.cfg_dict[Keys.io_batch] = {}
        self.cfg_dict[Keys.io_batch]['Source/GT List'] = []

        self.cfg_dict[Keys.modules] = {}

        # Dictionary containing lists of all ATR modules
        # (populated from output of mats.pkg module)
        self.mats_dict = {}

        # Dictionary to store all button widgets
        self.button_dict = {}

        # Dictionary to store progress bar widgets
        self.pBar_dict = {}

        self.reader = []
        self.task_manager = AtrTaskManager()

        print('!! Connect signal...')
        self.task_manager.start()
        self.task_manager.sig_prog.connect(self.progress_update)
        print('^^^')

        self.io_group = None  # IO Interface Group

        self.initUI()

    def initUI(self):
        self.update_mats_lists()

        grid = QGridLayout()

        # io
        self.io_group = self.create_io_group()
        self.io_batchmode_group = self.create_io_batchmode_group()

        self.io_stack = QStackedWidget(self)
        self.io_stack.addWidget(self.io_group)
        self.io_stack.addWidget(self.io_batchmode_group)

        # start
        self.start_group = self.create_start_widget()
        self.start_batchmode_group = self.create_start_batch_widget()

        self.start_stack = QStackedWidget(self)
        self.start_stack.addWidget(self.start_group)
        self.start_stack.addWidget(self.start_batchmode_group)

        # initialize stacks
        self.update_stack_groups()

        # Add groups to main widget
        grid.addWidget(self.io_stack, 0, 0)
        grid.addWidget(self.create_module_group(), 1, 0)
        grid.addWidget(self.start_stack, 2, 0)

        self.setLayout(grid)

    def save_config(self):
        fname = QFileDialog.getSaveFileName(
            self, 'Save Batch Config File', os.getcwd(), '*.guicfg')[0]

        # if statement handles 'cancel'
        if fname != '':
            if os.path.splitext(fname)[1] != '.guicfg':
                fname += '.guicfg'

            print(fname)
            pickle.dump(self.cfg_dict, open(fname, 'wb'))

    def load_config(self):
        fname = QFileDialog.getOpenFileName(
            self, 'Select ground truth file', os.getcwd(), '*.guicfg')[0]

        # if statement handles 'cancel'
        if fname != '':
            cfg_dict = pickle.load(open(fname, 'rb'))
            in_io_batch = cfg_dict[Keys.io_batch]
            io_batch = self.cfg_dict[Keys.io_batch]

            # batch_io
            for button_key in self.button_dict[Keys.io_batch]:
                btn = self.button_dict[Keys.io_batch][button_key]
                btn_src = self.button_dict[Keys.io_batch]['Select Batch Input']
                button_type = type(btn)

                # print(button_key)
                if button_key == 'Select Batch Input':
                    try:
                        source_gt_list = in_io_batch['Source/GT List']
                        io_batch['Source/GT List'] = source_gt_list
                        btn_src.setText(
                            f'{len(source_gt_list)} Datasets Selected')
                    except:
                        print('Batch Source/GT List not set')

                elif button_type == QComboBox:
                    index = btn.findText(cfg_dict[Keys.io_batch][button_key])
                    if index >= 0:
                        btn.setCurrentIndex(index)

            # modules
            for button_key in self.button_dict[Keys.modules]:
                button = self.button_dict[Keys.modules][button_key]
                button_type = type(button)

                if button_type == QComboBox:
                    index = button.findText(cfg_dict[Keys.modules][button_key])
                    if index >= 0:
                        button.setCurrentIndex(index)

    def update_stack_groups(self):
        # Update / Initialize stacked widgets
        ind = int(self.mainwindow.batchmode)

        self.io_stack.setCurrentIndex(ind)
        self.start_stack.setCurrentIndex(ind)
        self.progressBar = self.pBar_dict[['Single', 'Batch'][ind]]

    def update_mats_lists(self):
        # detector config
        dconfig = mats.DConfig()
        dconfig_dir = dconfig['config_dir']

        # classifier config
        cconfig = mats.CConfig()
        cconfig_dir = cconfig['config_dir']

        self.mats_dict = {
            'Data Readers': [''] + mats.pkg.get_type('reader'),
            'Sensors': [''] + mats.sensor.mats_known_sensors(),
            'Detectors': [''] + mats.pkg.get_type('detector'),
            'Normalizers': [''] + mats.pkg.get_type('normalizer'),
            'Classifiers': [''] + mats.pkg.get_type('classifier'),
            'Features': [''] + mats.pkg.get_type('feature'),
            'Detector Configs': [''] + glob.glob(dconfig_dir + '/*.dconfig'),
            'Class Configs': [''] + glob.glob(cconfig_dir + '/*.cconfig')
        }

    def create_io_group(self):
        group_box = QGroupBox("I/O")

        button_group = Keys.io
        button_names = ['Source Directory', 'Data Reader', 'Sensor',
                        'Data Files', 'Ground Truth File', 'Output Dir']
        button_types = ['button', 'dropdown', 'dropdown', 'button', 'button',
                        'button', 'button']

        grid = self.create_atr_grid(button_names, button_types, button_group)
        btn_dict = self.button_dict[button_group]

        # source dir
        btn_dict['Source Directory'].clicked.connect(self.source_dir_clicked)

        # reader
        btn_dict['Data Reader'].currentIndexChanged[str].connect(
            self.onchange_reader)

        # sensor
        btn_dict['Sensor'].currentIndexChanged[str].connect(
            self.onchange_sensor)

        # data files
        btn_dict['Data Files'].clicked.connect(self.data_files_clicked)

        # ground truth file
        btn_dict['Ground Truth File'].clicked.connect(
            self.ground_truth_clicked)

        # output dir
        btn_dict['Output Dir'].clicked.connect(self.outputdir_clicked)

        group_box.setLayout(grid)

        return group_box

    def create_io_batchmode_group(self):
        group_box = QGroupBox("I/O")
        button_group = Keys.io_batch
        button_names = ['Select Batch Input', 'Data Reader', 'Sensor',
                        'Output Dir']
        button_types = ['button', 'dropdown', 'dropdown', 'button']

        grid = self.create_atr_grid(button_names, button_types, button_group)
        btn_dict = self.button_dict[button_group]

        # reader
        btn_dict['Data Reader'].currentIndexChanged[str].connect(
            self.onchange_reader)

        # sensor
        btn_dict['Sensor'].currentIndexChanged[str].connect(
            self.onchange_sensor)

        # source dir
        btn_dict['Select Batch Input'].clicked.connect(
            self.select_batch_input_clicked)

        # output dir
        btn_dict['Output Dir'].clicked.connect(self.outputdir_clicked)

        group_box.setLayout(grid)

        return group_box

    def create_module_group(self):
        group_box = QGroupBox("ATR Modules")

        button_group = Keys.modules
        button_names = ['Detector', 'Detector Config', 'Normalizer',
                        'Classifier', 'Class Config', 'Features',
                        'Class Thresh']
        button_types = ['dropdown', 'dropdown', 'dropdown', 'dropdown',
                        'dropdown', 'label', 'doublespinbox']
        grid = self.create_atr_grid(button_names, button_types, button_group)
        btn_dict = self.button_dict[button_group]

        btn_dict['Class Config'].currentIndexChanged[str].connect(
            self.update_feature_widget)
        btn_dict['Class Thresh'].setMaximum(1)
        btn_dict['Class Thresh'].setDecimals(10)
        btn_dict['Class Thresh'].setSingleStep(0.01)
        btn_dict['Class Thresh'].setValue(0.5)

        group_box.setLayout(grid)

        return group_box

    def create_atr_grid(self, button_names, button_types, button_group):
        # Create grid of widgets
        # Button widgets are stored in self.button_dict under key:
        # button_prefix + button_name
        grid = QGridLayout()

        self.button_dict[button_group] = {}
        for ii, name in enumerate(button_names):
            button_type = button_types[ii]

            label = QLabel(name)

            grid.addWidget(label, ii, 0)

            if button_type == 'button':
                button = QPushButton('', self)
            elif button_type == 'dropdown':
                button = QComboBox(self)
            elif button_type == 'label':
                button = QLabel(self)
            elif button_type == 'doublespinbox':
                button = ATRDoubleSpinBox(self)
            else:
                raise ValueError('Invalid button type')

            grid.addWidget(button, ii, 1)
            button.setProperty('group', button_group)
            button.setObjectName(name)
            self.button_dict[button_group][name] = button
            if button_type == 'dropdown':
                self.button_dict[button_group][name].currentIndexChanged[str].connect(
                    self.update_dropdown_vars)
                self.refresh_dropdowns(button_group, name)
        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 1)

        return grid

    def create_start_widget(self):
        progress_bar = ATRProgressBar(self)
        self.pBar_dict['Single'] = progress_bar

        self.startButton = QPushButton("Start")

        self.startButton.clicked.connect(self.start_button_clicked)

        hbox = QHBoxLayout()
        hbox.addWidget(progress_bar)
        # hbox.addStretch(1)
        hbox.addWidget(self.startButton)

        start_widget = QWidget(self)
        start_widget.setLayout(hbox)

        return start_widget

    def create_start_batch_widget(self):
        self.progressBar_batch_datasets = ATRProgressBar(self)

        progress_bar = ATRProgressBar(self)
        self.pBar_dict['Batch'] = progress_bar

        self.startButton_batch = QPushButton('Batch')

        self.startButton_batch.clicked.connect(self.start_button_clicked)

        hbox = QHBoxLayout()

        vbox = QVBoxLayout()
        vbox.addWidget(self.progressBar_batch_datasets)
        vbox.addWidget(progress_bar)

        hbox.addLayout(vbox)
        hbox.addWidget(self.startButton_batch)

        start_widget = QWidget(self)
        start_widget.setLayout(hbox)

        return start_widget

    def refresh_all_dropdowns(self):
        io_dropdowns = ['Data Reader', 'Sensor']
        iobatch_dropdowns = ['Data Reader', 'Sensor']
        module_dropdowns = ['Detector', 'Normalizer', 'Classifier',
                            'Detector Config', 'Class Config']

        dropdowns = io_dropdowns + iobatch_dropdowns + module_dropdowns

        button_groups = [Keys.io] * len(io_dropdowns) + \
                        [Keys.io_batch] * len(iobatch_dropdowns) + \
                        [Keys.modules] * len(module_dropdowns)

        self.refresh_dropdowns(button_groups, dropdowns)

    def refresh_dropdowns(self, button_groups, dropdowns):
        # Called when available values for a dropdown changes
        if isinstance(dropdowns, str):
            dropdowns = [dropdowns]

        if isinstance(button_groups, str):
            button_groups = [button_groups] * len(dropdowns)

        for button_group, atr_component in zip(button_groups, dropdowns):
            self.button_dict[button_group][atr_component].clear()

            mats_name = atr_component + 's'

            for atr_module in self.mats_dict[mats_name]:
                self.button_dict[button_group][atr_component].addItem(
                    atr_module)

    def select_batch_input_clicked(self):
        self.batch_input_popup = BatchInputPopup(
            self, self.cfg_dict[Keys.io_batch]['Source/GT List'])
        self.batch_input_popup.show()

    def onchange_sensor(self, text):
        print(f'Sensor: {text}')
        # TODO(Bradley): A sensor change should require a rescan of data.
        return None

    def onchange_reader(self, text):
        rcfg = mats.Struct()
        print(f'Reader: {text}')
        if not text:
            return
        self.reader = mats.pkg.create(text)
        if self.reader:
            self.reader.configure(rcfg)
        else:
            raise RuntimeError(f'Failure creating reader module \'{text}\'')
        self.source_filelist = self.find_data_files()
        return

    def source_dir_clicked(self):
        dir_name = QFileDialog.getExistingDirectory(
            self, 'Select directory', '/home/Data/SSAM2')
        dir_name = QDir.toNativeSeparators(dir_name)
        print(f'Source Dir: {dir_name}')
        sender = self.sender()
        sender.setText(dir_name)
        module_type = sender.objectName()

        self.cfg_dict[Keys.io][module_type] = dir_name
        self.source_filelist = self.find_data_files()

    def find_data_files(self, source_dir_name=None):
        if source_dir_name:
            root_dir = source_dir_name
        else:
            root_dir = self.cfg_dict[Keys.io]['Source Directory']
        if self.reader:
            h5_filelist = self.reader.scan(root_dir)
        else:
            print('!! No reader Loaded')
            h5_filelist = []
        return h5_filelist

    def data_files_clicked(self):
        print('data files')
        self.list_popup = ListWidgetPopup(self)

    def ground_truth_clicked(self):
        fname = QFileDialog.getOpenFileName(
            self, 'Select ground truth file',
            self.cfg_dict[Keys.io]['Source Directory'])
        fname = QDir.toNativeSeparators(fname[0])
        print(f'Ground Truth: {fname}')
        sender = self.sender()
        sender.setText(fname)
        module_type = sender.objectName()
        self.cfg_dict[Keys.io][module_type] = fname

    def outputdir_clicked(self):
        dir_name = QFileDialog.getExistingDirectory(
            self, 'Select Output directory', ARCHIVE_ROOT)
        dir_name = QDir.toNativeSeparators(dir_name)
        print(f'Output Dir: {dir_name}')
        sender = self.sender()
        sender.setText(dir_name)
        module_type = sender.objectName()
        if self.mainwindow.batchmode is False:
            self.cfg_dict[Keys.io][module_type] = dir_name
        elif self.mainwindow.batchmode is True:
            self.cfg_dict[Keys.io_batch][module_type] = dir_name

    def update_dropdown_vars(self, text):
        sender = self.sender()
        module_group = sender.property('group')
        module_type = sender.objectName()

        self.cfg_dict[module_group][module_type] = text

    def update_feature_widget(self, text):
        if text != '':
            cconfig = mats.CConfig()
            cconfig.load(text)
            features = cconfig['features']
            self.button_dict[Keys.modules]['Features'].setText(
                '|'.join(features))

    def find_only_gtfiles(self, datafile_list, gt_filename):
        gt_list_of_dicts = mats.gt.read_txt(gt_filename)
        gt_datafilenames = [x['fn'] for x in gt_list_of_dicts]

        gt_only_list = [x for x in datafile_list
                        if os.path.basename(x) in gt_datafilenames]

        print(f'Initial Datafile List Length = {len(datafile_list)}')
        print(f'GT List Length = {len(gt_list_of_dicts)}')
        print(f'Filtered Datafile List Length = {len(gt_only_list)}')

        return gt_only_list

    @pyqtSlot(dict)
    def progress_update(self, val):
        if val['files_total'] == 0:
            p = 0
        else:
            p = math.floor(100 * val['files_completed'] / val['files_total'])
        self.progressBar.setValue(p)

        if self.mainwindow.batchmode is True:
            self.progressBar_batch_datasets.setValue(len(val['completed']))
        # print(f'PROGRESS SLOT: {val}')

    def start_button_clicked(self):
        try:
            module_dict = self.cfg_dict[Keys.modules]
            io_dict = self.cfg_dict[Keys.io]
            thresh = self.button_dict[Keys.modules]['Class Thresh'].value()

            # load detector and classifier config files
            dconfig = mats.DConfig()
            if len(module_dict['Detector Config']) == 0:
                # if not 'mats_test_modules' in module_dict['Detector']:
                #     raise RuntimeError('Missing dconfig')
                
                # We are going to assume test modules can run without a
                # dconfig. So we are going to setup the minimum for it to get
                # through checks.
                info = mats.pkg.module_info(module_dict['Detector'])
                dconfig['sensor'] = io_dict['Sensor']
                dconfig['detector'] = info[0]['name']
                dconfig['det_lang'] = info[0]['engine']
                info = mats.pkg.module_info(module_dict['Normalizer'])
                dconfig['normalizer'] = info[0]['name']
                dconfig['norm_lang'] = info[0]['engine']
            else:
                dconfig.load(module_dict['Detector Config'])
            
            cconfig = mats.CConfig()
            if len(module_dict['Class Config']) == 0:
                if 'mats_test_modules' not in module_dict['Classifier']:
                    raise RuntimeError('Missing cconfig')

                # Similar to dconfig above
                info = mats.pkg.module_info(module_dict['Classifier'])
                cconfig['sensor'] = io_dict['Sensor']
                cconfig['classifier'] = info[0]['name']
                cconfig['cls_lang'] = info[0]['engine']
                cconfig['detector'] = dconfig['detector']
            else:
                cconfig.load(module_dict['Class Config'])

            # create ATR config
            atrcfg = mats.AtrConfig()
            atrcfg.create_from(dconfig, cconfig)
            xxx = osp.join(self.cfg_dict[Keys.io]['Output Dir'], 'mats.atrcfg')
            atrcfg['filename'] = xxx
            print(atrcfg)
            mats.log.info('configuring atr...')
            self.mainwindow.statusbar.showMessage('Configuring ATR')
            start = timer()
            mats.atr.configure(atrcfg)
            end = timer()
            mats.log.info(f'configure time: {end - start}s')

            # create ATR cfg
            arc_uuid = uuid_generator()
            arc_cfg = {
                'Uuid': arc_uuid,
                'SourceConfigId': '00000000-0000-0000-0000-000000000000',
                'Name': 'Test',
                'Sensor': io_dict['Sensor'],
                'Description': '',
                'Version': '',
                'Location': [],
                'Environment': [],
                'Date': 0.0,
                'Threshold': 1.0,
                'RoCs': [],
                'Dependency': '',
                'Active': True,
                'Disabled': False,
                'ThreadSafe': False
            }
            # print(arc_cfg)

            self.progressBar.setRange(0, 100)
            self.progressBar.setValue(0)

            if self.mainwindow.batchmode is False:
                job = {
                    'reader': self.reader,
                    'atrcfg': atrcfg,
                    'cfg': arc_cfg,
                    'files': self.selected_datafiles,
                    'outdir': io_dict['Output Dir'],
                    'gtfn': io_dict['Ground Truth File'],
                    'thresh': thresh
                }
                self.task_manager.setup([job])
            elif self.mainwindow.batchmode is True:
                io_batch = self.cfg_dict[Keys.io_batch]
                jobs = []
                for ii, fn in enumerate(io_batch['Source/GT List']):
                    srcdir = fn[0]
                    gt_file = fn[1]
                    only_gt = fn[2]
                    outdir = os.path.join(
                        io_batch['Output Dir'],
                        os.path.relpath(srcdir, os.path.join(srcdir, '..'))
                    )
                    all_datafiles = self.find_data_files(srcdir)

                    # filter out non-ground truth
                    if only_gt is False:
                        selected_datafiles = all_datafiles
                    elif only_gt is True:
                        selected_datafiles = self.find_only_gtfiles(
                            all_datafiles, gt_file)
                    else:
                        raise ValueError('only_gt should be True or False')

                    jobs.append({
                        'reader': self.reader,
                        'atrcfg': atrcfg,
                        'cfg': arc_cfg,
                        'files': selected_datafiles,
                        'outdir': outdir,
                        'gtfn': gt_file,
                        'thresh': thresh
                    })
                self.progressBar_batch_datasets.setRange(0, len(jobs))
                self.progressBar_batch_datasets.setValue(0)
                self.task_manager.setup(jobs)
            else:
                raise ValueError('batchmode should be True or False')
            print('DONE')
        except Exception as e:
            print(e)


class BatchInputPopup(QWidget):
    # Popup that allows selection of multiple input datasets
    def __init__(self, parent, input_io_list):
        super().__init__()

        self.mainwidget = parent

        self.kod = []
        self.io_list = []

        self.initUI(input_io_list)

    def initUI(self, input_io_list):
        self.menubar = QMenuBar(self)

        # Save and Load
        config_menu = self.menubar.addMenu('&Config')
        save_config_action = QAction('Save Config', self)
        load_config_action = QAction('Load Config', self)
        save_config_action.triggered.connect(self.save_config)
        load_config_action.triggered.connect(self.load_config)
        config_menu.addAction(load_config_action)
        config_menu.addAction(save_config_action)

        # Debug
        debug_menu = self.menubar.addMenu('&Debug')
        print_sources_action = QAction('Print Sources', self)
        print_sources_action.triggered.connect(self.print_sources)
        debug_menu.addAction(print_sources_action)

        grid = QGridLayout()

        applyButton = QPushButton("Apply")
        cancelButton = QPushButton("Cancel")
        applyButton.clicked.connect(self.press_apply)
        cancelButton.clicked.connect(self.press_cancel)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(cancelButton)
        hbox.addWidget(applyButton)

        grid.addWidget(self.menubar, 0, 0)
        grid.addWidget(self.create_add_group(), 1, 0)
        grid.addWidget(self.create_source_group(), 2, 0)
        grid.addLayout(hbox, 3, 0)

        self.setLayout(grid)

        if input_io_list != []:
            for io in input_io_list:
                self.addWidget(io_settings=io)

        self.setGeometry(300, 300, 1250, 675)

        self.setWindowTitle('Batch Input')
        self.show()

        print('adding widgets back')
        print(self.io_list)

    def save_config(self):
        fname = QFileDialog.getSaveFileName(
            self, 'Save Batch Config File', os.getcwd(), '*.batchcfg')[0]

        # if statement handles 'cancel'
        if fname != '':

            self.remove_blank_widgets()

            if os.path.splitext(fname)[1] != '.batchcfg':
                fname += '.batchcfg'

            print(fname)
            pickle.dump(self.io_list, open(fname, 'wb'))

    def load_config(self):
        fname = QFileDialog.getOpenFileName(
            self, 'Select ground truth file', os.getcwd(), '*.batchcfg')[0]

        # if statement handles 'cancel'
        if fname != '':
            self.reset_widgets()
            tmp_io_list = pickle.load(open(fname, 'rb'))
            for io in tmp_io_list:
                if len(io) == 2:
                    io += [False]
                self.addWidget(io_settings=io)

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

    def create_add_group(self):
        group_box = QGroupBox('')
        grid = QGridLayout()

        self.add_button = QPushButton('Add Source Directories')
        self.remove_button = QPushButton('Remove All')
        self.check_all_button = QPushButton('Check/Uncheck GT')

        grid.addWidget(self.add_button, 0, 0)
        grid.addWidget(self.remove_button, 0, 1)
        grid.addWidget(self.check_all_button, 0, 2)

        # self.add_button.setObjectName('Add Button')
        # self.remove_button.setObjectName('Remove Button')

        self.add_button.clicked.connect(self.add_dirs)
        self.remove_button.clicked.connect(self.remove_all_widgets)
        self.check_all_button.clicked.connect(self.check_all_gts)

        group_box.setLayout(grid)

        return group_box

    def create_source_group(self):
        self.scrollLayout = QVBoxLayout()
        self.scrollLayout.addStretch(1)
        # self.scrollLayout.setAlignment(Qt.AlignTop)
        # self.scrollLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollLayout.setSpacing(0)

        # scroll area widget contents
        self.scrollWidget = QGroupBox('I/O')
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
        gt_button = QPushButton('Ground Truth')
        gt_only_checkbox = QCheckBox('GT only')

        x_button = QPushButton('')
        x_button.setIcon(QIcon('Button-Close-icon.png'))

        # set button font sizes
        tmp_font = QFont()
        tmp_font.setPointSize(8)
        source_button.setFont(tmp_font)
        gt_button.setFont(tmp_font)

        # force source and gt_buttons to be the same size
        source_button.setMinimumSize(source_button.sizeHint())
        gt_button.setMinimumSize(source_button.minimumSizeHint())
        x_button.setMaximumSize(source_button.minimumSizeHint())

        # button signals
        source_button.clicked.connect(self.source_button_clicked)
        gt_button.clicked.connect(self.gt_button_clicked)
        gt_only_checkbox.stateChanged.connect(self.gt_checkbox_statechanged)
        x_button.clicked.connect(self.x_button_clicked)

        self.kod.append([source_button, gt_button, x_button, gt_only_checkbox])

        if io_settings is None:
            self.io_list.append([None, None, None])
        else:
            self.io_list.append(io_settings)
            source_button_text = self.format_button_dirtext(io_settings[0])
            source_button.setText(source_button_text)
            # source_button.setStyleSheet("Text-align:left")
            if io_settings[1] is not None:
                gt_button_text = self.format_button_filetext(io_settings[1])
                gt_button.setText(gt_button_text)
                # gt_button.setStyleSheet("Text-align:left")
            if io_settings[2] is not None:
                gt_only_checkbox.setChecked(io_settings[2])

        self.hbox = QHBoxLayout()
        self.hbox.addWidget(x_button, stretch=0)
        self.hbox.addWidget(source_button, stretch=1)
        self.hbox.addWidget(gt_button, stretch=1)
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


class AtrTaskManager(QThread):
    sig_prog = pyqtSignal(dict)

    def __init__(self):
        """Initialize ATR Task Manager."""
        QThread.__init__(self)
        self._quitflag = False
        self._jobs_total = 0
        self._jobs_processing = 0
        self._jobs = deque()  # Jobs to be processed
        self._jobs_completed = deque()  # Completed jobs
        self.monitoring = False  # Indicates if run has been executed
        self.sleeptime = 5
        self.max_workers = 5
        self._files_total = 0  # Total files to process
        self._files_completed = 0  # Total files completed
        self._files_active = 0  # Total files processed in active jobs

    def __del__(self):
        print('Deleting ATR Task Manager...')
        self.quit()
        self.wait()

    def quit(self):
        """Starts shutdown of task manager and running tasks."""
        self._quitflag = True

    def progress(self):
        status = {
            'total': self._jobs_total,
            'completed': self._jobs_completed,
            'processing': self._jobs_processing,
            'files_total': self._files_total,
            'files_completed': self._files_completed+self._files_active
        }
        self.sig_prog.emit(status)
        return

    def reset(self):
        self._jobs_total = 0
        self._jobs.clear()
        self._jobs_completed.clear()

    def setup(self, jobs):
        """Add jobs for processing."""
        num_files = sum([len(x['files']) for x in jobs])
        self._jobs.extend(jobs)
        self._jobs_total += len(jobs)
        self._files_total += num_files

    def run(self):
        """Start task manager."""
        print('Starting Task Manager...')

        workers = deque()
        self.monitoring = True
        while not self._quitflag:
            # print(f'>> Number of jobs: {len(self._jobs)}')
            self.progress()

            # Clear out completed jobs
            if len(workers) > 0:
                # print('>> Checking worker status...')
                shifts = 0
                while shifts < len(workers):
                    completed = workers[0].files_completed
                    total = workers[0].files_total
                    # print(f'progress: {completed/total}')
                    if completed >= total:
                        # print('>> Removing completed work...')
                        self._jobs_completed.append(workers[0].job)
                        self._jobs_processing = self._jobs_processing - 1
                        self._files_completed += len(workers[0].job['files'])
                        workers.popleft()
                        continue
                    workers.rotate(-1)
                    shifts += 1

            while len(self._jobs) > 0:
                # print('>> Checking worker addition of jobs...')
                if len(workers) >= self.max_workers:
                    break  # No workers available
                # print('>> Creating new job...')
                job = self._jobs.popleft()

                worker = AtrWorker()
                worker.setup(job)
                worker.start()
                self._jobs_processing = self._jobs_processing + 1
                workers.append(worker)

            completed = sum([x.files_completed for x in workers])
            self._files_active = completed

            # print('>> waiting...')
            time.sleep(self.sleeptime)

        # Shutdown workers
        for i in range(len(workers)):
            workers[i].terminate()
            workers[i].join()
        workers.clear()

        self.monitoring = False
        print("!! ATR Task Manager stopping")


class AtrWorker(threading.Thread):
    def __init__(self):
        """Initialize ATR Worker Thread."""
        threading.Thread.__init__(self)
        self._quitflag = False
        self.job = None
        #self.files_completed = mp.Value('i', 0, lock=False)
        self.files_completed = 0
        #self.files_total = mp.Value('i', 0, lock=False)
        self.files_total = 0
        self.completed = False

    def quit(self):
        """Stop processing."""
        self._quitflag = True

    def setup(self, job):
        """Setup job to be processed."""
        if self.is_alive():
            return
        self.job = job
        print(f'AtrWorker setup: {self.job}')

    # def run(self):
    #     """Start processing."""
    #     if not self.job:
    #         return
    #     print(f'AtrWorker run: {self.job}')
    #     files = self.job['files']
    #     for ii, source_file in enumerate(files):
    #         print(f'processing: {source_file}')
    #         time.sleep(2)
    #         self.files_completed = self.files_completed + 1
    #     self.completed = True

    def run(self):
        """Start processing."""
        if not self.job:
            return
        print(f'AtrWorker run: {self.job}')
        thresh = self.job['thresh']
        outdir = self.job['outdir']
        atrcfg = self.job['atrcfg']
        files = self.job['files']
        gtfn = self.job['gtfn']
        print(f'Outdir: {outdir}')

        # save ATR config
        print('saving ATR configuration...')
        atrcfg['filename'] = os.path.join(outdir, 'mats.atrcfg')
        atrcfg.save()

        print('setting up archiver...')
        arc_mng = mats.Archiver()
        arc_mng.location(outdir)
        arc = mats.Archive()
        arc.location(outdir)
        arcr_cfg = mats.Struct()
        arcr_cfg['filename_format'] = 'filename'
        arc_mng.options(arcr_cfg)

        print(f'reading ground truth file ({gtfn})...')
        gt = mats.gt.read_txt(gtfn)

        self.files_total = len(files)
        for ii, source_file in enumerate(files):
            print('----------------------------------------------------------')
            print(f'Input {ii+1}/{len(files)}')
            print(f'Source File: {source_file}')
            total_start = timer()

            print('reading input structure...')
            start_read = timer()
            data = self.job['reader'].read(source_file)
            end_read = timer()
            read_time = end_read - start_read
            print(f'read time: {read_time}s')

            for ins in data:
                start_process = timer()
                con, ecd = mats.atr.process(ins, gt)
                end_process = timer()
                process_time = end_process - start_process
                print(f'process time: {process_time}s')

                start_archive = timer()
                print(ins)
                idty = arc_mng.create(self.job['cfg'], ins)
                print(f'Arc Name: |{idty}|')
                # idty = arc_mng.find(self.job['cfg'], ins)
                arc.load(idty)
                arc.add_contacts(con)
                arc.add_ecdata(ecd)
                arc.add_gt(gt)
                end_archive = timer()
                archive_time = end_archive - start_archive
                print(f'archive time: {archive_time}s')

            total_end = timer()
            total_time = total_end - total_start
            print(f'total time for image: {total_time}s')

            self.files_completed += 1

        # generate json perf report for this dataset
        start_perf = timer()
        command = f'$XATR_ROOT/bin/mats_perf_report -t {thresh} {outdir}'
        os.system(command)
        end_perf = timer()
        perf_time = end_perf - start_perf
        print(f'total time to generate perf report: {perf_time}')

        self.completed = True


def run_atr(io_dict, module_dict, selected_datafiles, gui):
    source_filelist = selected_datafiles

    # initialize reader
    rdr = mats.pkg.create(io_dict['Data Reader'])
    # currently readers do not nead config files, pass empty mats struct
    rcfg = mats.Struct()
    rdr.configure(rcfg)

    # load detector and classifier config files
    dconfig = mats.DConfig()
    dconfig.load(module_dict['Detector Config'])
    cconfig = mats.CConfig()
    cconfig.load(module_dict['Class Config'])

    # create ATR config
    atrcfg = mats.AtrConfig()
    atrcfg.create_from(dconfig, cconfig)
    atrcfg['filename'] = io_dict['Output Dir'] + '/mats.atrcfg'

    atrcfg.save()

    print('configuring atr...')
    gui.mainwindow.statusbar.showMessage('Configuring ATR')
    start = timer()
    mats.atr.configure(atrcfg)
    end = timer()
    print(f'configure time: {end - start}s')

    # Archiver
    arc_uuid = uuid_generator()

    print('setting up archiver...')
    gui.mainwindow.statusbar.showMessage('Setting up Archiver')
    out_dir = io_dict['Output Dir']
    arc_cfg = {
        'Uuid': arc_uuid,
        'SourceConfigId': '00000000-0000-0000-0000-000000000000',
        'Name': 'Test',
        'Description': '',
        'Version': '',
        'Location': [],
        'Environment': [],
        'Date': 0.0,
        'Threshold': 1.0,
        'RoCs': []
    }
    arc_mng = mats.Archiver()
    arc_mng.location(out_dir)
    arc = mats.Archive()
    arc.location(out_dir)

    arcr_cfg = mats.Struct()
    arcr_cfg['filename_format'] = 'filename'
    arc_mng.options(arcr_cfg)

    print('reading ground truth file...')
    gui.mainwindow.statusbar.showMessage('Reading Ground Truth File')
    gt = mats.gt.read_txt(io_dict['Ground Truth File'])

    gui.mainwindow.statusbar.showMessage('Running...')
    gui.progressBar.setRange(0, len(source_filelist))
    # gui.progressBar.setFormat('{} / {}'.format(0, len(source_filelist)))
    gui.progressBar.setValue(0)

    print(source_filelist)
    print('--Stopping--')
    return
    for ii, source_file in enumerate(source_filelist):
        print('--------------------------------------------------------------')
        print(f'Input {ii+1}/{len(source_filelist)}')
        print(f'Source File: {source_file}')
        total_start = timer()

        print('reading input structure...')
        start_read = timer()
        data = rdr.read(source_file)
        end_read = timer()
        read_time = end_read - start_read
        print(f'read time: {read_time}s')

        for ins in data:
            start_process = timer()
            con, ecd = mats.atr.process(ins, gt)
            end_process = timer()
            process_time = end_process - start_process
            print(f'process time: {process_time}s')

            start_archive = timer()
            arc_mng.create(arc_cfg, ins)
            idty = arc_mng.find(arc_cfg, ins)
            arc.load(idty)
            arc.add_contacts(con)
            arc.add_ecdata(ecd)
            arc.add_gt(gt)
            end_archive = timer()
            archive_time = end_archive - start_archive
            print(f'archive time: {archive_time}s')

        total_end = timer()
        total_time = total_end - total_start
        print(f'total time for image: {total_time}s')

        gui.progressBar.setValue(ii+1)

    # generate json perf report for this dataset
    start_perf = timer()
    # command = '$XATR_ROOT/bin/mats_perf_report -t 0.5 ' + out_dir
    thresh_value = gui.button_dict[Keys.modules]['Class Thresh'].value()
    command = f'$XATR_ROOT/bin/mats_perf_report -t {thresh_value} {out_dir}'
    os.system(command)
    end_perf = timer()
    perf_time = end_perf - start_perf
    print(f'total time to generate perf report: {perf_time}')

    gui.mainwindow.statusbar.showMessage('Done')
