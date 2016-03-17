# -*- coding:utf-8
'''
    create at 2016-03-09
    author:yx
'''

import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
from gensim import corpora, models, similarities
import logging
import jieba.posseg as pseg
import jieba
jieba.enable_parallel(4) # 开启并行分词模式，参数为并行进程数
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
from draw_data import time_between

class use_comment_classify():
    def __init__(self):
        self.title_name = {}
        self.vector_table = []
        self.word2topic = {}
        self.topic_word_num = {}
        self.topic2num = {} #标记topic的标号
        self.num2topic = [] #标记num的topic名

    def load_manual(self, file_name='manual_type1.txt'):
        import codecs
        try:
            topicfile = codecs.open(file_name, 'r', 'utf-8')
            for i in topicfile.readlines():
                word = i.strip().split('\t')
                self.word2topic[word[0]] = word[1]
                self.topic_word_num[word[1]] = 0
            topicfile.close()
        except Exception,e:
            logging.info(str(e))

    def load_manual2(self, begin, end, file_name='manual_type1.txt'):
        import codecs
        import copy
        lasttime = time_between(begin, end+' 00:00', 30)
        tempdict = [0 for i in range(lasttime)]
        try:
            topicfile = codecs.open(file_name, 'r', 'utf-8')
            for i in topicfile.readlines():
                word = i.strip().split('\t')
                self.word2topic[word[0]] = word[1]
                self.topic_word_num[word[1]] = copy.deepcopy(tempdict)
            topicfile.close()
        except Exception,e:
            logging.info(str(e))

    def printTitleTOfile(self):
        import codecs
        try:
            topic_file = codecs.open('topic_file.txt', 'w', 'utf-8')
            for i in range(len(self.vector_table)):
                topic_file.write(str(i) + ' ' + self.num2topic[i] + '\n')
                print str(i) + ' ' + self.num2topic[i]
                for j in self.vector_table[i]:
                    topic_file.write(self.title_name[j]+'\n')
            topic_file.close()
        except Exception,e:
            logging.info(str(e))

    def printTitleTOfile2(self, begin, end, temp_k):
        import codecs
        from matplotlib import pyplot as plt
        import numpy as np
        '''
        color_list = ['#990033','#FF66FF','#660099','#CC9909',
        '#33CCCC','#000000','#CC6699','#FF33FF','#993366','#000CC0','#333366'
        ,'#330099','#330033','#FF3300','#CC6600','#33FF33','#006600','#339900','#33CC66']
        '''
        color_list = ['b-','g-','r-','c-','m-','y-','k-','b--'
        ,'g--','r--','c--','m--','y--','k--']
        try:
            topic_file = codecs.open('topic_file.txt', 'w', 'utf-8')
            color_l = 0
            for i in self.topic_word_num.keys():
                topic_file.write(i + '\n')
                printt = np.argmax(self.topic_word_num[i])
                plt.plot(range(len(self.topic_word_num[i])), self.topic_word_num[i], color_list[color_l%14])
                plt.text(printt, self.topic_word_num[i][printt], i)
                color_l += 1
            topic_file.close()
            plt.title(begin + u" 到 " + end)
            plt.xlabel("per " + str(temp_k) + " mins")
            plt.show()
        except Exception,e:
            logging.info(str(e))

    def use_jieba(self, text, tid): 
        from operator import itemgetter
        import copy
        tempcopy = copy.deepcopy(self.topic_word_num)
        cuted_t = []
        allow_pos = ['ns', 'n'] # 保留的词性
        words = pseg.cut(text)
        for word, flag in words:
            if flag in allow_pos:
                if word in self.word2topic:
                    tempcopy[self.word2topic[word]] += 1
        type_topic = max(tempcopy.iteritems(), key=itemgetter(1))
        print type_topic
        if type_topic[1] > 0:
            if type_topic[0] in self.topic2num:
                self.vector_table[self.topic2num[type_topic[0]]].append(tid)
            else:
                self.topic2num[type_topic[0]] = len(self.vector_table)
                self.num2topic.append(type_topic[0])
                self.vector_table.append([tid])

    def use_jieba2(self, text, begin, last_time, time_k): 
        from operator import itemgetter
        import copy
        allow_pos = ['ns', 'n'] # 保留的词性
        words = pseg.cut(text)
        for word, flag in words:
            if flag in allow_pos:
                if word in self.word2topic:
                    tempk = time_between(begin, last_time, time_k)
                    self.topic_word_num[self.word2topic[word]][tempk] += 1
        
    def get_data(self, begin='2015-09-25', end='2015-11-25', num=500,
        update_top_num = True, contain_word = None):
        from draw_data import draw_data
        self.load_manual()
        title = draw_data()
        title_item = title.get_title_data(begin, end, num)
        logging.info('总数: ' + str(title_item.count()))
        cti = 0
        for ti in title_item:
            cti += 1
            logging.info('第' + str(cti))
            titleid = ti['_id']
            commentcontent = ''
            comment2title = title.title_comment(titleid)
            for ci in comment2title:
                commentcontent = commentcontent + ci['comments'] + '。' 
            self.title_name[titleid] = ti['title_content']
            self.use_jieba(commentcontent, titleid)
        self.printTitleTOfile()
        # 画图
        draw_title = draw_data()
        draw_title.draw_topic(self.vector_table, 30, '2015-09-25', '2015-11-25') 
        print "文章(评论)总数：%d"%(len(self.title_name))

    def get_data2(self, begin='2015-09-25', end='2015-11-25', num=500,
        update_top_num = True, contain_word = None):
        from draw_data import draw_data
        self.load_manual2(begin, end)
        Comment = draw_data()
        comments_temp = Comment.get_comment_data(begin, end)
        logging.info("评论共：" + str(comments_temp.count()))
        cci = 0
        for ci in comments_temp:
            cci += 1
            if cci%10000 == 0:
                logging.info('第 '+str(cci)+'个')
            self.use_jieba2(ci['comments'], begin, ci['time'], 30)
        self.printTitleTOfile2(begin, end, 30)

        
if __name__ == '__main__':
      use_conment = use_comment_classify()
      use_conment.get_data2(num=7000)
