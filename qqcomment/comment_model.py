# -*- coding:utf-8
'''
    create at 2016-02-26
    author:yx
'''
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
from gensim import corpora, models, similarities
import logging
from model_draw import Content_process
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class Comment_Content_process(Content_process):
    def __init__(self):
        Content_process.__init__(self)
    
    def get_data(self, begin='2015-09-25', end='2015-11-25', num=500,
        update_top_num = True, contain_word = None):
        from draw_data import draw_data
        title = draw_data()
        title_item = title.get_title_data(begin, end, num)
        logging.info('总数: ' + str(title_item.count()))
        cti = 0
        for ti in title_item:
            cti += 1
            logging.info('第' + str(cti))
            self.title_name.append(ti['title_content'])
            titleid = ti['_id']
            comment2title = title.title_comment(titleid)
            comment_text = ""
            for ci in comment2title:
                comment_text  = comment_text + ci['comments'] + '。'
            self.title_content.append(comment_text)
            self.title_id.append(titleid)
        print "文章(评论)总数：%d"%(len(self.title_name))

    def lsa_model(self, use_old_dicdict = True): 
        self.get_data(num=3000)
        (tfidf, dictionary) = self.get_tfidf(use_old_dicdict, num=3000)
        self.topic_num = 20
        lsa = models.lsimodel.LsiModel(corpus=tfidf, id2word=dictionary,
        num_topics=self.topic_num)
        lsa.print_topics(self.topic_num)
        lsa.save('./model.lsa')
        index = similarities.MatrixSimilarity(lsa[tfidf])
        index.save('./model_lsa.index')

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

if __name__ == "__main__":
    cp = Comment_Content_process()
    #cp.lda_model(False)
    #cp.similarty()
    #cp.similarty_all()
    #cp.lsa_model()
    #cp.similarty_lsa()
    #cp.lda_model(False)
    cp.dbscan_lsa()
