# -*- coding:utf-8
'''
    created at 2016-03-11
    author:yx
'''

'''
    @simirlar_metrix:dict 元组(a,b):2
    @N:list对应元组里面节点
    @usio:很小的范围距离
    @minpts:在usio范围内最小的节点数
    usio与minpts用来确定是否为核心节点
'''
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class optics_cly():
    def __init__(self, usio, usio2, minpts, simirlar_metrix, N):
        self.usio = usio
        self.usio2 = usio2
        self.minpts = minpts
        self.distance = simirlar_metrix
        self.nodeset = set(N)
        self.wating_dict = dict()
        self.core_node = dict()

    def get_corenode(self):
        count_in = dict()
        for dis in self.distance.keys():
            cur_dis = self.distance[dis]
            if cur_dis < self.usio:
                if dis[0] not in count_in:
                    count_in[dis[0]] = [1, cur_dis]
                else:
                    count_in[dis[0]][0] += 1
                    count_in[dis[0]][1]  = max(count_in[dis[0]][1], cur_dis)
                if dis[1] not in count_in:
                    count_in[dis[1]] = [1, cur_dis]
                else:
                    count_in[dis[1]][0] += 1
                    count_in[dis[1]][1]  = max(count_in[dis[1]][1], cur_dis)
        for i in count_in.keys():
            if count_in[i][0] >= self.minpts:
                self.core_node[i] = count_in[i][1]

    def insert_node(self, cur):
        for i in self.nodeset:
            #if (((i, cur) in self.distance) and (self.distance[(i,cur)] <=
                #self.usio)):
            if ((i, cur) in self.distance):
                if i in self.wating_dict:
                    self.wating_dict[i] = min(max(self.distance[(i, cur)],
                self.core_node[cur]), self.wating_dict[i])
                else:
                    self.wating_dict[i] = max(self.distance[(i, cur)],
                self.core_node[cur])
            #if (((cur, i) in self.distance) and (self.distance[(cur, i)] <=
                #self.usio)):
            if ((cur, i) in self.distance):
                if i in self.wating_dict:
                    self.wating_dict[i] = min(max(self.distance[(cur, i)],
                self.core_node[cur]),self.wating_dict[i])
                else:
                    self.wating_dict[i] = max(self.distance[(cur, i)],
                self.core_node[cur])

    def runOptics(self):
        from operator import itemgetter
        from matplotlib import pyplot as plt
        import numpy as np
        nodelist = []
        r_list = []
        self.get_corenode()
        logging.info('计算核心节点，done！')
        while(len(self.nodeset) > 0):
            if (len(self.nodeset & set(self.core_node.keys())) > 0):
                current_node = (self.nodeset & set(self.core_node.keys())).pop()
                self.nodeset.remove(current_node)
            else:
                break
            if current_node in self.core_node:
                r_list.append(self.core_node[current_node])
                nodelist.append(current_node)
                self.insert_node(current_node)
                while(len(self.wating_dict) > 0):
                    current_node = min(self.wating_dict.iteritems(),
                    key=itemgetter(1))[0]
                    self.nodeset.remove(current_node) 
                    r_list.append(self.wating_dict[current_node])
                    nodelist.append(current_node)
                    self.wating_dict.pop(current_node)
                    if current_node in self.core_node:
                        self.insert_node(current_node)
        logging.info("获得距离数据!!")
        #plt.hist(r_list, bins=10, range(len(r_list)))
        plt.bar(range(len(r_list)), r_list, width=1,align='edge', color='green')
        plt.show()
        return self.clustering(nodelist, r_list)

    def clustering(self, n_list, r_list):
        clusterid = -1
        k = 0
        result = []
        result.append([])
        clusterid = k
        k += 1
        for i in range(len(r_list)):
            if (r_list[i] > self.usio2) :
                if ((n_list[i] in self.core_node) and (self.core_node[n_list[i]] <=
                    self.usio2)):
                    if len(result[clusterid]) < 10:
                        result[clusterid] = [n_list[i]]
                    else:
                        clusterid = k
                        k += 1
                        result.append([])
                        result[clusterid].append(n_list[i])
            else:
                result[clusterid].append(n_list[i])
        return (result, n_list)
