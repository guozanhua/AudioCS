AudioCS
=======

将emoVoice的分析结果通过Socket读取，然后统计结果并分发给Client，最终呈现给用户（用于会议时分析与会者的情绪状态、活跃度等）

##输入
输入为openSSL::emoVoice通过Socket导出的信息有两种格式。具体参见emoVoice的文档
###OSC
分类器分类结果以及voice intensity的流数据用OSC（Open Sound Control）格式.
修改了python-osc-1.4.1的代码以实现OSC数据流的读取
###XML
捕捉到VAD的事件用XML格式输出

***

##处理
服务器将数据汇总后，做统计，然后将统计数据分发给各客户端。

***

##输出
呈现给用户的是一套可视化UI，使用PyQt4 + matplotlib + networkx
简直丑到爆！
