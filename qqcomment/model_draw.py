# -*- coding:utf-8
'''
    create at 2015-10-29
    author:yx
'''
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
from gensim import corpora, models, similarities
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class Content_process():
    def __init__(self): 
        self.title_content = []
        self.title_name = [] 
        self.topic_num = 0
        self.vector_table = []
        self.title_id = []

    def get_data(self, begin='2015-09-25', end='2015-11-25', num=10000,
        update_top_num = True, contain_word = None):
        import re
        from draw_data import draw_data
        title = draw_data()
        title_item = title.get_title_data(begin, end, num)
        if contain_word:
            for ti in title_item:
                title_text = ti['title_text']
                for word in contain_word:
                    if re.search(word, title_text):
                        self.title_name.append(ti['title_content'])
                        self.title_content.append(title_text)
                        self.title_id.append(ti['_id'])
                        break
        else:
            for ti in title_item:
                self.title_name.append(ti['title_content'])
                self.title_content.append(ti['title_text'])
                self.title_id.append(ti['_id'])
        print "文章总数：%d"%(len(self.title_name))
        if update_top_num:
            self.topic_num = len(self.title_name)

    def printTitleTOfile(self, hash_id2list):
        import codecs
        topic_file = codecs.open('topic_file.txt', 'w')
        for i in range(len(self.vector_table)):
            topic_file.write(str(i)+'\n')
            print i
            for j in self.vector_table[i]:
                print self.title_name[hash_id2list[j]]
                topic_file.write(self.title_name[hash_id2list[j]]+'\n')
        topic_file.close()

    # 使用jieba进行分词以及词性提取
    def use_jieba(self):
        import jieba.posseg as pseg
        import jieba
        jieba.enable_parallel(4) # 开启并行分词模式，参数为并行进程数
        cuted_t = []
        allow_pos = ['ns', 'n', 'vn', 'v'] # 保留的词性
        for i in self.title_content:
            words = pseg.cut(i)
            flit_words = []
            for word, flag in words:
                if flag in allow_pos:
                    flit_words.append(word)
            cuted_t.append(flit_words)
        return cuted_t

    def similarty_lsa(self, begin='2015-09-25', end='2015-11-25', num=10000):
        from draw_data import draw_data
        draw_title = draw_data()
        lsa = models.LsiModel.load('model.lsa', mmap='r')
        logging.info("load lsa model!!")
        index = similarities.MatrixSimilarity.load('model_lsa.index')
        self.title_name = []
        self.title_content = []
        self.get_data(num=10000)
        title_old_id = self.title_id[:]
        title_old_name = self.title_name[:]
        (tfidf, dictionary) = self.get_tfidf()
        self.title_name = []
        self.title_content = []
        self.title_id = []
        self.get_data(num=3000)
        (tfidf_less, dictionary) = self.get_tfidf(num=3000)

        hash_id2list = dict()
        for i in range(len(self.title_id)):
            hash_id2list[self.title_id[i]] = i
        
        logging.info("开始创造关联树...")
        for i in range(len(tfidf)):
            print title_old_name[i]
            t_set_id = -1
            t_set = set()
            for t in range(len(self.vector_table)):
                if title_old_id[i] in self.vector_table[t]:
                    t_set_id = -2
                    break
            if t_set_id == -1:
                self.vector_table.append(t_set)
                t_set_id = len(self.vector_table)-1
                t_set.add(title_old_id[i])
            if t_set_id >= 0:
                t_set = self.find_deep(index, tfidf_less, lsa, tfidf[i], t_set, hash_id2list)
        logging.info("print set... "+str(len(self.vector_table)))
        self.printTitleTOfile(hash_id2list)
        draw_title.draw_topic(self.vector_table, 30, '2015-09-25', '2015-10-10')

    def dbscan_lsa(self, begin='2015-09-25', end='2015-11-25', num=10000):
        from draw_data import draw_data
        draw_title = draw_data()
        lsa = models.LsiModel.load('model.lsa', mmap='r')
        logging.info("load lsa model!!")
        index = similarities.MatrixSimilarity.load('model_lsa.index')
        self.title_name = []
        self.title_content = []
        self.title_id = []
        self.get_data(num=3000)
        (tfidf, dictionary) = self.get_tfidf(True, num=3000)
        #self.get_data(num=3000)
        #(tfidf, dictionary) = self.get_tfidf(False)

        hash_id2list = dict() # 保存id -> 下标 similar_matrix中对应使用
        for i in range(len(self.title_id)):
            hash_id2list[self.title_id[i]] = i
        
        logging.info("开始创造关联树...")
        for i in range(len(tfidf)):
            t_set_id = -1
            t_set = set()
            for t in range(len(self.vector_table)):
                if self.title_id[i] in self.vector_table[t]:
                    t_set_id = -2
                    break
            if t_set_id == -1:
                t_set.add(self.title_id[i])
                t_set = self.find_deep_dbscan(index, tfidf, lsa, tfidf[i], t_set, hash_id2list)
                if len(t_set) > 7:
                    print self.title_name[i]
                    self.vector_table.append(t_set)
        logging.info("print set... "+str(len(self.vector_table)))
        self.printTitleTOfile(hash_id2list)
        draw_title.draw_topic(self.vector_table, 30, '2015-09-25', '2015-10-10')

    def find_deep_dbscan(self, index, tfidf, lsa, temptfidf, allset, hash_id2list):
        sims = index[lsa[temptfidf]]
        sims = sorted(enumerate(sims), key=lambda item: -item[1])
        subset = set()
        if len([i for i in sims if i[1] >= 0.85]) > 7:
            for j in sims:
                if j[1] > 0.85: 
                    subset.add(self.title_id[j[0]])
                    print str(j) + '**' + self.title_name[j[0]]
                elif j[1] < 0.7:
                    continue
                else:
                    print str(j) + '#' + self.title_name[j[0]]
            addset = subset - allset 
            while(len(addset)>0):
                a = addset.pop()
                allset.add(a)
                temptfidf = tfidf[hash_id2list[a]]
                allset = self.find_deep_dbscan(index, tfidf, lsa, temptfidf, allset, hash_id2list)
                addset = subset - allset
        return allset

    def find_deep(self, index, tfidf_less, lsa, temptfidf, allset, hash_id2list):
        sims = index[lsa[temptfidf]]
        sims = sorted(enumerate(sims), key=lambda item: -item[1])
        subset = set()
        for j in sims:
            if j[1] > 0.6: 
                subset.add(self.title_id[j[0]])
                print str(j) + '**' + self.title_name[j[0]]
            elif j[1] < 0.5:
                continue
            else:
                print str(j) + '#' + self.title_name[j[0]]
        addset = subset - allset 
        while(len(addset)>0):
            a = addset.pop()
            allset.add(a)
            temptfidf = tfidf_less[hash_id2list[a]]
            allset = self.find_deep(index, tfidf_less, lsa, temptfidf, allset, hash_id2list)
            addset = subset - allset
        return allset

    def similarty_lda(self, begin='2015-09-25', end='2015-11-25', num=10000):
        from draw_data import draw_data
        draw_title = draw_data()
        lda = models.ldamodel.LdaModel.load('model.lda', mmap='r')
        logging.info("load lda model!!")
        index = similarities.MatrixSimilarity.load('model_lda.index')
        self.title_name = []
        self.title_content = []
        self.get_data(num=10000)
        title_old_id = self.title_id[:]
        title_old_name = self.title_name[:]
        (tfidf, dictionary) = self.get_tfidf()
        self.title_name = []
        self.title_content = []
        self.title_id = []
        self.get_data(num=3000)
        (tfidf_less, dictionary) = self.get_tfidf(num=3000)

        hash_id2list = dict()
        for i in range(len(self.title_id)):
            hash_id2list[self.title_id[i]] = i
        
        logging.info("开始创造关联树...")
        for i in range(len(tfidf)):
            print title_old_name[i]
            t_set_id = -1
            t_set = set()
            for t in range(len(self.vector_table)):
                if title_old_id[i] in self.vector_table[t]:
                    t_set_id = -2
                    break
            if t_set_id == -1:
                self.vector_table.append(t_set)
                t_set_id = len(self.vector_table)-1
                t_set.add(title_old_id[i])
            if t_set_id >= 0:
                t_set = self.find_deep(index, tfidf_less, lda, tfidf[i], t_set, hash_id2list)
        logging.info("print set... "+str(len(self.vector_table)))
        self.printTitleTOfile(hash_id2list)
        draw_title.draw_topic(self.vector_table, 30, '2015-09-25', '2015-11-20')

    # 去掉频率为1的词
    def del_ones(self, cuted_t):
        logging.info("delete appear only onces words!!")
        all_word = sum(cuted_t, [])
        word_once = set(word for word in set(all_word) if
        all_word.count(word)==1)
        return [[word for word in text if word not in word_once] for text in
        cuted_t]

    def get_tfidf(self, use_old_dicdict = True, begin='2015-09-25',
    end='2015-11-25', num=10000):
        cuted_t = self.use_jieba()
        #cuted_t = self.del_ones(cuted_t)
        # dictionary = corpora.Dictionary(cuted_t)
        if use_old_dicdict:
            dictionary = corpora.Dictionary.load('deerwester.dict')
        else:
            dictionary = corpora.Dictionary(cuted_t)
            dictionary.save('./deerwester.dict')

        logging.info("created dictionary of doc")
        corpus = [dictionary.doc2bow(text) for text in cuted_t]
        logging.info("created corpus!")
        title2bow = {}
        tfidf = models.TfidfModel(corpus) 
        return (tfidf[corpus], dictionary)

    def lsa_model(self, use_old_dicdict = True, topic_num = 50): 
        self.get_data(num=500)
        (tfidf, dictionary) = self.get_tfidf(use_old_dicdict, num=500)
        self.topic_num = topic_num
        lsa = models.lsimodel.LsiModel(corpus=tfidf, id2word=dictionary,
        num_topics=self.topic_num)
        lsa.print_topics(self.topic_num)
        lsa.save('./model.lsa')
        index = similarities.MatrixSimilarity(lsa[tfidf])
        index.save('./model_lsa.index')

    def lda_model(self, use_old_dicdict = True):
        self.get_data(num=3000)
        # self.get_data()
        (tfidf, dictionary) = self.get_tfidf(use_old_dicdict, num=3000)
        self.topic_num = 300
        lda = models.ldamodel.LdaModel(corpus=tfidf, id2word=dictionary,
        num_topics=self.topic_num)
        lda.print_topics(self.topic_num)
        lda.save('./model.lda')
        index = similarities.MatrixSimilarity(lda[tfidf])
        index.save('./model_lda.index')

if __name__ == "__main__":
    cp = Content_process()
    #cp.lda_model(False)
    #cp.similarty()
    #cp.similarty_all()
    cp.lsa_model(False,100)
    #cp.similarty_lsa()
    #cp.lda_model()
    #cp.dbscan_lsa()
