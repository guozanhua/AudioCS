__author__ = 'BorisHe'
from connections import ServerSocketHandler, SimpDataProcessor
from time import sleep
import Queue

inQueue = Queue.Queue()
outQueue = Queue.Queue()
s = ServerSocketHandler.ServerUDPReceiver(exportQueue=inQueue, iAddress='192.168.1.200', port=1234)
s.start()
#d = DataProcessor.DataProcessor(inQueue, outQueue)
d = SimpDataProcessor.SimpleDataProcessor(inQueue, outQueue)
d.start()
s_send = ServerSocketHandler.ServerUDPSender(outQueue)
s_send.start()

sleep(9600)

s.stop()
d.stop()
s_send.stop()