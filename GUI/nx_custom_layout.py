#coding:utf-8

''' networkX custom layout '''

import numpy as np

def nx_custom_layout(graph):
    '''
    :param graph: NetworkX graph
    :return: dict: A dictionary of positions leyed by node
    '''

    n = len(graph)
    if n == 1:
        pos = np.asarray([[0.50, 0.50]], dtype=np.float32)
    elif n == 2:
        pos = np.asarray([[0.20, 0.80], [0.80, 0.20]], dtype=np.float32)
    elif n == 4:
        pos = np.asarray([[0.20, 0.20], [0.20, 0.80],
                          [0.80,0.20], [0.80,0.80]], dtype=np.float32)
    elif n == 3:
        pos = np.asarray([[0.50, 0.80], [0.20, 0.20],
                          [0.80, 0.20]], dtype=np.float32)
    else:
        print '`n` size not expected : %d' % n
        pos = np.asarray(np.random.random((n, 2)), dtype=np.float32)  # Behave as random_layout when size > 4

    return dict(zip(graph, pos))
