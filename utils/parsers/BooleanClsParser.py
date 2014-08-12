#coding:utf-8
'''从osc_message转到boolean，用于分类器的data'''

from models.ClassifierData import *
import string

def parse_cls_to_clsdata(osc_msg, timestamp, senderip):
    result_tags = osc_msg.parameters[5:]
    bools = ClassifierData.RESULT_NEGATIVE
    if float(result_tags[1]) < float(result_tags[3]):
        #negative < positive
        bools = ClassifierData.RESULT_POSITIVE
    pos_rate = result_tags[3]
    model = ClassifierData(timestamp, senderip, pos_rate, bools)
    # bools = ClassifierData.RESULT_NEGATIVE
    # if instr.find('positive') != -1:
    #     bools = ClassifierData.RESULT_POSITIVE
    # model = ClassifierData(timestamp, senderip, bools)
    return model
