#coding:utf-8

import sys

from PyQt4 import QtGui, QtCore
from Widgets.MetreHandLabel import MetreHandLabel
from Widgets.MatPlotLabel import MatPlotLabel
from GUI.Widgets.matplotlibWidgetFile import matplotlibWidget
from ClientGuiThreads import GraphMakeThread, TimelinePlotThread, GraphDrawThread
import networkx as nx
from GUI import nx_custom_layout
import time
import CusSettings
import cStringIO
import threading

COLOR_MAP_NODE = ['#FD5C04', '#e1dd07', '#008cc1', '#8fc43f']  # 橙色：253,92,4 黄色：255,221,7 蓝色：0，140,1930 绿色：143,196,63
COLOR_MAP_EDGE = ['#7a7c7b', '#77787a', '#6f6f6f', '#505050', '#56575b', '#6f6f6f']  # 边的颜色，各种灰色

STATIC_NODE_COLOR = {'10.214.143.221': '#FD5C04',
                     '10.214.143.224': '#e1dd07',
                     '10.214.143.222': '#008cc1',
                     '10.214.143.226': '#8fc43f'}

class ClientSummaryGUI(QtGui.QWidget):
    summaryGUImutex = threading.Lock()  # 公用的mutex

    def __init__(self, parent=None, init_position=(350, 350)):
        QtGui.QWidget.__init__(self, parent)
        self.setGeometry(init_position[0], init_position[1], 500, 380)
        #self.setStyleSheet("background-color:#3c4043")
        self.move_offset = None
        self.last_draw_time = 0  # 上次绘图的时间

        #self.bkg = QtGui.QPixmap(CusSettings.CURRENT_PATH + 'resources/summary_bkg.png')

        self.bkg_label = QtGui.QLabel(self)
        #self.bkg_label.setPixmap(self.bkg)
        self.bkg_label.setStyleSheet('background-color:rbga(0, 0, 0, 30)')
        self.bkg_label.setGeometry(0, 0, 500, 380)


        self.figure_widget = matplotlibWidget(self, figsize=(5.0, 3.8), dpi=10)
        #self.figure_widget.setGeometry(0, 0, 500, 380)
        self.figure_widget.hide()

        self.graph = nx.Graph()  # DiGraph

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint|QtCore.Qt.WindowStaysOnTopHint)  # Frameless window
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)  #Translucent window

        self.avg_count = 1.0  # 平均每个人说话的次数
        self.avg_edge_count = 1.0


        self.figure_cus_label = MatPlotLabel(self)
        self.figure_cus_label.setGeometry(0, 0, 500, 380)


        self.node_labels = {}

    def clear(self):
        # clear to restart
        self.last_draw_time = 0  # 上次绘图的时间
        self.figure_widget = matplotlibWidget(self, figsize=(5.0, 3.8), dpi=10)
        self.figure_widget.hide()
        self.graph = nx.Graph()
        self.figure_cus_label.clear()
        self.figure_cus_label.hide()
        self.figure_cus_label = MatPlotLabel(self)
        self.figure_cus_label.setGeometry(0, 0, 500, 380)
        self.figure_cus_label.show()


    def have_node(self, name):
        return name in self.graph.nodes()

    def get_ip_pos(self, ip):
        # 根据ip查找节点序号
        return self.graph.nodes().index(ip)

    def make_graph_thread(self, statDataDict):
        var_list = [self.avg_count, self.avg_edge_count]
        graph_thread = GraphMakeThread(self.summaryGUImutex, self.node_labels, self.graph,
                                       var_list, statDataDict)
        graph_thread.graph_done.connect(self.draw_graph_thread)
        #graph_thread.graph_done.connect(self.draw_graph)
        graph_thread.run()


    def make_graph(self, statDataDict):


        # 根据participants绘制网络图
        #empty_node_count = 0
        count = 0
        total = 0
        edge_count = 0
        edge_total = 0
        edge_weight = {}      # {src_ip, {dst_ip, weight}}   务必遵循src_ip < dst_ip!!!

        #self.graph.remove_edges_from(self.graph.edges())

        for ip, p in statDataDict.iteritems():

            node_weight = p.posCount + p.negCount
            total += node_weight
            # Add node label if available
            if p.nickname is not None:
                self.node_labels[ip] = p.nickname
            else:
                self.node_labels[ip] = ip

            if STATIC_NODE_COLOR.has_key(ip):
                n_color = STATIC_NODE_COLOR[ip]
            else:
                n_color = COLOR_MAP_NODE[count % 4]

            self.graph.add_node(ip, weight=node_weight, color=n_color)     # Node attribute `weight`

            for c_ip, conv_count in p.conv.iteritems():
                src_ip = ip
                dst_ip = c_ip
                if not ip < c_ip:
                    src_ip = c_ip
                    dst_ip = ip
                if not edge_weight.has_key(src_ip):
                    edge_weight[src_ip] = {}
                if not edge_weight[src_ip].has_key(dst_ip):
                    edge_weight[src_ip][dst_ip] = conv_count
                else:
                    edge_weight[src_ip][dst_ip] += conv_count

            for src_ip, dst_dict in edge_weight.iteritems():
                #conv_count = p.get_conv_count(c_ip)
                for dst_ip, conv_count in edge_weight[src_ip].iteritems():
                    edge_count += 1
                    edge_total += conv_count
                    self.graph.add_edge(src_ip, dst_ip, weight=conv_count, color=COLOR_MAP_EDGE[count % 6])
            count += 1

        if count != 0 and total != 0:
            self.avg_count = float(total)/float(count)
        if edge_count != 0 and edge_total != 0:
            self.avg_edge_count = float(edge_total) /float(edge_count)
        #print edge_weight
        #print self.graph.edges()
        return self.graph


    def draw_graph(self, var_list = None):
        '''使用networkx绘制网络图 若使用None参数则绘制self.graph'''
        #print self.graph.nodes()
        if var_list is not None:
            self.avg_edge_count = var_list[1]
            self.avg_count = var_list[0]

        if time.time() - self.last_draw_time < 1.0:
            return      #绘图间隔小于1秒的，忽略本次绘图
        #print '%f, %f' % (self.avg_count, self.avg_edge_count)
        # get node size and color
        node_size = [self.graph.node[n]['weight']*450.0/self.avg_count for n in self.graph.nodes_iter()]
        node_size_2 = [self.graph.node[n]['weight']*750.0/self.avg_count for n in self.graph.nodes_iter()]
        node_size_3 = [self.graph.node[n]['weight']*1250.0/self.avg_count for n in self.graph.nodes_iter()]
        #print node_size
        node_color = [self.graph.node[n]['color'] for n in self.graph.nodes_iter()]

        # get edge size and color
        edge_size = [self.graph.edge[s][d]['weight']*4.0/self.avg_edge_count for s,d in self.graph.edges_iter()]
        #print edge_size
        edge_color = [self.graph.edge[s][d]['color'] for s,d in self.graph.edges_iter()]

        pos = nx_custom_layout.nx_custom_layout(self.graph)

        self.figure_widget.clear()
        # nx.draw_networkx(self.graph, pos=pos, ax=self.figure_widget.canvas.ax, node_size=node_size, node_color=node_color
        #          , edge_color=edge_color)


        nx.draw_networkx_nodes(self.graph, pos, node_size=node_size, node_color=node_color,
                               ax=self.figure_widget.canvas.ax, linewidths=0.0, alpha=0.55)

        nx.draw_networkx_nodes(self.graph, pos, node_size=node_size_2, node_color=node_color,
                               ax=self.figure_widget.canvas.ax, linewidths=0.0, alpha=0.30)

        nx.draw_networkx_nodes(self.graph, pos, node_size=node_size_3, node_color=node_color,
                               ax=self.figure_widget.canvas.ax, linewidths=0.0, alpha=0.15)

        #print self.node_labels
        #print self.graph.nodes()
        nx.draw_networkx_labels(self.graph, pos, ax=self.figure_widget.canvas.ax, labels=self.node_labels)
        for i in range(0, len(edge_size)):
            #Draw edge with different width
            nx.draw_networkx_edges(self.graph, pos, width=edge_size[i], edge_color=edge_color[i],
                                   ax=self.figure_widget.canvas.ax, edgelist=[self.graph.edges()[i]],
                                   alpha=0.8)

        self.figure_widget.canvas.draw()
        #self.figure_widget.saveFig('summary_fig.png')
        #self.figure_cus_label.set_img('summary_fig.png')

        str_io_buffer = cStringIO.StringIO()
        self.figure_widget.saveFig(str_io_buffer)
        self.figure_cus_label.set_img_buffer(str_io_buffer)

        self.last_draw_time = time.time()

    def draw_graph_thread(self, var_list=None):
        if var_list is not None:
            self.avg_edge_count = var_list[1]
            self.avg_count = var_list[0]
        if time.time() - self.last_draw_time < 0.5:
            return      #绘图间隔小于1秒的，忽略本次绘图
        var_list = [self.avg_count, self.avg_edge_count]
        th = GraphDrawThread(self.summaryGUImutex, self.graph, var_list
                             , self.figure_widget, self.node_labels)
        th.graph_data_got.connect(self.draw_graph_data_got)
        th.run()

    def draw_graph_data_got(self, str_io_buffer):
        self.figure_cus_label.set_img_buffer(str_io_buffer)
        self.last_draw_time = time.time()

    def mousePressEvent(self, event):
        self.move_offset = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() and QtCore.Qt.LeftButton:
            diff = event.pos() - self.move_offset
            new_pos = self.pos() + diff
            self.move(new_pos)

    # def mouseDoubleClickEvent(self, qMouseEvent):
    #     #TODO: 在一定时间内连续双击，关闭整个UI程序(QUIT?)
    #     qMouseEvent.accept()
    #     self.close()


