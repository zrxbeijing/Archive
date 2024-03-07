# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ArchivScraperItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    date_publish = scrapy.Field()
    authors = scrapy.Field()
    text = scrapy.Field()
