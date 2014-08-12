#coding:utf-8
from GeneralData import *

class EventData(GeneralData):
    '''存储Event结果的数据模型'''
    def __init__(self, timestamp, ipsender, time_from, dur, sender='voice', event='vad', prob=1.00):
        GeneralData.__init__(self, timestamp, ipsender)
        self.sender = sender
        self.event = event
        self.time_from = time_from
        self.dur = dur
        self.prob = prob

