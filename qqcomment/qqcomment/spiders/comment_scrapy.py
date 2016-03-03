# -*-coding:utf-8-*-
'''
Created on 2015年8月29日

@author: yx
'''
import scrapy
import re
import urllib
import time
from qqcomment.items import CommentItem
from qqcomment.items import TitleItem
from qqcomment.items import UpdateItem


class get_comment(scrapy.Spider):
    name = "comment_scrapy"

    def __init__(self):
        self.start_urls = ['http://news.qq.com/']

    def parse(self, response):
        before_list = {}
        try:
            f = open('url.txt', 'r')
            for i in f.readlines():
                url_info = i.strip().split()
                print 'get old ' + url_info[0]
                before_list[url_info[0]] = None
                request = scrapy.Request(url_info[0], callback=self.comment_qq)
                request.meta['update_time'] = url_info[1]
                yield request
            f.close()
            f = open('url.txt', 'w')
            f.write('')
            f.close()
        except Exception, e:
            print str(e)
        try:
            url_list = response.xpath('//*[@id="mainTabPanel"]/div/div/em/span/span/a/@href').extract()
        except Exception, e:
            print str(e)
        for i in url_list: 
            if i not in before_list:
                print 'get ' + i
                request = scrapy.Request(i, callback=self.comment_qq)
                request.meta['update_time'] = None
                yield request

    # qq
    def comment_qq(self, response):
        # update_time 没有的话用文章时间
        created_time = response.xpath('//*[@id="C-Main-Article-QQ"]/div[1]/div[1]/div[1]/span[6]/text()').extract_first()
        if created_time == None:
            created_time = response.xpath('//*[@id="C-Main-Article-QQ"]/div[1]/div[1]/div[1]/span[5]/text()').extract_first()
        if created_time == None:
            return
        if response.meta['update_time']:
            update_time = response.meta['update_time']
        else:
            update_time = created_time
        # 获得文章id
        listp = re.findall(r'cmt_id\s*?=\s*?(\d*?);', response.body, re.S)
        if len(listp) == 0:
            listp = re.findall(r'aid\s*?:\s*?"(\d*?)",', response.body, re.S)
        cmt_id = listp[0]
        title_id = cmt_id
        url = 'http://coral.qq.com/article/' + cmt_id +'/comment?commentid=0&reqnum=10&tag=&callback=mainComment'
        request = scrapy.Request(url, callback=self.commentitem_qq)
        request.meta['title_id'] = title_id
        request.meta['update_time'] = update_time
        yield request
        # 获得文章详细信息
        if response.xpath('//*[@id="C-Main-Article-QQ"]/div[1]/h1/text()').extract_first():
            title = response.xpath('//*[@id="C-Main-Article-QQ"]/div[1]/h1/text()').extract_first()
        else:
            title = response.xpath('//*[@id="Main-P-QQ"]/div[1]/h1/text()').extract_first() 
        text_list = response.xpath('//*[@id="Cnt-Main-Article-QQ"]/p/text()').extract()
        num = response.xpath('//*[@id="cmtNum"]/text()').extract_first()
        text_p = ''
        for i in text_list:
            text_p += i
        titleitem = TitleItem()
        titleitem['_id'] = title_id
        titleitem['title_content'] = title
        titleitem['title_url'] = response.url
        titleitem['title_time'] = created_time
        titleitem['title_text'] = text_p
        titleitem['update_time'] = time.strftime("%Y-%m-%d %H:%M", time.localtime())
        titleitem['num'] = int(num)
        yield titleitem  
        
        
    def commentitem_qq(self, response):
        import json 
        update_time = response.meta['update_time']
        title_id = response.meta['title_id']
        json_c = json.loads(
            re.findall(r'mainComment\((.*)\)', response.body, re.S)[0]
        )
        commentid = json_c['data']['last']
        url = 'http://coral.qq.com/article/' + title_id +\
            '/comment?commentid=' + commentid +\
            '&reqnum=10&tag=&callback=mainComment' 
        for each_item in json_c['data']['commentid']:
            comments = CommentItem()
            comments['_id'] = each_item['id']
            comments['title_id'] = title_id
            comments['comments'] = each_item['content']
            comments['time'] = time.strftime("%Y-%m-%d %H:%M", time.localtime(each_item['time']))
            if comments['time'] <= update_time:
                updataitem = UpdateItem()
                updataitem['_id'] = title_id
                updataitem['num'] = json_c['data']['total']
                yield updataitem
                print 'update ' + title_id + ' ' + str(updataitem['num'])
                return
            comments['user'] = each_item['userid']
            if cmp(each_item['parent'], '0') == 0:
                comments['pid'] = None
            else:
                comments['pid'] = each_item['parent']
            yield comments
        if json_c['data']['hasnext']:
            request = scrapy.Request(url, callback=self.commentitem_qq)
            request.meta['title_id'] = title_id
            request.meta['update_time'] = update_time
            yield request 
        else:
            updataitem = UpdateItem()
            updataitem['_id'] = title_id
            updataitem['num'] = json_c['data']['total']
            yield updataitem
            print 'get ' + title_id + ' ' + str(updataitem['num'])
            return
