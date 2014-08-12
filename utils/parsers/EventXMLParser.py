#coding:utf-8
'''解析XML数据为Event类型'''
from models import EventData
import xml.etree.ElementTree as ET

def parse_xml_to_event(xml, timestamp, senderip):
    root = ET.fromstring(xml)
    root = root[0]
    sender = root.get('sender')
    event = root.get('event')
    from_time = root.get('from')
    dur = int(root.get('dur'))
    prob = float(root.get('prob'))
    #_type = root.get('type')
    model = EventData.EventData(timestamp, senderip, from_time, dur, sender, event, prob)
    return model


