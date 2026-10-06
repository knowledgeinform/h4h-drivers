import os
from types import SimpleNamespace

from PyQt5.QtWidgets import (
    QFileDialog, QListView, QTreeView, qApp, QFileSystemModel, QDoubleSpinBox,
    QAbstractItemView, QProgressBar, QWidget, QCheckBox, QPushButton,
    QListWidget, QHBoxLayout, QVBoxLayout, QDesktopWidget)

# Keys
Keys = SimpleNamespace()
Keys.io = 'I/O'
Keys.io_batch = 'Batch I/O'
Keys.modules = 'Modules'

# Globals
ARCHIVE_ROOT = os.path.expanduser('~/Downloads')


class DirDialog(QFileDialog):
    # File dialog class that allows selecting multiple directories
    def __init__(self, *args):
        QFileDialog.__init__(self, *args)
        self.setOption(self.DontUseNativeDialog, True)
        self.setFileMode(self.DirectoryOnly)

        for view in self.findChildren((QListView, QTreeView)):
            if isinstance(view.model(), QFileSystemModel):
                view.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.show()

    def get_dirlist(self):
        return self.selectedFiles()


class ATRProgressBar(QProgressBar):
    # Progress bar class that is formatted [x / len(x)]
    """docstring for qProress"""
    def __init__(self, args):
        super().__init__(args)
        self.valueChanged.connect(self.onValueChanged)

    def onValueChanged(self, value):
        self.setFormat(f'{value} / {self.maximum()}')
        qApp.processEvents()


class ATRDoubleSpinBox(QDoubleSpinBox):
    def __init__(self, *args):
        super().__init__(*args)

    def textFromValue(self, value):
        # return ('%f' % value).rstrip('0').rstrip('.')
        return '%.12g' % value


class ListWidgetPopup(QWidget):
    # List widget for selecting which data files to use
    def __init__(self, parent):
        super().__init__()

        self.parent = parent
        self.listWidget = None  # UI List Widget
        self.gt_only_filelist = None

        self.initUI()

    def initUI(self):
        gt_only_checkbox = QCheckBox('Gt Only')
        okButton = QPushButton("OK")
        cancelButton = QPushButton("Cancel")

        self.listWidget = QListWidget()
        self.listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.listWidget.addItems(self.parent.source_filelist)
        self.listWidget.selectAll()

        try:
            gt_file = self.parent.cfg_dict[Keys.io]['Ground Truth File']
            self.gt_only_filelist = self.parent.find_only_gtfiles(
                self.parent.source_filelist, gt_file)
        except:
            gt_file = None

        gt_only_checkbox.stateChanged.connect(self.gt_only_toggled)
        okButton.clicked.connect(self.press_ok)
        cancelButton.clicked.connect(self.press_cancel)

        hbox = QHBoxLayout()
        if gt_file is not None:
            hbox.addWidget(gt_only_checkbox)
        hbox.addStretch(1)
        hbox.addWidget(okButton)
        hbox.addWidget(cancelButton)

        vbox = QVBoxLayout()
        vbox.addWidget(self.listWidget)
        # vbox.addStretch(1)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        
        screen = QDesktopWidget().availableGeometry()
        winWidth = 350
        winHeight = 350
        self.setGeometry(screen.width()/2 - winWidth,
                         screen.height()/2 - winHeight/2, winWidth, winHeight)
        self.setWindowTitle('Data Files')
        self.show()

    def press_ok(self):
        # print([item.text() for item in self.listWidget.selectedItems()])
        self.parent.selected_datafiles = [
            item.text() for item in self.listWidget.selectedItems()]
        data_files_string = f'{len(self.parent.selected_datafiles)} files available'

        self.parent.button_dict[Keys.io]['Data Files'].setText(
            data_files_string)
        self.close()

    def press_cancel(self):
        self.close()

    def gt_only_toggled(self):
        sender = self.sender()
        self.listWidget.clear()
        if sender.isChecked():
            self.listWidget.addItems(self.gt_only_filelist)
        else:
            self.listWidget.addItems(self.parent.source_filelist)
