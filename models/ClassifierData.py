#coding:utf-8

#VERSION 2
#UPDATED ON 20140812

from GeneralData import *

class ClassifierData(GeneralData):
    '''分类器结果的数据'''
    RESULT_POSITIVE = 0
    RESULT_NEGATIVE = 1

    def __init__(self, timestamp, senderip, positive_rate, result = RESULT_NEGATIVE, duration=0.0):
        GeneralData.__init__(self, timestamp, senderip)
        self.result = result
        self.positive_rate = positive_rate #结果为positive的置信度0~1
        self.duration = duration


