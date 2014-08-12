#coding:utf-8
from GeneralData import *


class BinaryData(GeneralData):
    '''存储音频流数据'''
    def __init__(self, timestamp, sender, sample_time, data=None):
        GeneralData.__init__(self, timestamp, sender)
        self.sample_time = sample_time  # in milliseconds
        self.data = data  # float array

    def get_data_avg_value(self):
        '''Calculates average value of self.data'''
        data_len = len(self.data)
        if data_len <= 0:
            return 0
        sum = 0.0
        for d in self.data:
            sum += d
        return sum/float(data_len)
