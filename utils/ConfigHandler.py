#coding:utf-8
'''
读取服务器配置文件
'''
import ConfigParser

def get_nicknames(conf_path='srv_config.ini'):
    # 从配置文件读取nickname替换列表
    # 返回值为字典类 {IP, nickname}
    config = ConfigParser.SafeConfigParser()
    config.read(conf_path)
    if not config.has_section('nicknames'):
        print 'ERROR: Config file not valid.'
        return {}
    nicks = config.options('nicknames')
    #print nicks
    result = {}
    for option in nicks:
        nickname = config.get('nicknames', option)
        result[option] = nickname
    print result
    return result