class ClientUserGUI(QtGui.QWidget):
    def __init__(self, parent=None, ip='None', nickname=None, init_position=(300, 300)):
        QtGui.QWidget.__init__(self, parent)
        self.move_offset = 0
        self.ip = ip
        self.nickname = nickname
        self.emo_times = []    # 情绪状态发生时间的序列
        self.emo_values = []    # 情绪状态值的序列

        self.last_plot_time = 0     #上次刷新图形时的时间戳

        self.bkg_image = QtGui.QPixmap(CusSettings.CURRENT_PATH + 'resources/background_u.png')  #TODO:修改为相对路径
        self.bkg_image_label = QtGui.QLabel(self)
        self.bkg_image_label.setPixmap(self.bkg_image)

        self.figure_widget = matplotlibWidget(self, figsize=(1.94, 0.39), dpi=10)

        pushbtn_text = ip
        if nickname is not None:
            pushbtn_text += ('(' + self.nickname + ')')
        self.plot_button = QtGui.QPushButton(pushbtn_text, self)
        self.plot_button.raise_()

        self.hand_image = MetreHandLabel(self)

        self.figure_cus_label = MatPlotLabel(self)
        #self.fig_image_label.hide()

        self.setGeometry(init_position[0], init_position[1], 383, 126)  # 85+41
        self.init_ui()

    def clear(self):
        self.emo_times = []
        self.emo_values = []
        self.last_plot_time = 0     #上次刷新图形时的时间戳
        self.figure_cus_label.clear()
        self.figure_cus_label.hide()
        self.figure_cus_label = MatPlotLabel(self)
        self.figure_cus_label.setGeometry(17, 44, 194, 39)
        self.figure_cus_label.show()
        self.rotate_to_value(0.5)

    def append_emo_state(self, timestamp, value):
        # 在时间序列里把新的情感状态及对应的时间加进去
        self.emo_times.append(timestamp)
        self.emo_values.append(value)
        #print '(time, value) = (%d, %f) appended.' % (timestamp, value)
        if len(self.emo_values) > 200:
            # 如果过长，会导致显示混乱，现在先抽取一半元素显示
            #TODO: 有待测试
            self.emo_times = self.emo_times[::2]
            self.emo_values = self.emo_values[::2]

    def plot_timeline(self):
        curr_timestamp = time.time()
        if curr_timestamp - self.last_plot_time < 0.5:
            # 距离上次刷新不到0.5秒
            return

        # 绘制时间线
        self.figure_widget.canvas.ax.clear()
        self.figure_widget.canvas.ax.plot(self.emo_times, self.emo_values, 'r')
        self.figure_widget.canvas.draw()
        self.figure_widget.setAlpha(0.0)

        #output_fig_name = 'outputfig_' + self.ip + '.png'
        str_io_buf = cStringIO.StringIO()
        self.figure_widget.saveFig(str_io_buf)
        #self.figure_cus_label.set_img(output_fig_name)
        self.figure_cus_label.set_img_buffer(str_io_buf)

        self.last_plot_time = time.time()

    def plot_timeline_thread(self):
        # 使用线程操作，避免UI卡死！
        curr_timestamp = time.time()
        if curr_timestamp - self.last_plot_time < 0.5:
            # 距离上次刷新不到0.5秒
            return
        thread = TimelinePlotThread(self.figure_widget, self.emo_times, self.emo_values)
        thread.img_data_got.connect(self.timeline_image_got)
        thread.run()

    def timeline_image_got(self, str_io_buf):
        self.figure_cus_label.set_img_buffer(str_io_buf)

        self.last_plot_time = time.time()

    def init_ui(self):

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint|QtCore.Qt.WindowStaysOnTopHint)  # Frameless window
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)  #Translucent window

        self.bkg_image_label.setGeometry(0, 0, 383, 85)
        self.plot_button.setGeometry(52, 7, 120, 25)
        #self.figure_widget.setGeometry(17, 44, 194, 39)
        self.figure_widget.hide()       # TODO: 考虑去掉这个widget
        self.hand_image.setGeometry(257, 42, 82, 82)
        self.figure_cus_label.setGeometry(17, 44, 194, 39)

        # self.connect(self.quit, QtCore.SIGNAL('clicked()'),
        #              QtGui.qApp, QtCore.SLOT('quit()'))
        self.plot_button.clicked.connect(self.plot_button_clicked)

    def test_rotation(self):
        self.hand_image.rotate(45)

    def rotate_to_value(self, f_value):
        '''旋转至某一positive数值, 从0至1.0'''

        angle = (f_value - 0.5) * 180.0
        #print 'new angle = %f' % angle
        #TODO:有空搞点延迟效果
        # for i in range(5, 0, -1):
        #     swing_angle = (random.random() - 0.5) * i * 2
        #     self.hand_image.rotate_to(angle + swing_angle)
        #     sleep(0.05)

        self.hand_image.rotate_to(angle)

    def mousePressEvent(self, qMouseEvent):
        self.move_offset = qMouseEvent.pos()
        #print self.move_offset

    def mouseMoveEvent(self, qMouseEvent):
        if qMouseEvent.buttons() and QtCore.Qt.LeftButton:
            diff = qMouseEvent.pos() - self.move_offset
            new_pos = self.pos() + diff
            self.move(new_pos)

    def plot_button_clicked(self):
        self.plot_button.hide()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    #qb = ClientUserGUI()
    qb = ClientSummaryGUI()
    #qb.show()
    qa = ClientUserGUI()
    qa.show()
    sys.exit(app.exec_())



