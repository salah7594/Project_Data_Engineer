"""
The database is dropped at start.
"""

# -*- coding: utf-8 -*-
import scrapy

from ..items import AuthorsItem, SeriesItem, ComicsItem

import unidecode
import re
import string
from pymongo import MongoClient
from datetime import datetime
client = MongoClient("mongo")
client.drop_database("bdgest")


class AuthorsSpider(scrapy.Spider):

    """start_urls: author names not starting with letters + author names from A to Z"""

    name = 'authors'
    allowed_domains = ['bedetheque.com']
    start_urls = ['https://www.bedetheque.com/liste_auteurs_BD_{0}.html'.format(x) for x in string.ascii_lowercase]
    start_urls.append('https://www.bedetheque.com/liste_auteurs_BD_0.html')
#    start_urls = ['https://www.bedetheque.com/liste_auteurs_BD_a.html']
    def parse(self, response):

        """Parse the start_urls, fetch author page url and call parse_authors with this url as response"""

        for author_page in response.xpath('//ul[@class="nav-liste"]/li')[-30:-10]:
            var_url = author_page.xpath("./a/@href").extract()[0]

            yield scrapy.Request(var_url, callback=self.parse_authors)

    def parse_authors(self, response):  
        """
        Parses the author's page. Retrieves their bdgest id, name, last name, nickname, country, personal webpage,
        birth date, death date and image url. A full name variable is created by combining name, last name and nickname.

        Args:
            response: a response page which is an author's page

        Yield:
            - scrapy.Request with the parse_series function as callback. The series type and author id are passed to it
            through the meta dictionary.
            - authors_item when all of his series and comics have been parsed.
        """
        authors_item = AuthorsItem()

        for x in response.xpath('//ul[@class="auteur-info"]/li'):
            var_label = x.xpath('./label/text()').extract()[0].split(" ")[0]
            if var_label == 'Identifiant':
                authors_item["_id"] = x.xpath('./text()').extract()[0]
            elif var_label == 'Nom':
                if len(x.xpath('./span/text()').extract())>0:
                    authors_item["last_name"] = x.xpath('./span/text()').extract()[0]
            elif var_label == 'Prénom':
                if len(x.xpath('./span/text()').extract())>0:
                    authors_item["first_name"] = x.xpath('./span/text()').extract()[0]
            elif var_label == 'Pseudo':
                if len(x.xpath('./text()').extract())>0:
                    authors_item["nickname"] = x.xpath('./text()').extract()[0]
            elif var_label == 'Pays':
                if len(x.xpath('./span/text()').extract())>0:
                    unaccented_string = unidecode.unidecode(x.xpath('./span/text()').extract()[0])
                    var_country = unaccented_string.lower()
                    authors_item["country"] = var_country
            elif var_label == 'Site':
                authors_item['web_page'] = x.xpath('./a/@href').extract()[0]
            elif var_label =='Naissance':
                if len(x.xpath('./text()').extract())>0:
                    authors_item["birth_date"] = datetime.strptime(re.findall('\d+\/\d+\/\d+', x.xpath('./text()').extract()[0])[0], "%d/%m/%Y")
            elif var_label =='Décès':
                if len(x.xpath('./text()').extract())>0:
                    authors_item["death_date"] = datetime.strptime(re.findall('\d+\/\d+\/\d+', x.xpath('./text()').extract()[0])[0], "%d/%m/%Y")

        var_full_name = ""
        for x in ["first_name", "last_name", "nickname"]:
            if authors_item.get(x):
                if x=="nickname": var_full_name += '"{0}"'.format(authors_item[x])
                else: var_full_name += authors_item[x] + " "
        if var_full_name:
            authors_item["full_name"] = var_full_name.rstrip()
        authors_item["url"] = response.url
        var_image = response.xpath('//div[@class="auteur-image"]//img/@src').extract()[0] #double slash in case //div/a/img
        if not var_image == "https://www.bdgest.com/skin/nophoto.png":
            authors_item["image"] = var_image 
        if len(response.xpath('//table[@id="tab-biblio-0"]'))>0: #check for authors without series
            for table in response.xpath('//table[@id="tab-biblio-0"]'):
                var_series_type = table.xpath('./thead/tr/th/text()').extract()[0]

                for x in table.xpath('./tbody//a/@href'):
                    var_url = x.extract()
                    var_url = re.sub('.html$', '__10000.html', var_url) #show all comics of a series

                    yield scrapy.Request(var_url, callback=self.parse_series, meta={'var_series_type': var_series_type,
                                                                                    'var_author_id': authors_item['_id']})


        yield authors_item

    def parse_series(self, response):

        """
        Parses the series page. Retrieves: bdgest id, genre, publishing status (parution), volume (tome),
        origin, language.

        On the series page, there are actually many informations about the comics.
        The data related to comics: bdgest id, person in charge of scenario, illustration, coloring, 
        translation, date of legal deposit, editor, collection, format, ISBN, number of pages.

        Args:
            response: a response which is a series page

        Yield:
            series_item: once all comics have been parsed
        """

        series_item = SeriesItem()
        var_series_type = response.meta['var_series_type']
        var_author_id = response.meta['var_author_id']
        var_series_id = response.xpath('//input[@id="IdSerie"]/@value').extract()[0]
        var_series_name = response.xpath('//h1/a/text()').extract()[0]
        series_item["url"] = response.url
        series_item["name"] = var_series_name
        series_item["_id"] = var_series_id
        series_item["author_id"] = var_author_id
        series_item["description"] = response.xpath('//meta[@name="description"]/@content').extract()[0]

        for x in response.xpath('//ul[@class="serie-info"]/li'):
            var_label = x.xpath('./label/text()').extract()[0].split(" ")[0]
            if var_label == 'Genre':
                if len(x.xpath('./span/text()').extract())>0:
                    series_item["genre"] = x.xpath('./span/text()').extract()[0]
            elif var_label == 'Parution':
                if len(x.xpath('./span/text()').extract())>0:
                    var_status = x.xpath('./span/text()').extract()[0]
                    if "cours" in var_status.lower(): series_item["status"] = 1
                    else: series_item["status"] = 0
            elif "tome" in var_label.lower():
                if len(x.xpath('./text()').extract())>0:
                    series_item["volume_nb"] = x.xpath('./text()').extract()[0]
            elif "origine" in var_label.lower():
                if len(x.xpath('./text()').extract())>0:
                    series_item["origin"] = x.xpath('./text()').extract()[0]
            elif "langue" in var_label.lower():
                if len(x.xpath('./text()').extract())>0:
                    series_item["lang"] = x.xpath('./text()').extract()[0]

        for x in response.xpath('//div[@class="album-main"]'):
            var_url = x.xpath('./h3/a/@href').extract()[0]
            var_title = x.xpath('.//span[@itemprop="name"]/text()').extract()[1].strip()
            var_title = re.sub('\s+', ' ', var_title)
            if var_title.startswith('.'): var_title = var_title[2:]

            comics_item = ComicsItem()
            comics_item["title"] = var_title
            comics_item["url"] = var_url
            comics_item["author_id"] = var_author_id
            comics_item["series_id"] = var_series_id

            for y in x.xpath('.//ul[@class="infos"]/li'):

                if len(y.xpath('./label/text()').extract())>0:
                    var_label = y.xpath('./label/text()').extract()[0].split(" ")[0]
                    var_label = var_label.lower()
                    if "identifiant" in var_label:
                        if len(y.xpath('./text()').extract())>0: comics_item["_id"] = y.xpath('./text()').extract()[0]
                    elif "scénario" in var_label:
                        if len(y.xpath('.//span/text()').extract())>0: comics_item["scenario"] = y.xpath('.//span/text()').extract()[0]
                    elif "dessin" in var_label:
                        if len(y.xpath('.//span/text()').extract())>0: comics_item["illustration"] = y.xpath('.//span/text()').extract()[0]
                    elif "couleur" in var_label:
                        if len(y.xpath('.//span/text()').extract())>0: comics_item["coloring"] = y.xpath('.//span/text()').extract()[0]
                    elif "traduction" in var_label:
                        if len(y.xpath('./span/text()').extract())>0: comics_item["translation"] = y.xpath('./span/text()').extract()[0]
                    elif "dépot" in var_label:
                        if len(y.xpath('./text()').extract())>0: 
                            # Even if the list is not empty, the actual legal deposit date can be an empty string.
                            # This additional condition prevents a spider error from occurring.
                            if y.xpath('./text()').extract()[1].strip():
                                comics_item["legal_deposit"] = datetime.strptime(y.xpath('./text()').extract()[1].strip(), "%m/%Y")
                    elif "editeur" in var_label:
                        if len(y.xpath('./text()').extract())>0: comics_item["editor"] = y.xpath('./text()').extract()[0]
                        elif len(y.xpath('./span/text()').extract())>0: comics_item["editor"] = y.xpath('./span/text()').extract()[0]                       
                    elif "collection" in var_label:
                        if len(y.xpath('./a/text()').extract())>0: comics_item["collection"] = y.xpath('./a/text()').extract()[0]
                    elif "format" in var_label:
                        if len(y.xpath('./text()').extract())>0: comics_item["format"] = y.xpath('./text()').extract()[0]
                    elif "isbn" in var_label:
                        if len(y.xpath('./span/text()').extract())>0: comics_item["isbn"] = y.xpath('./span/text()').extract()[0]
                    elif "planche" in var_label:
                        if len(y.xpath('./span/text()').extract())>0: comics_item["pages"] = y.xpath('./span/text()').extract()[0]  

            yield scrapy.Request(var_url, callback=self.parse_comics, meta={"comics_item": comics_item})

        yield series_item


    def parse_comics(self, response):
        """
        Parses the comics page. Most of the scraping was previously done within the parse_series function.
        This parse function adds the description and image fields to the comic item.

        Args:
            response: a comic response page

        Yield:
            comics_item
        """
        comics_item = response.meta['comics_item']
        comics_item["description"] = response.xpath('//meta[@name="description"]/@content').extract()[0]
        comics_item["image"] = response.xpath('//img[@itemprop="image"]/@src').extract()[0]

        yield comics_item

