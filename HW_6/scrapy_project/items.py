import scrapy


class Project1Item(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    salary = scrapy.Field()
    url = scrapy.Field()
