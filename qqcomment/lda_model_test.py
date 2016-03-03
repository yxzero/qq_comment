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
                        break
        else:
            for ti in title_item:
                self.title_name.append(ti['title_content'])
                self.title_content.append(ti['title_text'])
        print "文章总数：%d"%(len(self.title_name))
        if update_top_num:
            self.topic_num = len(self.title_name)
    
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

    def similarty(self):
        lda = models.ldamodel.LdaModel.load('model.lda', mmap='r')
        logging.info("load lda model!!")
        # index = similarities.MatrixSimilarity.load('model.index')
        title2bow = {}
        class_table = dict()
        for i in range(self.topic_num):
            class_table[i] = []
        try:
            f = open('title2bow.txt', 'r')
            title2bow = eval(f.read())
            f.close()
            logging.info("read title2bow!!")
        except Exception,e:
            print str(e)
        for i in title2bow.keys(): 
            vet_lda = lda[title2bow[i]]
            if len(vet_lda) > 0:
                j = max(vet_lda, key=lambda item: -item[1])
                class_table[j[0]].append([i,j[1]])
        for i in range(self.topic_num):
            printstr = str(i) + ': '
            for t in lda.show_topic(i):
                printstr += str(t[1]) + ':' + str(t[0]) + '+'
            print printstr
            for j in class_table[i]:
                print j[0] + ' ' + str(j[1])

    def similarty_all(self, begin='2015-09-25', end='2015-11-25', num=10000):
        contain_word = [u'屠呦呦',u'天价虾', u'TPP', u'二胎', u'巴黎', u'习马会',
        u'丹东一号']
        lda = models.ldamodel.LdaModel.load('model.lda', mmap='r')
        logging.info("load lda model!!")
        self.get_data(begin='2015-09-25', end='2015-11-25', num=1000)
        (tfidf, dictionary) = self.get_tfidf()
        class_table = dict()
        self.topic_num = 200
        for i in range(self.topic_num):
            # if lda.show_topic(i)[0][0] < 0.01: 
            class_table[i] = []
        for i in range(len(tfidf)): 
            vet_lda = lda[tfidf[i]]
            if len(vet_lda) > 0:
                j = max(vet_lda, key=lambda item: -item[1])
                class_table[j[0]].append([self.title_name[i],j[1]])
        for i in range(self.topic_num):
            printstr = str(i) + ': '
            for t in lda.show_topic(i):
                printstr += str(t[1]) + ':' + str(t[0]) + '+'
            print printstr
            for j in class_table[i]:
                print j[0] + ' ' + str(j[1])
        print 'another way!!'
        index = similarities.MatrixSimilarity.load('model_lsa.index')
        self.title_name = []
        self.title_content = []
        self.get_data(contain_word = contain_word, num=10000)
        (tfidf, dictionary) = self.get_tfidf()
        self.title_name = []
        self.title_content = []
        self.get_data(num=3000)
        for i in range(len(tfidf)):
            sims = index[lda[tfidf[i]]]
            sims = sorted(enumerate(sims), key=lambda item: -item[1])
            for j in sims:
                print str(j) + '#' + self.title_name[j[0]]

    def similarty_lsa(self, begin='2015-09-25', end='2015-11-25', num=10000):
        contain_word = [u'屠呦呦',u'天价虾', u'TPP', u'二胎', u'巴黎', u'习马会',
        u'丹东一号'] 
        lsa = models.LsiModel.load('model.lsa', mmap='r')
        logging.info("load lsa model!!")
        self.get_data(begin='2015-09-25', end='2015-11-25', num=1000)
        (tfidf, dictionary) = self.get_tfidf()
        class_table = dict()
        self.topic_num = 200
        for i in range(self.topic_num):
            # if lda.show_topic(i)[0][0] < 0.01: 
            class_table[i] = []
        for i in range(len(tfidf)): 
            vet_lsa = lsa[tfidf[i]]
            if len(vet_lsa) > 0:
                j = max(vet_lsa, key=lambda item: -item[1])
                class_table[j[0]].append([self.title_name[i],j[1]])
        for i in range(self.topic_num):
            printstr = str(i) + ': '
            for t in lsa.show_topic(i):
                printstr += str(t[1]) + ':' + str(t[0]) + '+'
            print printstr
            for j in class_table[i]:
                print j[0] + ' ' + str(j[1])
        print 'another way!!'
        index = similarities.MatrixSimilarity.load('model_lda.index')
        self.title_name = []
        self.title_content = []
        self.get_data(contain_word = contain_word, num=10000)
        (tfidf, dictionary) = self.get_tfidf()
        self.title_name = []
        self.title_content = []
        self.get_data(num=3000)
        for i in range(len(tfidf)):
            sims = index[lsa[tfidf[i]]]
            sims = sorted(enumerate(sims), key=lambda item: -item[1])
            for j in sims:
                print str(j) + '#' + self.title_name[j[0]]

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
        cuted_t = self.del_ones(cuted_t)
        # dictionary = corpora.Dictionary(cuted_t)
        if use_old_dicdict:
            dictionary = corpora.Dictionary.load('deerwester.dict')
        else:
            self.title_name = []
            self.title_content = []
            self.get_data(begin=begin, end=end, num=num, update_top_num = False)
            cuted_all = self.use_jieba()
            cuted_all = self.del_ones(cuted_all)
            dictionary = corpora.Dictionary(cuted_all)
            dictionary.save('./deerwester.dict')

        logging.info("created dictionary of doc")
        corpus = [dictionary.doc2bow(text) for text in cuted_t]
        logging.info("created corpus!")
        title2bow = {}
        tfidf = models.TfidfModel(corpus) 
        return (tfidf[corpus], dictionary)
        
    def lda_model(self, use_old_dicdict = True):
        contain_word = [u'屠呦呦',u'天价虾', u'TPP', u'二胎', u'巴黎', u'习马会',
        u'慰安妇', u'丹东一号']
        self.get_data(num=3000)
        # self.get_data()
        (tfidf, dictionary) = self.get_tfidf(use_old_dicdict, num=3000)
        self.topic_num = 200
        lda = models.ldamodel.LdaModel(corpus=tfidf, id2word=dictionary,
        num_topics=self.topic_num)
        lda.print_topics(self.topic_num)
        lda.save('./model.lda')
        index = similarities.MatrixSimilarity(lda[tfidf])
        index.save('./model_lda.index')

    def lsa_model(self, use_old_dicdict = True):
        contain_word = [u'屠呦呦',u'天价虾', u'TPP', u'二胎', u'巴黎', u'习马会',
        u'慰安妇', u'丹东一号'] 
        self.get_data(num=3000)
        (tfidf, dictionary) = self.get_tfidf(use_old_dicdict, num=3000)
        self.topic_num = len(contain_word)
        self.topic_num = 200
        lsa = models.lsimodel.LsiModel(corpus=tfidf, id2word=dictionary,
        num_topics=self.topic_num)
        lsa.print_topics(self.topic_num)
        lsa.save('./model.lsa')
        index = similarities.MatrixSimilarity(lsa[tfidf])
        index.save('./model_lsa.index')

if __name__ == "__main__":
    cp = Content_process()
    #cp.lda_model(False)
    #cp.similarty()
    cp.similarty_all()
    #cp.lsa_model(False)
    #cp.similarty_lsa()
