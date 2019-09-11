# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html



import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Compose, MapCompose, TakeFirst

class StripText:
    def __init__(self, chars=' \r\t\n'):
        self.chars = chars

    def __call__(self, value):  # This makes an instance callable!
        try:
            return value.strip(self.chars)
        except:
            return value

def str_to_int(x):
    try:
        return int(str_to_float(x))
    except:  # noqa E722
        return x
    
class ProductItem(scrapy.Item):
    url = scrapy.Field()
    reviews_url = scrapy.Field()
    id = scrapy.Field()
    app_name = scrapy.Field() #A basic field that saves its data using the default_output_processor
    specs = scrapy.Field(
        output_processor=MapCompose(StripText()) #A field with a customized output processor. MapCompose is one of a few processors included with Scrapy
    )
    tags = scrapy.Field(
        output_processor=MapCompose(StripText())
    )
    n_reviews = scrapy.Field(
        output_processor=Compose(
            MapCompose(StripText(), lambda x: x.replace(',', ''),
            lambda x: x.replace('(', ''),
            lambda x: x.replace(')', ''), str_to_int)
            

        )
    )
    
    
class ProductItemLoader(ItemLoader):
    default_output_processor=TakeFirst()  #Returns the first non-null/non-empty value from the values received
