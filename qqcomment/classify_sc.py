# -*- coding:utf-8
'''
    create at 2016-03-04
    author:yx
'''
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
from gensim import corpora, models, similarities
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
import numpy as np
from sklearn.cluster import spectral_clustering
from model_draw import Content_process

class classify_spectral_clustering(Content_process):
    def __init__(self):
        Content_process.__init__(self)

    def classifySpeCluLsa(self, class_num):
        from draw_data import draw_data 
        draw_title = draw_data()
        lsa = models.LsiModel.load('model.lsa', mmap='r')
        logging.info("load lsa model!!")
        index = similarities.MatrixSimilarity.load('model_lsa.index')
        self.get_data(num=3000)
        (tfidf, dictionary) = self.get_tfidf(True, num=3000)

        hash_id2list = dict() # 保存id -> 下标 similar_matrix中对应使用
        for i in range(len(self.title_id)):
            hash_id2list[self.title_id[i]] = i

        logging.info('开始创建相似矩阵...')
        similar_matrix = np.zeros((len(tfidf),len(tfidf))) #存放相似度
        for i in range(len(tfidf)):
            sims = index[lsa[tfidf[i]]]
            for j,v in enumerate(sims): 
                similar_matrix[i][j] = v
                similar_matrix[j][i] = v
        logging.info('done,相似矩阵建立完成,使用普聚类进行分类...')
        labels = spectral_clustering(similar_matrix, n_clusters=class_num, eigen_solver='arpack')
        self.vector_table = [[] for i in range(class_num)]
        for i in range(len(labels)):
            self.vector_table[labels[i]].append(self.title_id[i])
        logging.info("print set... "+str(len(self.vector_table)))
        self.printTitleTOfile(hash_id2list)
        draw_title.draw_topic(self.vector_table, 30, '2015-09-25', '2015-12-25')

class class_optics_clustering(Content_process):
    def __init__(self):
        Content_process.__init__(self)

    def classifyoptCluLsa(self):
        from draw_data import draw_data
        from optics_cluster import optics_cly
        draw_title = draw_data()
        lsa = models.LsiModel.load('model.lsa', mmap='r')
        logging.info("load lsa model!!")
        index = similarities.MatrixSimilarity.load('model_lsa.index')
        self.get_data(num=500)
        (tfidf, dictionary) = self.get_tfidf(True, num=500)

        hash_id2list = dict() # 保存id -> 下标 similar_matrix中对应使用
        for i in range(len(self.title_id)):
            hash_id2list[self.title_id[i]] = i
        
        logging.info('开始创建相似距离...')
        similar_matrix = dict()
        for i in range(len(tfidf)):
            sims = index[lsa[tfidf[i]]]
            for j,v in enumerate(sims):
                if v >= 0.3:
                    similar_matrix[(self.title_id[i], self.title_id[j])] = 1 - v
        logging.info('done,建立完成,使用optics进行分类...')

        opc = optics_cly(0.2, 0.3, 7, similar_matrix, self.title_id)
        (self.vector_table, n_list) = opc.runOptics()
        self.print_nlist(hash_id2list, n_list)
        self.printTitleTOfile(hash_id2list)
        draw_title.draw_topic(self.vector_table, 30, '2015-09-25', '2015-12-25')
        
    def print_nlist(self, hash_i, nlist):
        import codecs
        write_file = codecs.open('write_optisc.txt', 'w', 'utf-8')
        for i in range(len(nlist)):
            write_file.write(str(i) + self.title_name[hash_i[nlist[i]]] +
            '\n')
        write_file.close()
         
        
if __name__ == '__main__':
    #csc = classify_spectral_clustering()
    #csc.lsa_model(False, 70)
    #csc.classifySpeCluLsa(10)
    
    osc = class_optics_clustering()
    osc.classifyoptCluLsa()
