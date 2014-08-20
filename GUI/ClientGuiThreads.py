#coding:utf-8
'''
GUI操作的线程类
'''
import threading
from PyQt4 import QtCore
import ClientGUI
import cStringIO
import networkx as nx
from GUI import nx_custom_layout

class GraphMakeThread(QtCore.QThread):
    #mutex = threading.Lock()
    graph_done = QtCore.pyqtSignal()    #绘图完成的信号

    def __init__(self, mutex, node_labels, graph, avg_count, avg_edge_count, statDataDict):
        QtCore.QThread.__init__(self)
        self.mutex = mutex
        self.node_labels = node_labels
        self.graph = graph
        self.avg_count = avg_count
        self.avg_edge_count = avg_edge_count
        self.statDataDict = statDataDict

    def run(self):
        self.mutex.acquire()

        count = 0
        total = 0
        edge_count = 0
        edge_total = 0
        edge_weight = {}      # {src_ip, {dst_ip, weight}}   务必遵循src_ip < dst_ip!!!

        for ip, p in self.statDataDict.iteritems():

            node_weight = p.posCount + p.negCount
            total += node_weight
            # Add node label if available
            if p.nickname is not None:
                self.node_labels[ip] = p.nickname
            else:
                self.node_labels[ip] = ip

            if ClientGUI.STATIC_NODE_COLOR.has_key(ip):
                n_color = ClientGUI.STATIC_NODE_COLOR[ip]
            else:
                n_color = ClientGUI.COLOR_MAP_NODE[count % 4]

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
                    self.graph.add_edge(src_ip, dst_ip, weight=conv_count, color=ClientGUI.COLOR_MAP_EDGE[count % 6])
                    count += 1

        if count != 0 and total != 0:
            self.avg_count = float(total)/float(count)
        if edge_count != 0 and edge_total != 0:
            self.avg_edge_count = float(edge_total) /float(edge_count)

        self.mutex.release()

        self.graph_done.emit()

class TimelinePlotThread(QtCore.QThread):
    mutex = threading.Lock()
    img_data_got = QtCore.pyqtSignal(object)    # 图片数据获取完成

    def __init__(self, figure_widget, emo_times, emo_values):
        QtCore.QThread.__init__(self)
        self.figure_widget = figure_widget
        self.emo_times = emo_times
        self.emo_values = emo_values

    def run(self):
        self.mutex.acquire()

        self.figure_widget.canvas.ax.clear()
        self.figure_widget.canvas.ax.plot(self.emo_times, self.emo_values, 'r')
        self.figure_widget.canvas.draw()
        self.figure_widget.setAlpha(0.0)

        #output_fig_name = 'outputfig_' + self.ip + '.png'
        str_io_buf = cStringIO.StringIO()
        self.figure_widget.saveFig(str_io_buf)

        self.mutex.release()

        self.img_data_got.emit(str_io_buf)

class GraphDrawThread(QtCore.QThread):
    graph_data_got = QtCore.pyqtSignal(object)      # 网络节点绘制完成，emit个数据过去

    def __init__(self, mutex, graph, avg_count, avg_edge_count, figure_widget, node_labels):
        QtCore.QThread.__init__(self)
        self.mutex = mutex
        self.graph = graph
        self.avg_count = avg_count
        self.avg_edge_count = avg_edge_count
        self.figure_widget = figure_widget
        self.node_labels = node_labels

    def run(self):
        self.mutex.acquire()

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

        nx.draw_networkx_nodes(self.graph, pos, node_size=node_size, node_color=node_color,
                               ax=self.figure_widget.canvas.ax, linewidths=0.0, alpha=0.55)

        nx.draw_networkx_nodes(self.graph, pos, node_size=node_size_2, node_color=node_color,
                               ax=self.figure_widget.canvas.ax, linewidths=0.0, alpha=0.30)

        nx.draw_networkx_nodes(self.graph, pos, node_size=node_size_3, node_color=node_color,
                               ax=self.figure_widget.canvas.ax, linewidths=0.0, alpha=0.15)

        nx.draw_networkx_labels(self.graph, pos, ax=self.figure_widget.canvas.ax, labels=self.node_labels)
        for i in range(0, len(edge_size)):
            #Draw edge with different width
            nx.draw_networkx_edges(self.graph, pos, width=edge_size[i], edge_color=edge_color[i],
                                   ax=self.figure_widget.canvas.ax, edgelist=[self.graph.edges()[i]],
                                   alpha=0.8)

        self.figure_widget.canvas.draw()


        str_io_buffer = cStringIO.StringIO()
        self.figure_widget.saveFig(str_io_buffer)

        self.mutex.release()

        self.graph_data_got.emit(str_io_buffer)
