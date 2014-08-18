#coding:utf-8
'''客户端Socket相关的东西'''
import threading
import socket
import cPickle
from models.Participant import Participant

class ClientSocketReceiver(threading.Thread):
    def __init__(self, exportQueue, iAddress, port=2345):
        threading.Thread.__init__(self)
        self.exportQueue = exportQueue
        address = (iAddress, port)
        self.udpClientServ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpClientServ.bind(address)
        self.should_stop = False
        self.BUFFERSIZE = 10240

        print 'A ClientUDPReceiver instance has been created.(%s)' %str(port)

    def run(self):
        while not self.should_stop:
            data, srcAddr = self.udpClientServ.recvfrom(self.BUFFERSIZE)
            print 'Received data from %s' %str(srcAddr[0])


            participants = cPickle.loads(data)  #INFO:收到的是所有人的数据
            print participants
            self.exportQueue.put(participants)


    def stop(self):
        self.should_stop = True
        self.udpClientServ.close()
        print 'Connection closed.\tA ClientUDPRcv instance has been removed.'
