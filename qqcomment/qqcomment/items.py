# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TitleItem(scrapy.Item):
    _id = scrapy.Field()
    title_content = scrapy.Field()
    title_url = scrapy.Field()
    title_text = scrapy.Field()
    title_time = scrapy.Field()
    update_time = scrapy.Field()
    num = scrapy.Field()

class CommentItem(scrapy.Item):
    title_id = scrapy.Field()
    comments = scrapy.Field()
    pid = scrapy.Field()
    _id = scrapy.Field()
    user = scrapy.Field()
    time = scrapy.Field()

class UpdateItem(scrapy.Item):
    _id = scrapy.Field()
    num = scrapy.Field()
