import os
import os.path as osp
from pathlib import Path
from warnings import warn as Warn

from PyQt5.QtWidgets import (
        QMainWindow, QWidget, QMenuBar, QAction, QAbstractItemView,
        QTableWidget, QTableWidgetItem, QFileDialog, QPushButton, QHeaderView,
        QGridLayout, QLabel, QVBoxLayout, QHBoxLayout, QCheckBox, QSizePolicy
)
from PyQt5.QtCore import (Qt, QDir)
from PyQt5.QtGui import (QFont, QIcon)

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import numpy as np
import mats
import mats.pkg
import mats.gt
import matsui.input

import sys
#from PyQt5.QtWidgets import QApplication
#app = QApplication(sys.argv)


def add_centered_cell(tb, rx, cx, val):
    item = QTableWidgetItem(val)
    item.setTextAlignment(Qt.AlignHCenter)
    tb.setItem(rx, cx, item)
    return


class UiFileSelect(QWidget):
    def __init__(self, title):
        super().__init__()
        layout = QHBoxLayout(self)
        self.button = QPushButton('', self)
        self.label = QLabel(title)
        self.button.clicked.connect(self._callback)
        self.data = None
        self.maxTextLength = 40
        self.dialog_title = 'Select ground truth file'
        self.file_filter = '*.yml'
        self.hooks = []
        #self.init_dir = os.getcwd()
        self.init_dir = '/media/Trinity/xatr-ssam2/GT'

        layout.addWidget(self.label)
        layout.addWidget(self.button)
    
    def setValue(self, dirName):
        self.data = dirName
        if len(dirName) > self.maxTextLength:
            dirPath, fn = osp.split(dirName)
            if (len(fn) > self.maxTextLength):
                dirName = '...'+fn[-self.maxTextLength+3:]
            else:
                remainder = self.maxTextLength - len(fn) - 4
                if remainder > 0:
                    dirName = osp.join(dirPath[:remainder]+'...', fn)
                else:
                    dirName = fn
        self.button.setText(dirName)
        return

    def _callback(self):
        selection = QFileDialog.getOpenFileName(
            self, self.dialog_title, self.init_dir, self.file_filter)[0]
        if selection == '':
            print('Empty Selection')
            return
        self.setValue(selection)
        
        for func in self.hooks:
            func(self)

        return
    
    def addHook(self, func):
        self.hooks.append(func)


class UiFolderSelect(QWidget):
    def __init__(self, title):
        super().__init__()
        layout = QHBoxLayout(self)
        self.button = QPushButton('', self)
        self.label = QLabel(title)
        self.button.clicked.connect(self._callback)
        self.data = None
        self.maxTextLength = 40
        self.dialog_title = 'Select Data Directory'
        self.hooks = []
        
        layout.addWidget(self.label)
        layout.addWidget(self.button)
    
    def setValue(self, dirName):
        self.data = dirName
        if len(dirName) > self.maxTextLength:
            dirPath, fn = osp.split(dirName)
            if (len(fn) > self.maxTextLength):
                dirName = '...'+fn[-self.maxTextLength+3:]
            else:
                remainder = self.maxTextLength - len(fn) - 4
                if remainder > 0:
                    dirName = osp.join(dirPath[:remainder]+'...', fn)
                else:
                    dirName = fn
        self.button.setText(dirName)
        return

    def _callback(self):
        dir_name = QFileDialog.getExistingDirectory(
            self, self.dialog_title, os.getcwd())
        dir_name = QDir.toNativeSeparators(dir_name)
        self.setValue(dir_name)

        for func in self.hooks:
            func(self)

        return
    
    def addHook(self, func):
        self.hooks.append(func)


class IoPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        self.source = UiFileSelect('GT File:')
        self.data = UiFolderSelect('Data Location:')

        layout.addWidget(self.source)
        layout.addWidget(self.data)


