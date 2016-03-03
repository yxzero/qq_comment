# -*-coding:utf-8-*-
'''
Created on 2015年9月18日

@author: yx
'''
import pymongo
import time
import datetime

def get_url():
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['qqcomment']
    #db.authenticate("root","111111")
    two_day = (datetime.datetime.now() + datetime.timedelta(days=-3)).strftime("%Y-%m-%d %H:%M")
    cursor = db.TitleItem.find({"title_time": {"$gt": two_day}})
    try:
        f = open('url.txt', 'w')
        for i in cursor:
            f.write(i['title_url'] + '\t' + i['update_time'] + '\n')
        f.close()
    except Exception, e:
        print str(e)
    client.close() 
