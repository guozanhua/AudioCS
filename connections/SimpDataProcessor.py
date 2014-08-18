#encoding:utf-8

''' 简化版的数据处理，只处理分类器结果的event数据 '''

import threading
from models.UniteModel import *
from models.Participant import *
from models.ClassifierData import *
from models.ConvContent import *
from utils.LogHandler import LogFileHandler
from utils.ConfigHandler import get_nicknames

class SimpleDataProcessor(threading.Thread):

    def __init__(self, importQueue, exportQueue):
        threading.Thread.__init__(self)
        self.importQueue = importQueue
        self.exportQueue = exportQueue
        self.shouldStop = False
        self.participants = {}  # 所有参与者的Hash表(IP, Participant)
        self.nicknames = get_nicknames() # {IP , Nickname}
        self.logHandler = LogFileHandler()

    def run(self):
        lastIP = None  # 上一个发送者的IP
        while not self.shouldStop:
            if self.importQueue.empty():
                continue

            #TODO: PROCESS DATA RIGHT HERE
            element = self.importQueue.get()
            print 'Incoming element >>> '
            if element.type != UniteModel.TYPE_CLASSIFY_RESULT:
                print 'DO NOT USE SimpDataProcessor WITHOUT TYPE_CLASSIFY_RESULT, DATA OMITTED!'
                continue
            cls_model = element.content

            #Write to log file
            self.logHandler.write_classifier_data(cls_model)

            ip = cls_model.senderip
            timestamp = cls_model.timestamp
            emoState = cls_model.result
            posRate = cls_model.positive_rate
            duration = cls_model.duration

            posdiff = 0
            negdiff = 0
            if emoState == ClassifierData.RESULT_POSITIVE:
                posdiff = 1
            else:
                negdiff = 1

            if not self.has_participant(ip):
                #如果没有这个参与者，则新建一条记录
                participant = Participant(ip, duration, posdiff, negdiff)
                participant.latest_pos_val = posRate  # 判断为positive的rate
                self.participants[ip] = participant
            else:
                #如果有记录，则在之前的基础上加上时间和相关的东西
                self.participants[ip].totalTime += duration
                self.participants[ip].posCount += posdiff
                self.participants[ip].negCount += negdiff

            self.participants[ip].latest_pos_val = posRate  # 判断为positive的rate
            self.participants[ip].latest_timestamp = timestamp  #消息发送时间
            self.participants[ip].ip = ip   #IP地址还是要的

            if self.nicknames.has_key(ip):
                self.participants[ip].nickname = self.nicknames[ip]  # 设置昵称

            if (lastIP is not None) and (lastIP != ip):
                #构造Conversation (排除上个人的ip是自己的情况！)
                convContent = ConvContent(lastIP, timestamp, duration, emoState)
                if not self.participants[ip].conversations.has_key(lastIP):
                    self.participants[ip].conversations[lastIP] = []  #新建一个列表，存放与这个人的conversations
                self.participants[ip].conversations[lastIP].append(convContent)

            #TODO: PUT PROCESSED DATA TO EXPORT QUEUE
            #exportQueue里面是完整的participants数据
            self.exportQueue.put(self.participants)


            lastIP = ip     # Update lastIP to current ip

    def stop(self):
        self.shouldStop = True
        self.logHandler.close_file()


    def has_participant(self, ip):
        return self.participants.has_key(ip)