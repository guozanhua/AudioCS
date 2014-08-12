__author__ = 'BorisHe'
from connections import ClientSocketHandler
import Queue
from time import sleep

inQueue = Queue.Queue()
ip = '127.0.0.1'
c = ClientSocketHandler.ClientSocketReceiver(inQueue, ip)
c.start()

sleep(1200)

c.stop()