__author__ = 'BorisHe'
from connections import ServerSocketHandler, SimpDataProcessor
from time import sleep
import Queue
import socket

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


raw_input('RUNNING...Press ANY KEY to quit...')

s.stop()
d.stop()
s_send.stop()
exit()