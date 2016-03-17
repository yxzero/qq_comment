#-*- coding:utf-8
'''
    created at 2016-02-24
    author:yx
'''
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
from gensim import corpora, models, similarities
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class Comment_freq():
    def __init__(self):
        self.vectobi = {}

    def print_and_sorted(self, comments_t):
        from operator import itemgetter    
        import jieba.posseg as pseg
        import jieba
        jieba.enable_parallel(4) # 开启并行分词模式，参数为并行进程数
        cci = 0
        allow_pos = ['ns', 'n']
        for ci in comments_t:
            cci += 1
            if cci%50 == 0:
                logging.info('pro ' + str(cci))
            words = pseg.cut(ci)
            for word, flag in words:
                if flag in allow_pos:
                    if word in self.vectobi:
                        self.vectobi[word] += 1
                    else:
                        self.vectobi[word] = 1
        logging.info("sorted...")
        word_freq = sorted(self.vectobi.iteritems(), key=itemgetter(1),
            reverse=True)
        freqfile = open('freq.txt', 'w')
        for i in word_freq:
            freqfile.write(i[0] + '\t' + str(i[1]) + '\n')
        freqfile.close()
        logging.info("length:" + str(len(word_freq)) + " writed 100 in freq.txt")
            
        
    def get_data(self, begin='2015-09-25', end='2015-11-25'):
        from draw_data import draw_data
        Comment = draw_data()
        comments_temp = Comment.get_comment_data(begin, end)
        logging.info("评论共：" + str(comments_temp.count()))
        cci = 0
        comments_t = []
        tc = ''
        for ci in comments_temp:
            cci += 1
            if cci%1000 == 0:
                comments_t.append(tc)
                tc = ''
            else:
                tc = tc + ' ' + ci['comments']
        logging.info('合并之后: ' + str(len(comments_t)))
        return comments_t

def count_day(begin='2015-09-25',days=60):
    import datetime
    from matplotlib import pyplot as plt
    import numpy as np
    from draw_data import draw_data
    Comment = draw_data()
    begin = datetime.datetime.strptime(begin, '%Y-%m-%d')
    end = begin + datetime.timedelta(days=1)
    len_comment = []
    for i in range(days):
        comments_temp = Comment.get_comment_data(str(begin), str(end))
        len_comment.append(comments_temp.count())
        tempend = end
        end = end + datetime.timedelta(days=1)
        begin = tempend
    plt.bar(range(len(len_comment)), len_comment, width=1,align='edge', color='green')
    plt.show()

if __name__ == '__main__':
    #cf = Comment_freq()
    #comments_t = cf.get_data()
    #cf.print_and_sorted(comments_t)
    count_day()
    
