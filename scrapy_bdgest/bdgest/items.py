"""
"""

# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class AuthorsItem(scrapy.Item):

    _id = scrapy.Field()
    url = scrapy.Field()
    first_name = scrapy.Field()
    last_name = scrapy.Field()
    nickname = scrapy.Field()
    full_name = scrapy.Field()
    country = scrapy.Field()
    web_page = scrapy.Field()
    birth_date = scrapy.Field()
    death_date = scrapy.Field()
    image = scrapy.Field()

class SeriesItem(scrapy.Item):

    _id = scrapy.Field()
    url = scrapy.Field()
    name = scrapy.Field()
    author_id = scrapy.Field()
    genre = scrapy.Field()
    status = scrapy.Field()
    volume_nb = scrapy.Field()
    volume = scrapy.Field()
    origin = scrapy.Field()
    lang = scrapy.Field()
    description = scrapy.Field()

class ComicsItem(scrapy.Item):

    _id = scrapy.Field()
    series_id = scrapy.Field()
    author_id = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    volume = scrapy.Field()
    scenario = scrapy.Field()
    illustration = scrapy.Field()
    coloring = scrapy.Field()
    legal_deposit = scrapy.Field()
    editor = scrapy.Field()
    collection = scrapy.Field()
    format = scrapy.Field()
    isbn = scrapy.Field()
    pages = scrapy.Field()
    translation = scrapy.Field()
    image = scrapy.Field()
    description = scrapy.Field()



