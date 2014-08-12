#coding: utf-8
from utils.parsers import osc_types
from models import BinaryData

'''将音频流数据转换为model数据'''

def parse_stream_to_model(osc_msg, senderip, timestamp):
    params = osc_msg.parameters
    sample_time = params[1]  # time in milliseconds
    sample_number = params[3]
    #size_by_byte = params[5]
    sample_type = params[6]
    raw_floats = params[7]
    if sample_type != 9:  #SSI_FLOAT
        print 'Unknown sample_type %d' % sample_type
        return None
    data = []
    count = 0
    index = 0
    while count < sample_number:
        val, index = osc_types.get_float(raw_floats, index, False)
        data.append(val)
        count += 1
    print 'Totally %d floats parsed.' % count
    model = BinaryData.BinaryData(timestamp, senderip, sample_time, data)
    return model