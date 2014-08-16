#coding:utf-8
'''客户端吃消息的东西，需要掌握GUI的操纵大权'''

import threading
from PyQt4 import QtGui, QtCore
import sys

class ClientQtDataConsumer(QtCore.QThread):
    '''新的Consumer 使用QThread，当拿到东西后会给ClientUIController发送信号'''
    data_got = QtCore.pyqtSignal(object)

    def __init__(self, inQueue):
        QtCore.QThread.__init__(self)
        self.inQueue = inQueue
        self.shouldStop = False
        print 'ClientQtDataConsumer start...'

    def run(self):
        while not self.shouldStop:
            if self.inQueue.empty():
                continue
            print 'ClientDataConsumer: Got sth.'
            participants = self.inQueue.get()
            self.data_got.emit(participants)    # emit!!!


    def stop(self):
        self.shouldStop = True
        print 'ClientQtDataConsumer quit'
        #quit()




class ClientDataConsumer(threading.Thread):
    def __init__(self, importQueue, uiController):
        threading.Thread.__init__(self)
        self.importQueue = importQueue      #输入的Queue，里面是一个个participants
        self.uiController = uiController    #界面控制器，里面有能够更新某个界面的函数接口
        self.shouldStop = False

    def run(self):

        while not self.shouldStop:
            if self.importQueue.empty():
                continue
            print 'ClientDataConsumer: Got sth.'
            participants = self.importQueue.get()  #得到的是列表[Participant]
            #TODO: DEAL WITH DATA AND USE UI_CONTROLLER TO UPDATE UI
            self.uiController.put_data(participants)



    def stop(self):
        self.shouldStop = True



