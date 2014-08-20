#coding:utf-8
__author__ = 'BorisHe'
from connections import ServerSocketHandler, SimpDataProcessor
#from time import sleep
import Queue
import socket
import sys

inQueue = Queue.Queue()
outQueue = Queue.Queue()

socket_text = str(socket.gethostbyname_ex(socket.gethostname()))
print 'Local ip addresses: %s' % socket_text
ip = raw_input('Enter server ip address:')
s = ServerSocketHandler.ServerUDPReceiver(exportQueue=inQueue, iAddress=ip, port=1234)
s.start()
#d = DataProcessor.DataProcessor(inQueue, outQueue)
d = SimpDataProcessor.SimpleDataProcessor(inQueue, outQueue)
d.start()
s_send = ServerSocketHandler.ServerUDPSender(outQueue)
s_send.start()


text = raw_input('[RUNNING]`start` to start listening, `stop`: to stop listening :')
while True:
    if text == 'stop':
        s.stop()
        d.stop()
        s_send.stop()
        sys.exit(0)
    # elif text == 'clear':
    #     d.clear()
    elif text == 'start':
        s.echo_only = False     #关闭echo only，正式开始记录
    else:
        text = raw_input('[RUNNING]`start` to start listening, `stop`: to stop listening :')


