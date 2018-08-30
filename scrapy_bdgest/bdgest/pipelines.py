# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from .items import AuthorsItem, SeriesItem, ComicsItem
from scrapy import log
import pymongo


class MongoDBPipeline(object):

    def __init__(self):
        connection = pymongo.MongoClient("mongo")
        self.db = connection['bdgest']

    def process_item(self, item, spider):
        if isinstance(item, AuthorsItem):
            self.collection = self.db['authors']
            valid = True
            for data in item:
                if not data:
                    valid = False
                    raise DropItem("Missing {0}!".format(data))
            if valid:
                self.collection.insert_one(dict(item))
                log.msg("Author added to MongoDB database!",
                        level=log.DEBUG, spider=spider)
            return item

        elif isinstance(item, SeriesItem):
            self.collection = self.db['series']
            valid = True
            for data in item:
                if not data:
                    valid = False
                    raise DropItem("Missing {0}!".format(data))
            if valid:
                self.collection.insert_one(dict(item))
                log.msg("Series added to MongoDB database!",
                        level=log.DEBUG, spider=spider)
            return item

        elif isinstance(item, ComicsItem):
            self.collection = self.db['comics']
            valid = True
            for data in item:
                if not data:
                    valid = False
                    raise DropItem("Missing {0}!".format(data))
            if valid:
                self.collection.insert_one(dict(item))
                log.msg("Comic added to MongoDB database!",
                        level=log.DEBUG, spider=spider)
            return item