class Canvas(FigureCanvas):
    def __init__(self, parent=None, width= 300, height= 300):
        self._keyModifier = None
        self._actionClick = {}
        fig = Figure(figsize=(width, height))
        self.axes = fig.add_subplot(111)
        self.spread = None  # 400
        #self.cmap = 'copper'
        self.cmap='pink'
        self.aspect = 'auto'
        self.baseScale = 2.0
        self.xlim = [0, 0]
        self.ylim = [0, 0]
        self.yoffset = 0
        self.clickPos = None
        self.point = None
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.setFocusPolicy(Qt.ClickFocus)

        self.figure.canvas.mpl_connect('scroll_event', self.eventZoom)
        self.figure.canvas.mpl_connect('key_press_event', self.eventKeyPress)
        self.figure.canvas.mpl_connect('key_release_event', self.eventKeyRelease)
        self.figure.canvas.mpl_connect('button_press_event', self.eventClicked)

        return
    
    def addClickAction(self, mod, action):
        self._actionClick[mod] = action
        pass
    
    def eventKeyPress(self, event):
        if event.key in self._actionClick:
            self._keyModifier = event.key
        else:
            self._keyModifier = None
        return
    
    def eventKeyRelease(self, event):
        self._keyModifier = None
        
    def eventClicked(self, event):
        if not event.xdata:
            return
        # print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
        #       ('double' if event.dblclick else 'single', event.button,
        #        event.x, event.y, event.xdata, event.ydata))
        
        if event.dblclick:
            return
        if not event.button==1:
            return
        
        if self._keyModifier:
            self.clickPos = (event.xdata, event.ydata)
            self._actionClick[self._keyModifier](self)

        return

    def eventZoom(self, event):
        cur_xlim = self.axes.get_xlim()
        cur_ylim = self.axes.get_ylim()
        cur_xrange = (cur_xlim[1] - cur_xlim[0])*.5
        cur_yrange = abs(cur_ylim[1] - cur_ylim[0])*.5
        xdata = event.xdata # get event x location
        ydata = event.ydata # get event y location
        if event.button == 'up':  # Zoom in
            scale_factor = 1/self.baseScale
        elif event.button == 'down':  # Zoom out
            scale_factor = self.baseScale
        else:  # No zoom
            scale_factor = 1

        # set new limits
        ylower = max(0, ydata-cur_yrange*scale_factor)
        yupper = min(self.ylim[1]-self.ylim[0], ydata+cur_yrange*scale_factor)
        self.axes.set_xlim([
            max(self.xlim[0], xdata-cur_xrange*scale_factor),
            min(self.xlim[1], xdata+cur_xrange*scale_factor)])
        self.axes.set_ylim([ylower, yupper])
        self.draw()
        return

    def show(self, inp, x, y):
        img = inp.data('HF')['abs']
        print(img.shape)
        img = img - np.min(img)
        img = img / np.mean(img)
        img = np.clip(img, 0, 16)
	# These functions are not complete
        #img = matsui.graphics.clip_image(img)
        #img = matsui.graphics.imadjust(img, [0.001, 0.70], None, 1.0)
        if self.spread is not None:
            lower = max(0, y-self.spread)
            upper = min(img.shape[0], y+self.spread)
        else:
            lower = 0
            upper = img.shape[0]
        print('Image along-track index range: {} to {}'.format(lower, upper))
        self.axes.clear()
        self.axes.imshow(
            img[lower:upper, :],
            cmap=self.cmap,
            aspect=self.aspect,
            #vmax=0.08
        )
        self.point, = self.axes.plot(x, y-lower, 'bo')
        self.draw()
        
        self.xlim = [0, img.shape[1]]
        self.ylim = [lower, upper]
        self.yoffset = lower
        return
    
    def blank(self):
        self.axes.clear()
        self.axes.imshow(
            np.zeros((10,10)),
            cmap=self.cmap,
            aspect=self.aspect,
            #vmax=0.08
        )
       
        self.draw()
        
       


