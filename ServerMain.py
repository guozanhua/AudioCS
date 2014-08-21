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


text = raw_input('[RUNNING]`s` to start listening, `q` to stop listening, `r` to restart server :')
while True:
    if text == 'q':
        s.stop()
        d.stop()
        s_send.stop()
        sys.exit(0)
    # elif text == 'clear':
    #     d.clear()
    elif text == 's':
        s.echo_only = False     #关闭echo only，正式开始记录
        print 'Server fully started...'
        text = raw_input('[RUNNING]`s` to start listening, `q` to stop listening, `r` to restart server :')

    elif text == 'r':
        # reboot
        print '=========== SERVER RESTARTED =========='
        s.echo_only = True
        d.restart()
        #old_participants = d.participants
        d = SimpDataProcessor.SimpleDataProcessor(inQueue, outQueue)
        d.start()
        text = raw_input('[RUNNING]`s` to start listening, `q` to stop listening, `r` to restart server :')
    else:
        text = raw_input('[RUNNING]`s` to start listening, `q` to stop listening, `r` to restart server :')


