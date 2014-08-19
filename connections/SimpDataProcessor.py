#encoding:utf-8

''' 简化版的数据处理，只处理分类器结果的event数据 '''

import threading
from models.UniteModel import *
from models.Participant import *
from models.ClassifierData import *
from models.netdata import PStatData, PIncrData, HugePackage
from models.ConvContent import *
from utils.LogHandler import LogFileHandler
from utils.ConfigHandler import get_nicknames

class SimpleDataProcessor(threading.Thread):

    def __init__(self, importQueue, exportQueue):
        threading.Thread.__init__(self)
        self.importQueue = importQueue
        self.exportQueue = exportQueue
        self.shouldStop = False
        self.participants = {}  # 所有参与者的Hash表(IP, PStatData)
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
            # if element.type != UniteModel.TYPE_CLASSIFY_RESULT:
            #     print 'DO NOT USE SimpDataProcessor WITHOUT TYPE_CLASSIFY_RESULT, DATA OMITTED!'
            #     continue
            posdiff = 0
            negdiff = 0

            if element.type == UniteModel.TYPE_CLASSIFY_RESULT:
                cls_model = element.content
                self.logHandler.write_classifier_data(cls_model)    #   Write log file
                ip = cls_model.senderip
                timestamp = cls_model.timestamp
                emoState = cls_model.result
                posRate = cls_model.positive_rate
                incrData = PIncrData(ip=ip, pos_val=posRate, timestamp=timestamp)
                #duration = cls_model.duration

                if emoState == ClassifierData.RESULT_POSITIVE:
                    posdiff = 1
                else:
                    negdiff = 1
                convdiff = 1
            elif element.type == UniteModel.TYPE_ECHO_DATA:
                # Echo Data的返回值没有incrData!
                ip = element.content
                incrData = None
                convdiff = 0


            if not self.has_participant(ip):
                #如果没有这个参与者，则新建一条记录
                # participant = Participant(ip, duration, posdiff, negdiff)
                # participant.latest_pos_val = posRate  # 判断为positive的rate
                statData = PStatData(ip)
                statData.posCount += posdiff
                statData.negCount += negdiff
                if self.nicknames.has_key(ip):
                    statData.nickname = self.nicknames[ip]  # 设置昵称
                self.participants[ip] = statData
            else:
                #如果有记录，则在之前的基础上加上时间和相关的东西
                #self.participants[ip].totalTime += duration
                self.participants[ip].posCount += posdiff
                self.participants[ip].negCount += negdiff


            #self.participants[ip].latest_pos_val = posRate  # 判断为positive的rate
            #self.participants[ip].latest_timestamp = timestamp  #消息发送时间
            #self.participants[ip].ip = ip   #IP地址还是要的

            if (lastIP is not None) and (lastIP != ip):
                #构造Conversation (排除上个人的ip是自己的情况！)
                #convContent = ConvContent(lastIP, timestamp, duration, emoState)
                #if not self.participants[ip].conversations.has_key(lastIP):
                #    self.participants[ip].conversations[lastIP] = []  #新建一个列表，存放与这个人的conversations
                #self.participants[ip].conversations[lastIP].append(convContent)

                # 加入ip与lastIP的对话计数
                if not self.participants[ip].conv.has_key(lastIP):
                    self.participants[ip].conv[lastIP] = convdiff
                else:
                    self.participants[ip].conv[lastIP] += convdiff

            #TODO: PUT PROCESSED DATA TO EXPORT QUEUE
            #exportQueue里面是HugePackage数据
            hugePkg = HugePackage(incrData, self.participants)

            self.exportQueue.put(hugePkg)


            lastIP = ip     # Update lastIP to current ip

    def clear(self):
        self.participants.clear()
        self.importQueue.queue.clear()
        self.exportQueue.queue.clear()

    def stop(self):
        self.shouldStop = True
        self.logHandler.close_file()


    def has_participant(self, ip):
        return self.participants.has_key(ip)