class GtTable(QTableWidget):
    def __init__(self):
        super().__init__()
        self.headers = {
            'Act': 0, 'X': 1, 'Y': 2, 'Side': 3, 'ID': 4, 'Type': 5,
            'Filename': 6, 'Note': 7
        }
        
        self.data_location = None
        self.gt = []
        self.hooks = []

        self.setColumnCount(len(self.headers))
        self.setHorizontalHeaderLabels(list(self.headers.keys()))
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setFixedWidth(600)
        for colname in self.headers:
            if colname == 'Filename':
                self.horizontalHeader().setSectionResizeMode(
                    self.headers[colname], QHeaderView.Stretch
                )
            else:
                self.horizontalHeader().setSectionResizeMode(
                    self.headers[colname], QHeaderView.ResizeToContents
                )
        self.clicked.connect(self.clickedGt)
        self.cellChanged.connect(self.onCellChanged)
        return
    
    def getSelection(self):
        if not self.data_location:
            Warn('"data_location" not set for GtTable')
        print(self.selectedIndexes())
        ix = self.selectedIndexes()[0]
        return self.gt[ix.row()]
    
    def updateSelection(self, x, y):
        if not self.data_location:
            Warn('"data_location" not set for GtTable')
        ix = self.selectedIndexes()[0]
        xitem = QTableWidgetItem(str(int(x)))
        xitem.setTextAlignment(Qt.AlignHCenter)
        yitem = QTableWidgetItem(str(int(y)))
        yitem.setTextAlignment(Qt.AlignHCenter)
        self.setItem(ix.row(), self.headers['X'], xitem)
        self.setItem(ix.row(), self.headers['Y'], yitem)
        self.gt[ix.row()]['x'] = int(x)
        self.gt[ix.row()]['y'] = int(y)
        return

    def clickedGt(self):
        if not self.data_location:
            Warn('"data_location" not set for GtTable')
        for func in self.hooks:
            func(self)
        return

    def addGt(self, gt):
        rx = self.rowCount()
        
        act = QTableWidgetItem()
        act.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        if 'enabled' in gt:
            if gt['enabled']:
                act.setCheckState(Qt.Unchecked)
            else:
                act.setCheckState(Qt.Checked)
        else:
            act.setCheckState(Qt.Unchecked)

        x = QTableWidgetItem(str(gt['x']))
        x.setTextAlignment(Qt.AlignHCenter)
        y = QTableWidgetItem(str(gt['y']))
        y.setTextAlignment(Qt.AlignHCenter)
        side = QTableWidgetItem(gt['side'])
        side.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        side.setTextAlignment(Qt.AlignHCenter)
        num = QTableWidgetItem(str(gt['num']))
        num.setTextAlignment(Qt.AlignHCenter)
        tid = QTableWidgetItem(str(gt['type']))
        tid.setTextAlignment(Qt.AlignHCenter)
        fn = QTableWidgetItem(gt['fn'])
        fn.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        fn.setTextAlignment(Qt.AlignLeft)
        
        if 'note' in gt:
            note = QTableWidgetItem(gt['note'])
        else:
            note = QTableWidgetItem('')
        note.setTextAlignment(Qt.AlignLeft)
            
        self.insertRow(rx)
        self.setItem(rx, self.headers['Act'], act)
        self.setItem(rx, self.headers['X'], x)
        self.setItem(rx, self.headers['Y'], y)
        self.setItem(rx, self.headers['Side'], side)
        self.setItem(rx, self.headers['ID'], num)
        self.setItem(rx, self.headers['Type'], tid)
        self.setItem(rx, self.headers['Filename'], fn)
        self.setItem(rx, self.headers['Note'], note)

        return
    
    
#    @pyqtSlot(int, int)
    def onCellChanged(self, row, column):
        print(row, column)
        
        text = self.item(row, column).text()
        
        if column == 7:
            self.gt[row]['note'] = text
        
        
        

    def loadGt(self, filename):
        self.blockSignals(True)
        #self.gt = mats.gt.read_txt(filename)
        self.gt = mats.gt.read_yml(filename)
        self.gt_filename = filename
        #self.gt = mats.core.gt_read(filename)
        #self.gt = mats.generic_gt_reader(filename)
        print('Loaded {} GT locations'.format(len(self.gt)))
        for gt in self.gt:
            self.addGt(gt)
            
        self.blockSignals(False)
        
        
        
        return

    def saveGt(self):
        tmp_split = osp.splitext(self.gt_filename)
        new_filename = tmp_split[0] + '_new' + tmp_split[1]
        new_ymlname = tmp_split[0] + '_new' + '.yml'
        #mats.gt.write_txt(new_filename, self.gt)
        mats.gt.write_yml(new_ymlname, self.gt)
    
    def addHook(self, func):
        self.hooks.append(func)
        return


