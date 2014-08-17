#coding:utf-8

import sys

from PyQt4 import QtGui, QtCore
from Widgets.MetreHandLabel import MetreHandLabel
from Widgets.MatPlotLabel import MatPlotLabel
from GUI.Widgets.matplotlibWidgetFile import matplotlibWidget
import random
import networkx as nx
from GUI import nx_custom_layout
from time import sleep
import CusSettings

COLOR_MAP_NODE = ['#bf0c10', '#e1dd07', '#8cc12d', '#8fc43f']  # 红色：191,12,26 黄色：255,221,7 蓝色：140,193,45 绿色：143,196,63
COLOR_MAP_EDGE = ['#7a7c7b', '#77787a', '#6f6f6f', '#505050', '#56575b', '#6f6f6f']  # 边的颜色，各种灰色

class ClientSummaryGUI(QtGui.QWidget):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setGeometry(350, 350, 500, 380)
        #self.setStyleSheet("background-color:#3c4043")
        self.move_offset = None

        self.bkg = QtGui.QPixmap(CusSettings.CURRENT_PATH + 'resources/summary_bkg.png')
        self.bkg_label = QtGui.QLabel(self)
        self.bkg_label.setPixmap(self.bkg)
        self.bkg_label.setGeometry(0, 0, 500, 380)


        self.figure_widget = matplotlibWidget(self, figsize=(5.0, 3.8), dpi=10)
        self.figure_widget.setGeometry(0, 0, 500, 380)
        self.figure_widget.hide()

        self.graph = nx.DiGraph()  # DiGraph

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint|QtCore.Qt.WindowStaysOnTopHint)  # Frameless window
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)  #Translucent window

        self.avg_count = 1.0  # 平均每个人说话的次数
        self.avg_edge_count = 1.0


        self.figure_cus_label = MatPlotLabel(self)
        self.figure_cus_label.setGeometry(0, 0, 500, 380)



        #g = nx.complete_graph(5)
        #self.draw_graph(g)

    def have_node(self, name):
        return name in self.graph.nodes()

    def get_ip_pos(self, ip):
        # 根据ip查找节点序号
        return self.graph.nodes().index(ip)


    def make_graph(self, participants):
        # 根据participants绘制网络图
        count = 0
        total = 0
        edge_count = 0
        edge_total = 0
        for ip, p in participants.iteritems():

            node_weight = p.posCount + p.negCount
            total += node_weight
            self.graph.add_node(ip, weight=node_weight, color=COLOR_MAP_NODE[count%4])     # Node attribute `weight`
            for c_ip, conv in p.conversations.iteritems():
                conv_count = p.get_conv_count(c_ip)
                edge_count += 1
                edge_total += conv_count
                self.graph.add_edge(ip, c_ip, weight=conv_count, color=COLOR_MAP_NODE[count%4])
            count += 1
        self.avg_count = float(total)/float(count)
        if edge_count != 0:
            self.avg_edge_count = float(edge_total) /float(edge_count)
        return self.graph


    def draw_graph(self):
        '''使用networkx绘制网络图 若使用None参数则绘制self.graph'''
        print self.graph.nodes()

        # get node size and color
        node_size = [self.graph.node[n]['weight']*500.0/self.avg_count for n in self.graph.nodes_iter()]
        node_size_2 = [self.graph.node[n]['weight']*1000.0/self.avg_count for n in self.graph.nodes_iter()]
        node_size_3 = [self.graph.node[n]['weight']*1500.0/self.avg_count for n in self.graph.nodes_iter()]
        print node_size
        node_color = [self.graph.node[n]['color'] for n in self.graph.nodes_iter()]

        # get edge size and color
        edge_size = [self.graph.edge[s][d]['weight']*5.0/self.avg_edge_count for s,d in self.graph.edges_iter()]
        print edge_size
        edge_color = [self.graph.edge[s][d]['color'] for s,d in self.graph.edges_iter()]

        pos = nx_custom_layout.nx_custom_layout(self.graph)

        self.figure_widget.clear()
        # nx.draw_networkx(self.graph, pos=pos, ax=self.figure_widget.canvas.ax, node_size=node_size, node_color=node_color
        #          , edge_color=edge_color)
        nx.draw_networkx_nodes(self.graph, pos, node_size=node_size, node_color=node_color,
                               ax=self.figure_widget.canvas.ax, linewidths=0.0, alpha=0.10)

        nx.draw_networkx_nodes(self.graph, pos, node_size=node_size_2, node_color=node_color,
                               ax=self.figure_widget.canvas.ax, linewidths=0.0, alpha=0.15)

        nx.draw_networkx_nodes(self.graph, pos, node_size=node_size_3, node_color=node_color,
                               ax=self.figure_widget.canvas.ax, linewidths=0.0, alpha=0.40)

        nx.draw_networkx_labels(self.graph, pos, ax=self.figure_widget.canvas.ax)
        for i in range(0, len(edge_size)):
            #Draw edge with different width
            nx.draw_networkx_edges(self.graph, pos, width=edge_size[i], edge_color=edge_color[i],
                                   ax=self.figure_widget.canvas.ax, edgelist=[self.graph.edges()[i]],
                                   alpha=0.5)

        self.figure_widget.canvas.draw()
        self.figure_widget.saveFig('summary_fig.png')
        self.figure_cus_label.set_img('summary_fig.png')



    def mousePressEvent(self, event):
        self.move_offset = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() and QtCore.Qt.LeftButton:
            diff = event.pos() - self.move_offset
            new_pos = self.pos() + diff
            self.move(new_pos)

    def mouseDoubleClickEvent(self, qMouseEvent):
        #TODO: 在一定时间内连续双击，关闭整个UI程序(QUIT?)
        qMouseEvent.accept()
        self.close()


