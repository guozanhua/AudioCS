#coding:utf-8
'''
服务器端通过网络发出的数据类型都在这边了
'''

class HugePackage():
    def __init__(self, incrData, statDataDict):
        self.incrData = incrData            # 每次更新肯定只有一个人的数据发生改变
        self.statDataDict = statDataDict    # {ip, PStatData}

class PStatData():
    def __init__(self, ip, nickname=None):
        self.ip = ip
        self.nickname = nickname
        self.posCount = 0
        self.negCount = 0
        self.conv = {}      # {ip, 对话次数}

class PIncrData():
    def __init__(self, ip, pos_val, timestamp):
        self.ip = ip
        self.pos_val = pos_val
        self.timestamp = timestamp