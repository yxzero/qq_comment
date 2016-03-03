# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo

class QqcommentPipeline(object):
    def __init__(self):
        self.mongo_uri = 'mongodb://localhost:27017/'
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client['qqcomment']

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        collection_name = item.__class__.__name__
        try:
            if collection_name == 'TitleItem':
                self.db[collection_name].update({'_id': item['_id']}, dict(item), upsert = True)
            elif collection_name == 'CommentItem':
                self.db[collection_name].insert(dict(item))
            else:
                self.db['TitleItem'].update({'_id': item['_id']}, {"$set": {'num': item['num']}})
        except Exception, e:
            pass
            #print str(e)
        return item
