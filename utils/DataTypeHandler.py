#coding:utf-8
from models.UniteModel import *
'''判断输入数据流的数据类型'''

DATA_TYPE_BIN = UniteModel.TYPE_BINARY_DATA
DATA_TYPE_CLS = UniteModel.TYPE_CLASSIFY_RESULT
DATA_TYPE_XML = UniteModel.TYPE_EVENT_DATA
DATA_TYPE_ECHO = UniteModel.TYPE_ECHO_DATA
DATA_TYPE_UNKNOWN = UniteModel.TYPE_OTHER



def determine_data_type(data):
    if data.startswith('/strm'):
        #Stream data
        return DATA_TYPE_BIN
    elif data.startswith('/echo'):
        return DATA_TYPE_ECHO
    elif data.startswith('/evnt'):
        #Classification data send as `event`
        return DATA_TYPE_CLS
    else:
        return DATA_TYPE_XML
    # length = len(data)
    # if length==9:
    #     bool1 = data.find('positive')
    #     bool2 = data.find('negative')
    #     if bool1!=-1 or bool2!=-1:
    #         return DATA_TYPE_CLS
    #     else:
    #         return DATA_TYPE_UNKNOWN
    #
    # elif -1 != data.find('events'):
    #         return DATA_TYPE_XML
    # else:
    #         return DATA_TYPE_BIN
    #         #TODO:TYPE_UNKNOWN NOT CONSIDERED

