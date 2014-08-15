#coding:utf-8
'''数据处理中心'''
import threading
from models.UniteModel import *
from models.Participant import *
from models.ClassifierData import *
from models.ConvContent import *


class DataProcessor(threading.Thread):
    BATCH_DATA_SIZE = 3  #每次说话收到的数据包个数

    def __init__(self, importQueue, exportQueue):
        threading.Thread.__init__(self)
        self.importQueue = importQueue
        self.exportQueue = exportQueue
        self.shouldStop = False
        self.participants = {}  #所有参与者的Hash表(IP, Participant)
        self.elementDict = {}   #暂存元素的element表(IP, [element])

    def get_full_elements(self, element_in):
        '''将一个元素放进列表，如果有可用的配对组（目前3个一组），则返回值为可用数据的tuple，否则返回None, None'''
        ip = element_in.content.senderip
        if self.elementDict.has_key(ip):
            self.elementDict[ip].append(element_in) #塞进去先
            return self.get_valid_elems(self.elementDict[ip])
        else:
            self.elementDict[ip] = [element_in]
            return None, None

    def run(self):
        lastIP = None #上一个发送者的IP
        while not self.shouldStop:
            if self.importQueue.empty():
                continue

            # elements = []
            # for i in range(0, DataProcessor.BATCH_DATA_SIZE):
            #     element = self.importQueue.get()
            #     print '\nI`ve got an element type = %d, remaining element size :%d' %(element.type, self.importQueue.qsize())
            #     elements.append(element)
            #self.importQueue.task_done()
            #TODO: PROCESS DATA RIGHT HERE
            element = self.importQueue.get()
            eventElem, classElem = self.get_full_elements(element)#self.get_valid_elems(elements)
            if (eventElem, classElem) == (None, None):
                continue  #尚未填满
            print 'I`m full...'
            eveContent = eventElem.content
            clsContent = classElem.content
            timestamp = eveContent.timestamp
            ip = eveContent.senderip
            emoState = clsContent.result
            posRate = clsContent.positive_rate

            posdiff = 0
            negdiff = 0
            if emoState == ClassifierData.RESULT_POSITIVE:
                posdiff = 1
            else:
                negdiff = 1
            duration = eveContent.dur

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
            #print str(self.participants)


    def stop(self):
        self.shouldStop = True

    def has_participant(self, ip):
        return self.participants.has_key(ip)

    def get_valid_elems(self, elements):
        eventElem = None
        classElem = None
        for elem in elements:
            if UniteModel.TYPE_EVENT_DATA == elem.type:
                eventElem = elem
            elif UniteModel.TYPE_CLASSIFY_RESULT == elem.type:
                classElem = elem
        if (eventElem is None) or (classElem is None):
            #print '[ERROR]CANNOT FIND SPECIFIED ELEMENT'
            return None, None

        del self.elementDict[eventElem.content.senderip]

        return eventElem, classElem
