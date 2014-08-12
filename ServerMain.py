__author__ = 'BorisHe'
from connections import ServerSocketHandler, DataProcessor
from time import sleep
import Queue

inQueue = Queue.Queue()
outQueue = Queue.Queue()
s = ServerSocketHandler.ServerUDPReceiver(exportQueue=inQueue, iAddress='127.0.0.1', port=1234)
s.start()
d = DataProcessor.DataProcessor(inQueue, outQueue)
d.start()
s_send = ServerSocketHandler.ServerUDPSender(outQueue)
s_send.start()

sleep(1200)

s.stop()
d.stop()
s_send.stop()