#coding:utf-8
from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT

class MplCanvas(FigureCanvas):

    def __init__(self, figsize=(8, 6), dpi=80):
        self.fig = Figure(figsize=figsize, dpi=dpi)
        self.fig.subplots_adjust(wspace=0, hspace=0, left=0, right=1.0, top=1.0, bottom=0)

        self.ax = self.fig.add_subplot(111, frameon=False)
        self.ax.patch.set_visible(False)
        self.ax.set_axis_off()
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        #self.setAlpha(0.0)

    def saveFig(self, str_io_buf):
        self.setAlpha(0.0)
        self.fig.savefig(str_io_buf, transparent=True, frameon=False, format='png')
        # 140818 Save file to StringIO Buffer not disk file

    def getFig(self):
        return self.fig

    def setAlpha(self, value):
        self.fig.patch.set_alpha(value)
        self.ax.patch.set_alpha(value)
        self.ax.set_axis_off()

    def set_face_color(self, color):
        self.fig.set_facecolor(color)  # "#000000"

class matplotlibWidget(QtGui.QWidget):

    def __init__(self, parent = None, figsize=(8, 6), dpi=80):
        QtGui.QWidget.__init__(self, parent)
        self.canvas = MplCanvas(figsize=figsize, dpi=dpi)
        #self.canvas.ax.set_title("I-V Curve")
        #self.canvas.ax.set_xlabel("V")
        #self.canvas.ax.set_ylabel("I")
        #self.toolbar = NavigationToolbar2QT(self.canvas, None, True)
        self.vbl = QtGui.QVBoxLayout()
        self.vbl.addWidget(self.canvas)
        #self.vbl.addWidget(self.toolbar)
        self.setLayout(self.vbl)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)     # 鼠标穿透
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint|QtCore.Qt.WindowStaysOnTopHint)
        self.setAlpha(0.0)

    def setAlpha(self, value):
        self.canvas.setAlpha(value)

    def set_face_color(self, color):
        self.canvas.set_face_color(color)

    def clear(self):
        self.canvas.ax.clear()
        self.canvas.ax.patch.set_alpha(0.0)

    def saveFig(self, path='d:/output_fig.png'):
        self.canvas.saveFig(path)


