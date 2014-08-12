#coding:utf-8
class Participant:
    '''参与人的类，里面存储一些统计数据，及对话数据'''
    def __init__(self, ip, totalTime, posCount=0, negCount=0, conversations = None):
        self.ip = ip
        self.totalTime = totalTime
        self.posCount = posCount
        self.negCount = negCount
        self.conversations = conversations #字典型，{participantIP, [ConvContent]}

        if conversations is None:
            self.conversations = {}  #字典型，{participantIP, [ConvContent]}

    def get_conv_count(self, partcipantIP):
        '''与指定IP地址人员的会话次数'''
        if not self.conversations.has_key(partcipantIP):
            return 0
        convs = self.conversations[partcipantIP]
        return len(convs)

    def get_total_count(self):
        #总对话次数
        return self.posCount + self.negCount

    def get_avg_time(self):
        #平均对话时长
        return self.totalTime / self.get_total_count()

    def __str__(self):
        '''String output'''
        output = 'IP:' + str(self.ip) \
                 + '\ntotalTime:' + str(self.totalTime) \
                 + '\npos/neg:' + str(self.posCount) + '/' + str(self.negCount) \
                 + '\nconversation size:' + str(len(self.conversations))
        return output