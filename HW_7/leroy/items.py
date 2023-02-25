# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst


def process_photos(value):
    if '80x' not in value:
        return value
    else:
        return None


def process_price(value):
    value = value.replace(' ', '')
    if value.isdigit():
        return int(value)
    else:
        return None


class Project2Item(scrapy.Item):
    _id = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field(input_processor=MapCompose(process_photos))
    price = scrapy.Field(input_processor=MapCompose(process_price), output_processor=TakeFirst())
    url = scrapy.Field()