class GtReview(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'GT Review'
        self.left = 300
        self.right = 300
        self.width = 1000
        self.height = 600
        
        mats.pkg.scan()
        self.rdr = mats.pkg.create('rdrMSHDF')
        self.rdr.configure(mats.Struct())
        self.data = None
        self.data_location = None
        self.file_list = None

        self.initUI()
    
    def initUI(self):
        self.setGeometry(self.left, self.right, self.width, self.height)
        self.setWindowTitle(self.title)
        
        # Exit
        exitAct = QAction(QIcon('Button-Close-icon.png'), 'Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(self.close)
        
        # Save
        saveAct = QAction('Save', self)
        saveAct.setShortcut('Ctrl+S')
        saveAct.setStatusTip('Save GT')
        saveAct.triggered.connect(self.saveGt)

        # Menu Bar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(saveAct)
        fileMenu.addAction(exitAct)
        
        self.mainwidget = QWidget()
        self.setCentralWidget(self.mainwidget)
        self.main_layout = QHBoxLayout(self.mainwidget)
        
        self.leftpanel = QVBoxLayout()
        self.rightpanel = QVBoxLayout()
        
        self.main_layout.addLayout(self.leftpanel)
        self.main_layout.addLayout(self.rightpanel)
        
        self.iopanel = IoPanel()
        self.iopanel.source.addHook(self.loadGt)
        self.iopanel.data.addHook(self.setDataLocation)
        self.table = GtTable()
        self.table.addHook(self.loadData)
        self.leftpanel.addWidget(self.iopanel)
        self.leftpanel.addWidget(self.table)
        
        self.canvas = Canvas(self)
        self.canvas.addClickAction('shift', self.moveGt)
        self.rightpanel.addWidget(self.canvas)
        
        self.current_selection = None
        
        
        self.show()
    
    def moveGt(self, src):
        src.point.set_xdata(src.clickPos[0])
        src.point.set_ydata(src.clickPos[1])
        x = np.round(src.clickPos[0])
        y = np.round(src.clickPos[1]+src.yoffset)
        src.draw()
        self.table.updateSelection(x,y)
        return
    
    def saveGt(self, event):
        self.table.saveGt()
        print('Saving')
        return

    def loadGt(self, src):
        print('GT File: {}'.format(src.data))
        self.table.loadGt(src.data)
        
        #data_path = osp.dirname(src.data)
        
        gt_path = Path(src.data)
        data_path = gt_path.parents[2] / ('SSAM2/' + gt_path.stem.replace('_new', ''))
        data_path = str(data_path)
        
        
        self.table.data_location = data_path
        self.iopanel.data.setValue(data_path) # update button
        
        self.table.selectRow(0)
        
    def setDataLocation(self, src):
        print('Data Location: {}'.format(src.data))
        self.table.data_location = src.data
    
    def loadData(self, src):
        gt = src.getSelection()
        print(gt)
        
        if self.current_selection != gt:
            
            self.current_selection = gt

            fn = osp.join(src.data_location, gt['fn'])
            if not os.path.exists(fn):
                if self.file_list is None:
                    self.file_list = scan_dir(src.data_location)
                fn = file_list_search(gt['fn'], self.file_list)
                if fn is None:
                    print('File does not exist')
                    #raise FileNotFoundError
                    self.canvas.blank()
                    return
                    
            print('Data Filename: {}'.format(fn))
            self.data = self.rdr.read(fn)
    
            if len(self.data) > 1 and gt['side'] == 'STBD':
                data = self.data[1]
            else:
                data = self.data[0]
            x = gt['x']
            y = gt['y']
            
            self.canvas.show(data, x, y)
            
            
        return


def scan_dir(src):
    fileList = []
    for path, _, files in os.walk(src):
        for fn in files:
            fileList.append({'name': fn, 'path': path})
    return fileList


def file_list_search(filename, fileList):
    return next((os.path.join(file['path'], filename) for file in fileList if file["name"] == filename), None)
