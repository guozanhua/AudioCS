#coding:utf-8
from PyQt4 import QtGui, QtCore

class MetreHandLabel(QtGui.QLabel):
    def __init__(self, parent, centre_pos):
        QtGui.QLabel.__init__(self, parent)
        self.cent_pos = centre_pos  # 控件中心位置
        self.img = QtGui.QPixmap('D:/Python/AudioCS/resources/hand_of_emometre_f.png')
        #self.refresh_img()
        self.rotate_angle = 0.0

    def rotate(self, angle):
        #self.img = self.img.transformed(QtGui.QTransform().rotate(angle))
        self.rotate_angle += angle
        self.update()

    def rotate_to(self, angle):
        self.rotate_angle = angle
        self.update()

    def refresh_img(self):
        self.setPixmap(self.img)

    def get_geometry(self):
        ''' 获得旋转后的坐标位置 '''
        print '%d, %d' %(self.img.width(), self.img.height())

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.translate(60, 60)
        painter.rotate(self.rotate_angle)
        painter.translate(-60, -60)

        painter.drawPixmap(0, 0, 120, 120, self.img)