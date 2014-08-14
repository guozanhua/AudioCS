#coding:utf-8
from connections import ClientSocketHandler, ClientDataConsumer
from GUI.ClientUIController import ClientUIController
import Queue
from time import sleep
from PyQt4 import QtGui
import sys

app = QtGui.QApplication(sys.argv)

inQueue = Queue.Queue()
ip = '127.0.0.1'
c = ClientSocketHandler.ClientSocketReceiver(inQueue, ip)
c.start()
uiCtrl = ClientUIController()
uiCtrl.show()
c_consumer = ClientDataConsumer.ClientDataConsumer(inQueue, uiCtrl)
c_consumer.start()

#sleep(4800)
app.exec_()  # 进入主线程循环
c.stop()
c_consumer.stop()