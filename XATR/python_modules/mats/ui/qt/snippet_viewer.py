import os
import numpy as np
import mats

from PyQt5.QtWidgets import (QWidget, QPushButton, QSizePolicy, QHBoxLayout)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mats.ui.qt.common import DirDialog

ARCHIVE_ROOT = os.path.expanduser('~/Downloads')


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(
            self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class SnippetCanvas(MyMplCanvas):
    def compute_initial_figure(self):
        t = np.arange(0.0, 3.0, 0.01)
        s = np.sin(2*np.pi*t)
        self.axes.plot(t, s)

    def update_figure(self, img):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        self.axes.cla()
        self.axes.imshow(img, cmap='pink')
        self.draw()

    def set_title(self, tit):
        self.axes.set_title(tit, fontsize=8)
        self.draw()


class SnippetViewerPopup(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.mainwindow = parent
        self.idx = 0
        self.current_ind = 0
        self.initUI()

    def initUI(self):
        # self.setGeometry(300, 300, 640, 400)
        self.sc = SnippetCanvas(self, width=5, height=4, dpi=100)

        button = QPushButton('Set Archive Dir(s)', self)
        button.setToolTip('Archive directory where snippets are located')
        # button.move(500,0)
        # button.resize(140,100)
        button.pressed.connect(self.select_dirs)

        hbox = QHBoxLayout()

        hbox.addWidget(self.sc)
        hbox.addWidget(button)

        # This makes qt detect arrow keys
        self.setFocusPolicy(Qt.StrongFocus)

        self.setLayout(hbox)

        self.show()

    def select_dirs(self):
        dir_list = ''
        dir_dialog = DirDialog(self, 'Select directory', ARCHIVE_ROOT)
        if dir_dialog.exec_():
            dir_list = dir_dialog.get_dirlist()

        if dir_list != '':
            self.dir_list = dir_list
            self.update_archive_files(dir_list)

    def update_archive_files(self, dir_list):
        arc_files = []
        for arc_dir in dir_list:
            arc_files += self.find_arc_files(arc_dir)

        self.arc_files = arc_files

        self.snippets_hf, self.snippets_bb, self.labels, self.cls_conf = self.get_snippets(self.arc_files)

        self.pos_inds = np.nonzero(self.labels == True)[0]
        self.neg_inds = np.nonzero(self.labels == False)[0]

        self.snippets = self.snippets_hf

        self.sc.update_figure(self.snippets[0])

    def get_snippets(self, arc_files):
        # snippets = []
        snippets_bb = []
        snippets_hf = []
        labels = []
        cls_conf = []

        arc = mats.Archive()

        print('loading snippets')
        for ii, arc_file in enumerate(arc_files):
            if ii % 100 == 0:
                print(f'{ii} / {len(arc_files)}')
            arc.load(arc_file)
            ecds = arc.ecdata()
            cons = arc.contact()
            for con, ecd in zip(cons, ecds):
                snippets_hf.append(np.abs(ecd.snippet('HF')['data']))
                snippets_bb.append(np.abs(ecd.snippet('BB')['data']))
                labels.append(con['gt'])
                cls_conf.append(con['classconf'])

        print(f'{ii} / {len(arc_files)}')
        return snippets_hf, snippets_bb, np.array(labels), np.array(cls_conf)

    def find_arc_files(self, source_dir_name):
        root_dir = source_dir_name

        h5_filelist = []
        for root, _, filelist in os.walk(root_dir, topdown=False):
            for fname in filelist:
                if os.path.splitext(fname)[1] == '.h5':
                    h5_filelist.append(root + '/' + fname)
        return h5_filelist

    def keyPressEvent(self, k):
        # print (f'button pressed: {k}')

        if k.key() == Qt.Key_Left:
            # print('left button')
            # self.idx -= 1
            self.current_ind -= 1

        if k.key() == Qt.Key_Right:
            # print('right button')
            # self.idx += 1
            self.current_ind += 1

        if k.key() == Qt.Key_Down:
            self.snippets = self.snippets_bb

        if k.key() == Qt.Key_Up:
            self.snippets = self.snippets_hf

        self.idx = self.pos_inds[self.current_ind]
        self.sc.update_figure(self.snippets[self.idx])
        tit = '#' + str(self.idx) + '     ind = ' + str(self.current_ind) + '    label = ' + str(self.labels[self.idx]) \
                  + '     pred = ' + str(self.cls_conf[self.idx])
        self.sc.set_title(tit)