class ClientUserGUI(QtGui.QWidget):
    def __init__(self, parent=None, ip='None'):
        QtGui.QWidget.__init__(self, parent)
        self.move_offset = 0
        self.ip = ip
        self.emo_times = []    # 情绪状态发生时间的序列
        self.emo_values = []    # 情绪状态值的序列

        self.bkg_image = QtGui.QPixmap(CusSettings.CURRENT_PATH + 'resources/background_u.png')  #TODO:修改为相对路径
        self.bkg_image_label = QtGui.QLabel(self)
        self.bkg_image_label.setPixmap(self.bkg_image)

        self.figure_widget = matplotlibWidget(self, figsize=(2.8, 0.6), dpi=10)

        self.plot_button = QtGui.QPushButton(ip, self)
        self.plot_button.raise_()

        self.hand_image = MetreHandLabel(self, (423,118))

        self.figure_cus_label = MatPlotLabel(self)
        #self.fig_image_label.hide()


        self.init_ui()



    def append_emo_state(self, timestamp, value):
        # 在时间序列里把新的情感状态及对应的时间加进去
        self.emo_times.append(timestamp)
        self.emo_values.append(value)
        print '(time, value) = (%d, %f) appended.' % (timestamp, value)

    def plot_timeline(self):
        # 绘制时间线
        self.figure_widget.canvas.ax.clear()
        self.figure_widget.canvas.ax.plot(self.emo_times, self.emo_values, 'r-')
        self.figure_widget.canvas.draw()
        self.figure_widget.setAlpha(0.0)

        output_fig_name = 'outputfig_' + self.ip + '.png'
        self.figure_widget.saveFig(output_fig_name)
        self.figure_cus_label.set_img(output_fig_name)




    def init_ui(self):
        self.setGeometry(300, 300, 640, 480)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint|QtCore.Qt.WindowStaysOnTopHint)  # Frameless window
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)  #Translucent window

        self.bkg_image_label.setGeometry(0, 0, 542, 121)
        self.plot_button.setGeometry(74, 10, 100, 35)
        self.figure_widget.setGeometry(20, 60, 280, 60)
        self.figure_widget.hide()
        self.hand_image.setGeometry(361, 58, 120, 120)
        self.figure_cus_label.setGeometry(20, 60, 280, 60)

        #TODO:REMOVE THIS
        #self.figure_cus_label.set_img('d:/output_fig.png')
        #TODO:END

        # self.connect(self.quit, QtCore.SIGNAL('clicked()'),
        #              QtGui.qApp, QtCore.SLOT('quit()'))
        self.plot_button.clicked.connect(self.plot_button_clicked)

    def test_rotation(self):
        self.hand_image.rotate(45)

    def rotate_to_value(self, f_value):
        '''旋转至某一positive数值, 从0至1.0'''
        angle = (f_value - 0.5) * 180.0
        print 'new angle = %f' % angle
        #TODO:有空搞点延迟效果
        for i in range(5, 0, -1):
            swing_angle = (random.random() - 0.5) * i * 2
            self.hand_image.rotate_to(angle + swing_angle)
            sleep(0.05)

        self.hand_image.rotate_to(angle)

    def mousePressEvent(self, qMouseEvent):
        self.move_offset = qMouseEvent.pos()
        #print self.move_offset

    def mouseMoveEvent(self, qMouseEvent):
        if qMouseEvent.buttons() and QtCore.Qt.LeftButton:
            diff = qMouseEvent.pos() - self.move_offset
            new_pos = self.pos() + diff
            self.move(new_pos)

    def mouseDoubleClickEvent(self, qMouseEvent):
        #TODO: 在一定时间内连续双击，关闭整个UI程序(QUIT?)
        qMouseEvent.accept()
        self.close()



    def plot_button_clicked(self):
        # randomNumbers = random.sample(range(0, 10), 10)
        # self.figure_widget.canvas.ax.clear()
        # self.figure_widget.canvas.ax.plot(randomNumbers)
        # self.figure_widget.canvas.draw()
        # self.figure_widget.setAlpha(0.0)
        # self.test_rotation()
        self.plot_button.hide()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    #qb = ClientUserGUI()
    qb = ClientSummaryGUI()
    #qb.show()
    qa = ClientUserGUI()
    qa.show()
    sys.exit(app.exec_())



