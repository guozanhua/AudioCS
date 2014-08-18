#coding:utf-8
'''GUI总管大臣，管理UI的东西'''
from ClientGUI import ClientUserGUI, ClientSummaryGUI
from connections import ClientSocketHandler, ClientDataConsumer
from PyQt4 import QtGui, QtCore
import sys
import Queue
import socket
import os
import CusSettings

class ClientUIController(QtGui.QWidget):
    def __del__(self):
        self.c.stop()
        self.data_consumer.stop()
        self.data_consumer.quit()

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.num_clients = 0
        self.client_UIs = {}    # One UI for each user, {IP, ui}
        self.summary_UI = ClientSummaryGUI()  # Summary UI

        self.inQueue = Queue.Queue()
        self.c = None
        self.data_consumer = None

        self.vbox = QtGui.QVBoxLayout()

        self.vbox.addStretch(2)
        self.infoLabel = QtGui.QLabel()
        self.socket_text = str(socket.gethostbyname_ex(socket.gethostname()))
        self.infoLabel.setText(self.socket_text)
        self.vbox.addWidget(self.infoLabel)
        self.vbox.addStretch(2)

        self.setLayout(self.vbox)



        self.init_threads()

        self.summary_UI.show()

    def mouseDoubleClickEvent(self, *args, **kwargs):
        print 'QUIT...'
        for ip, client in self.client_UIs.iteritems():
            client.close()
        self.c.stop()
        self.data_consumer.stop()
        self.summary_UI.close()
        self.close()
        QtCore.QCoreApplication.instance().quit()


    def init_threads(self):
        # 开启各种线程

        text, ok = QtGui.QInputDialog.getText(self, 'Input your current ip address'
                                     , self.socket_text , text='192.168.1.200')
        if ok:
            ip = text
        else:
            ip = '192.168.1.200'
        print 'Host IP address set to: %s' %ip

        currPath = os.getcwd().replace('\\','/') + '/'
        text, ok = QtGui.QInputDialog.getText(self, 'Current path', 'Enter current path',
                                              text=currPath)
        if ok:
            CusSettings.CURRENT_PATH = text
        print 'Execution path set to: %s' %text


        self.c = ClientSocketHandler.ClientSocketReceiver(self.inQueue, ip)     # Socket Thread

        self.data_consumer = ClientDataConsumer.ClientQtDataConsumer(self.inQueue)
        self.data_consumer.data_got.connect(self.put_data)

        self.c.start()
        self.data_consumer.start()


    def has_client(self, ip):
        # 判断是否已经有这个IP对应的UI了
        return self.client_UIs.has_key(ip)

    def add_client(self, ip, nickname=None):
        # 增加一个客户端的UI
        self.client_UIs[ip] = ClientUserGUI(ip=ip, nickname=nickname)
        self.client_UIs[ip].show()
        #sys.exit(self.app.exec_())
        #self.app.exec_()
        print 'A new ui instance created.'

    def remove_client(self, ip):
        self.client_UIs[ip].close()
        del self.client_UIs[ip]

    def put_data(self, participants):
        ''' 从远方来的消息往这里塞 '''
        p_length = len(participants)
        if p_length < 1:
            print '[ERROR] NO VALID PARTICIPANT'
            return
        for ip, p in participants.items():

            if not self.has_client(ip):
                self.add_client(ip, nickname=p.nickname)
                print 'Participant %s added.' % ip
            # 把消息放进去
            emo_value = p.latest_pos_val
            print 'emo_val=%f' % emo_value
            self.client_UIs[ip].rotate_to_value(emo_value)
            timestamp = p.latest_timestamp
            self.client_UIs[ip].append_emo_state(timestamp, emo_value)
            self.client_UIs[ip].plot_timeline()
        #TODO:...SUMMARY GUI
        self.summary_UI.make_graph(participants)
        self.summary_UI.draw_graph()


def run_me():
    app = QtGui.QApplication(sys.argv)
    ctrlGUI = ClientUIController()
    ctrlGUI.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run_me()