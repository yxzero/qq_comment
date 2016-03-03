# -*-coding:utf-8-*-
'''
Created on 2015年8月30日

@author: yx
'''
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
import multiprocessing
from get_url import get_url
import time

if __name__ == '__main__':
    runner = CrawlerRunner(get_project_settings())
    d = runner.crawl('comment_scrapy')
    d.addBoth(lambda _: reactor.stop())
    reactor.run()  # the script will block here until the crawling is finished
    print "get once!!"
    get_url()
    print "update url!!" + ' at ' + time.strftime("%Y-%m-%d %H:%M", time.localtime())
