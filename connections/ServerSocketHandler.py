#coding=utf-8
#A class to handle socket-related services, including a UDP server
import socket
import threading
import time
from utils import DataTypeHandler
from utils.parsers import EventXMLParser, BooleanClsParser, StreamDataParser, osc_message
from models import UniteModel, BinaryData
import cPickle
from models.netdata import HugePackage

class ServerUDPReceiver(threading.Thread):

    def __init__(self, exportQueue, iAddress = '', port = 1234):
        threading.Thread.__init__(self)
        self.exportQueue = exportQueue
        #输出到处理中心的队列
        self.PORT = port
        self.IADDRESS = iAddress
        self.BUFFERSIZE = 10240
        self.udpServSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        addr = (self.IADDRESS, self.PORT)
        self.udpServSock.bind(addr)
        self.should_stop = False
        self.echo_only = True       # 只接受Echo信息

        print 'A ServerUDPReceiver instance has been created.(%s)' %str(self.PORT)

    # def __del__(self):
    #     self.udpServSock.close()
    #     print 'Connection closed.\nA SocketHandler instance has been removed.'

    def run(self):
        #Initialize UDP server
        while not self.should_stop:
            data, srcAddr = self.udpServSock.recvfrom(self.BUFFERSIZE)
            print 'Received data from %s' %str(srcAddr[0])
            data_type = DataTypeHandler.determine_data_type(data)
            print 'length %d, data type %d' %(len(data), data_type)
            timestamp = int(time.time())

            #continue
            #Push data to exportQueue

            # if data_type == DataTypeHandler.DATA_TYPE_BIN:
            #     osc_msg = osc_message.OscMessage(data)
            #     modelData = StreamDataParser.parse_stream_to_model(osc_msg, srcAddr[0], timestamp)#BinaryData.BinaryData(timestamp, srcAddr[0], data)
            if data_type == DataTypeHandler.DATA_TYPE_ECHO:
                modelData = srcAddr[0]    # ECHO消息的modelData为发送人的IP
            elif data_type == DataTypeHandler.DATA_TYPE_CLS:
                if self.echo_only:
                    print 'ECHO ONLY.'
                    continue
                osc_msg = osc_message.OscMessage(data)
                modelData = BooleanClsParser.parse_cls_to_clsdata(osc_msg, timestamp, srcAddr[0])
            # elif data_type == DataTypeHandler.DATA_TYPE_XML:
            #     modelData = EventXMLParser.parse_xml_to_event(data, timestamp, srcAddr[0])

            else:
                print 'ERROR: UNKNOWN DATA TYPE %d' % data_type
                continue

            model = UniteModel.UniteModel(data_type, modelData)
            self.exportQueue.put(model)
            self.exportQueue.task_done()
            #print 'Queue size = %d' %(self.exportQueue.qsize())

    def stop(self):
        self.should_stop = True
        self.udpServSock.close()
        print 'Connection closed.\tA SrvUDPRcv instance has been removed.'


class ServerUDPSender(threading.Thread):
    '''服务器向客户端发送'''
    def __init__(self, importQueue, targetPort = 2345):
        threading.Thread.__init__(self)
        self.importQueue = importQueue
        self.should_stop = False
        self.targetPort = targetPort
        print 'A ServerUDPSender instance has been created.(%s)' %str(self.targetPort)

    def run(self):
        while not self.should_stop:
            if self.importQueue.empty():
                continue
            hugePkg = self.importQueue.get()
            print 'I`ve got something...'

            if isinstance(hugePkg, HugePackage):
                for ip in hugePkg.statDataDict:
                #建立Socket连接，发还数据给客户端
                #p = participants[ip]
                    address = (ip, self.targetPort)
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    p_pickle = cPickle.dumps(hugePkg)  #用cPickle序列化,发送所有人的资料！
                    s.sendto(p_pickle, address)
                    s.close()
            elif isinstance(hugePkg, list):
                print 'Sending restart package to everyone...'
                for ip in hugePkg:
                    print ip
                    fakePkg = HugePackage(None, None)
                    address = (ip, self.targetPort)
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    p_pickle = cPickle.dumps(fakePkg)  #用cPickle序列化,发送所有人的资料！
                    s.sendto(p_pickle, address)
                    s.close()
            else:
                print 'ServerUDPSender: what`s this shit?!'





    def stop(self):
        self.should_stop = True
        print 'Connection closed.\tA SrvUDPSen instance has been removed.'
        #TODO:sth