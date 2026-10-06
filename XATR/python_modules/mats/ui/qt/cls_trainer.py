import os

from PyQt5.QtWidgets import (QWidget, QMenuBar, QAction, QGridLayout)
from PyQt5.QtWidgets import (QGroupBox, QGridLayout, QLabel, QComboBox)
from PyQt5.QtWidgets import (QLineEdit, QCheckBox, QHBoxLayout, QVBoxLayout)
from PyQt5.QtWidgets import (QScrollArea, QTextEdit, QPushButton)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from mats.ui.qt.common import (DirDialog, ATRProgressBar)

import mats


class ClassifierTrainerPopup(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.options_dict = {}

        self.kod = []
        self.kod2 = []
        self.mainwidget = parent
        self.initUI()

        self.fill_features()

    def initUI(self):
        self.menubar = QMenuBar(self)

        config_menu = self.menubar.addMenu('&Config')
        save_config_action = QAction('Save Config', self)
        load_config_action = QAction('Load Config', self)
        # save_config_action.triggered.connect(self.save_config)
        # load_config_action.triggered.connect(self.load_config)
        config_menu.addAction(load_config_action)
        config_menu.addAction(save_config_action)

        grid = QGridLayout()

        grid.addWidget(self.menubar, 0, 0)
        grid.setRowStretch(0, 0)
        grid.addWidget(self.create_top_group(), 1, 0)
        grid.setRowStretch(1, 0)
        grid.addLayout(self.create_feature_group(), 2, 0)
        # grid.addWidget(self.create_feature_group(), 2, 0)
        grid.setRowStretch(2, 1)
        grid.addWidget(self.create_description_group(), 3, 0)
        grid.setRowStretch(3, 1)
        grid.addLayout(self.create_file_group(), 4, 0)
        grid.setRowStretch(4, 1)
        grid.addWidget(self.create_options_group(), 5, 0)
        grid.setRowStretch(5, 0)
        grid.addWidget(self.create_start_widget(), 6, 0)
        grid.setRowStretch(6, 0)

        self.setLayout(grid)

        self.setGeometry(300, 300, 400, 600)
        self.setWindowTitle('Classifier Trainer')
        self.show()

    def create_top_group(self):
        groupBox = QGroupBox('')
        grid = QGridLayout()

        self.classifier_label = QLabel('Classifier')
        self.file_label = QLabel('Training Filename')

        self.classifier_dropdown = QComboBox()
        self.file_textbox = QLineEdit()
        self.use_det_features_checkbox = QCheckBox('Use Detector Features')

        classifiers = mats.pkg.get_type('classifier')
        self.classifier_dropdown.addItems(classifiers)

        grid.addWidget(self.classifier_label, 0, 0)
        grid.addWidget(self.classifier_dropdown, 0, 1)
        grid.addWidget(self.file_label, 1, 0)
        grid.addWidget(self.file_textbox, 1, 1)
        grid.addWidget(self.use_det_features_checkbox, 2, 0, 1, 2)

        groupBox.setLayout(grid)

        return groupBox

    def create_feature_group(self):
        config_label = QLabel('Configure Feature Module')
        config_label.setAlignment(Qt.AlignCenter)

        header_hbox = QHBoxLayout()
        header_hbox.addWidget(QLabel('Use'), stretch=0)
        header_hbox.addWidget(config_label, stretch=1)
        header_hbox.setContentsMargins(5, 11, 0, 0)

        self.scrollLayout = QVBoxLayout()
        # self.scrollLayout.addLayout(header_hbox)
        self.scrollLayout.addStretch(1)
        self.scrollLayout.setSpacing(0)

        # scroll area widget contents
        scrollWidget = QWidget()
        scrollWidget.setLayout(self.scrollLayout)

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

    def create_description_group(self):
        groupBox = QGroupBox('Description')

        self.description = QTextEdit()

        vbox = QVBoxLayout()
        vbox.addWidget(self.description)

        groupBox.setLayout(vbox)

        return groupBox

    def add_feature_widget(self, feature_name, checkbox_setting):

        # define buttons
        feature_button = QPushButton(feature_name)
        feature_checkbox = QCheckBox()

        # set button font sizes
        tmp_font = QFont()
        tmp_font.setPointSize(8)
        feature_button.setFont(tmp_font)

        self.kod.append([feature_name, feature_checkbox])

        feature_button.setProperty('feature_name', feature_name)
        # dir_label = self.format_button_dirtext(io_settings[0])
        feature_button.setText(feature_name)
        feature_checkbox.setChecked(checkbox_setting)

        self.hbox = QHBoxLayout()
        self.hbox.addWidget(feature_checkbox, stretch=0)
        self.hbox.addWidget(feature_button, stretch=1)
        self.hbox.setSpacing(7)

        self.scrollLayout.insertLayout(0, self.hbox)

    def fill_features(self):
        features = mats.pkg.get_type('feature')

        for feature in features:
            self.add_feature_widget(feature, False)

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

    def add_dirs(self):
        dir_list = ''
        dir_dialog = DirDialog(self, 'Select directory', os.getcwd())
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

    def create_options_group(self):
        groupBox = QGroupBox('Options')

        vbox = QVBoxLayout()
        vbox.setSpacing(1)

        options = ['Save Features', 'Perform Feature Analysis',
                   'Normalize Features', 'Perform Cross Validation',
                   'Contact Selection']

        for option in options:
            new_checkbox_widget = QCheckBox(option)
            self.options_dict[option] = new_checkbox_widget
            vbox.addWidget(new_checkbox_widget)

        groupBox.setLayout(vbox)

        return groupBox

    def create_start_widget(self):
        self.progressBar = ATRProgressBar(self)

        self.startButton = QPushButton("Start")
        self.startButton.clicked.connect(self.start_button_clicked)

        hbox = QHBoxLayout()

        hbox.addWidget(self.progressBar)
        # hbox.addStretch(1)
        hbox.addWidget(self.startButton)

        start_widget = QWidget(self)
        start_widget.setLayout(hbox)

        return start_widget

    def start_button_clicked(self):
        pass
