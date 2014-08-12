#coding:utf-8
'''客户端吃消息的东西，需要掌握GUI的操纵大权'''

import threading

class ClientDataConsumer(threading.Thread):
    def __init__(self, importQueue, uiController):
        threading.Thread.__init__(self)
        self.importQueue = importQueue      #输入的Queue，里面是一个个participants
        self.uiController = uiController    #界面控制器，里面有能够更新某个界面的函数接口
        self.shouldStop = False

    def run(self):
        while not self.shouldStop:
            if self.importQueue.empty():
                continue
            participants = self.importQueue.get()  #得到的是列表[Participant]
            #TODO: DEAL WITH DATA AND USE UI_CONTROLLER TO UPDATE UI

            

    def stop(self):
        self.shouldStop = True



