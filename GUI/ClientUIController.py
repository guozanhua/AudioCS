#coding:utf-8
'''GUI总管大臣，管理UI的东西'''
from ClientGUI import ClientUserGUI
from connections import ClientSocketHandler, ClientDataConsumer
from PyQt4 import QtGui
import sys
import Queue

class ClientUIController(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.num_clients = 0
        self.client_UIs = {}    # One UI for each user, {IP, ui}
        self.summary_UI = None  # Summary UI

        self.inQueue = Queue.Queue()
        self.c = None
        self.data_consumer = None


        self.infoLabel  = QtGui.QLabel()
        self.infoLabel.setText('Blabla...')
        self.setCentralWidget(self.infoLabel)

        self.init_threads()

    def init_threads(self):
        # 开启各种线程
        ip = '127.0.0.1'
        self.c = ClientSocketHandler.ClientSocketReceiver(self.inQueue, ip)     # Socket Thread

        self.data_consumer = ClientDataConsumer.ClientQtDataConsumer(self.inQueue)
        self.data_consumer.data_got.connect(self.put_data)

        self.c.start()
        self.data_consumer.start()


    def has_client(self, ip):
        # 判断是否已经有这个IP对应的UI了
        return self.client_UIs.has_key(ip)

    def add_client(self, ip):
        # 增加一个客户端的UI
        self.client_UIs[ip] = ClientUserGUI()
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
                self.add_client(ip)
                print 'Participant %s added.' % ip
            # 把消息放进去
            emo_value = p.latest_pos_val
            print 'emo_val=%f' % emo_value
            self.client_UIs[ip].rotate_to_value(emo_value)
            timestamp = p.latest_timestamp
            self.client_UIs[ip].append_emo_state(timestamp, emo_value)
            
            #TODO:...SUMMARY GUI




if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ctrlGUI = ClientUIController()
    ctrlGUI.show()
    sys.exit(app.exec_())