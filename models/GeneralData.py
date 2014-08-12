#coding:utf-8
class GeneralData:
    '''通用数据类型'''

    def __init__(self, timestamp, senderip):
        self.timestamp = timestamp #事件发生的时间戳(Socket收发时间)
        self.senderip = senderip #发送者IP

