#coding:utf-8
'''GUI总管大臣，管理UI的东西'''
from ClientGUI import ClientUserGUI, ClientSummaryGUI
from connections import ClientSocketHandler, ClientDataConsumer
from PyQt4 import QtGui, QtCore
from win32api import GetSystemMetrics
import sys
import Queue
import socket
import os
import CusSettings

class ClientUIController(QtGui.QWidget):
    CLIENT_UI_POS_X = [0.10, 0.46, 0.77, 0.39]  # 相对坐标
    CLIENT_UI_POS_Y = [0.11, 0.11, 0.11, 0.60]

    def __del__(self):
        self.c.stop()
        self.data_consumer.stop()
        self.data_consumer.quit()

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.num_clients = 0
        self.client_UIs = {}    # One UI for each user, {IP, ui}


        self.screen_resolution = (GetSystemMetrics(0), GetSystemMetrics(1))
        print 'Screen resolution :%dx%d' % (self.screen_resolution[0], self.screen_resolution[1])

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

        self.summary_UI = ClientSummaryGUI(init_position=
                                           (self.screen_resolution[0]*0.67, self.screen_resolution[1]*0.59))  # Summary UI
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
                                     , self.socket_text, text='10.214.143.')
        if ok:
            ip = text
        else:
            ip = '192.168.1.200'
        print 'Host IP address set to: %s' %ip

        currPath = os.getcwd().replace('\\','/') + '/'
        # text, ok = QtGui.QInputDialog.getText(self, 'Current path', 'Enter current path',
        #                                       text=currPath)
        CusSettings.CURRENT_PATH = currPath
        print 'Execution path set to: %s' % currPath


        self.c = ClientSocketHandler.ClientSocketReceiver(self.inQueue, ip)     # Socket Thread

        self.data_consumer = ClientDataConsumer.ClientQtDataConsumer(self.inQueue)
        #self.data_consumer.data_got.connect(self.put_data)
        self.data_consumer.stat_data_got.connect(self.put_stat_data)
        self.data_consumer.incr_data_got.connect(self.put_incr_data)

        self.c.start()

        self.data_consumer.start()

        text, ok = QtGui.QInputDialog.getText(self, 'Input SERVER ip address'
                                     , 'Input SERVER ip address, it`s NOT your own ip...'
                                , text='10.214.143.220')
        if ok:
            ip = text
        else:
            ip = '10.214.143.220'
        print 'Server IP address set to: %s' %ip
        self.send_echo_to_server(server_ip=text)


    def send_echo_to_server(self, server_ip):
        address = (server_ip, 1234)  # port number 1234
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto('/echo', address)
        s.close()
        print 'echo message sent to %s' % server_ip


    def has_client(self, ip):
        # 判断是否已经有这个IP对应的UI了
        return self.client_UIs.has_key(ip)

    def add_client(self, ip, nickname=None):
        # 增加一个客户端的UI
        client_count = len(self.client_UIs)     # 根据当前客户端的数量设定初始位置(有待进一步修改)
        pos_x = self.CLIENT_UI_POS_X[client_count-1] * self.screen_resolution[0]
        pos_y = self.CLIENT_UI_POS_Y[client_count-1] * self.screen_resolution[1]

        self.client_UIs[ip] = ClientUserGUI(ip=ip, nickname=nickname, init_position=(pos_x, pos_y))
        self.client_UIs[ip].show()

        print 'A new ui instance created.'

    def remove_client(self, ip):
        self.client_UIs[ip].close()
        del self.client_UIs[ip]

    def put_stat_data(self, statDataDict):
        # 统计信息
        p_length = len(statDataDict)
        if p_length < 1:
            print '[ERROR] NO VALID PARTICIPANT'
            return
        for ip, p in statDataDict.iteritems():
            if not self.has_client(ip):
                self.add_client(ip, nickname=p.nickname)
                print 'Participant %s added.' % ip
        self.summary_UI.make_graph(statDataDict)
        self.summary_UI.draw_graph()

    def put_incr_data(self, incrData):
        # 增量信息
        ip = incrData.ip
        pos_val = incrData.pos_val
        timestamp = incrData.timestamp
        print 'emo_val=%f' % pos_val
        self.client_UIs[ip].rotate_to_value(pos_val)
        self.client_UIs[ip].append_emo_state(timestamp, pos_val)
        self.client_UIs[ip].plot_timeline()

    #ABANDONED
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