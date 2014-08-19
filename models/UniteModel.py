#coding:utf-8
class UniteModel:
    '''统一模型
        将所有数据存放成统一的模型，以便加入队列进行处理分发
    '''
    TYPE_CLASSIFY_RESULT = 0    #分类器结果
    TYPE_BINARY_DATA = 1        #二进制数据（音频之类的）
    TYPE_EVENT_DATA = 2         #Event事件数据
    TYPE_ECHO_DATA = 3          #Echo data
    TYPE_OTHER = 99             #其他类型（plain text之类的）

    def __init__(self, type = TYPE_OTHER, content = None):
        self.type = type
        self.content = content


