from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ..items import ProductItem, ProductItemLoader


class ProductSpider(CrawlSpider):
    name = 'products'
    start_urls = ["http://store.steampowered.com/search/?sort_by=Released_DESC"]
    allowed_domains=["steampowered.com"]
    rules = [
        Rule(LinkExtractor(allow='/app/(.+)/', restrict_css='#search_result_container'),
            callback='parse_product'),
        Rule(LinkExtractor(allow='page=(\d+)', restrict_css='.search_pagination_right'))
    ]

    def parse_product(self, response):
        loader = ProductItemLoader(item=ProductItem(), response=response)
        
        loader.add_css('app_name', '.apphub_AppName ::text') #Here we connect the app_name field to an actual selector with .add_css().
        loader.add_css('specs', '.game_area_details_specs a ::text')
        loader.add_css('tags', '.app_tag ::text')
        loader.add_css('n_reviews', '.user_reviews_count ::text')
        return loader.load_item()
