#coding:utf-8
import time
import datetime

class LogFileHandler:
    def __init__(self, path=None):
        if None == path:
            path = 'log/' + time.strftime('%Y%m%d%H%M%S') + '_log.log'
        self.path = path
        self.file = open(path, 'a')  # a+ 以读写方式打开文件，并把文件指针移到文件尾。
        print 'Log file created. %s' % path

    def write_classifier_data(self, cls_event):
        # 写ClassifierData
        readable_time = datetime.datetime.fromtimestamp(cls_event.timestamp).strftime('%Y-%m-%d %H:%M:%S')

        str_to_write = ''
        str_to_write += (readable_time + ', ')
        str_to_write += (cls_event.senderip + ', ')
        str_to_write += (str(cls_event.result) + ', ')
        str_to_write += (str(cls_event.positive_rate) + ', ')
        str_to_write += (str(cls_event.duration) + '\n')
        self.file.write(str_to_write)
        self.file.flush()

    def close_file(self):
        self.file.close()
        print 'Log file closed.'
