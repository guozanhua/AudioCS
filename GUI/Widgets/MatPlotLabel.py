#coding:utf-8
''' 绘图结果用的label
'''
from PyQt4 import QtGui
import CusSettings


class MatPlotLabel(QtGui.QLabel):
    def __init__(self, parent):
        QtGui.QLabel.__init__(self, parent)
        self.img_path = CusSettings.CURRENT_PATH + 'resources/output_fig_def.png'
        self.img = QtGui.QPixmap(self.img_path)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(0, 0, self.img)

    def set_img_buffer(self, str_io_buffer):
        qimg = QtGui.QImage.fromData(str_io_buffer.getvalue())
        self.img = QtGui.QPixmap.fromImage(qimg)
        self.update()  # call paintEvent

    def set_img(self, path):
        self.img_path = path
        self.img = QtGui.QPixmap(self.img_path)
        self.update()