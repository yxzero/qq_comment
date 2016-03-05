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
        self.get_data(num=1000)
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
        
if __name__ == '__main__':
    csc = classify_spectral_clustering()
    #csc.lsa_model(False, 70)
    csc.classifySpeCluLsa(7) 
