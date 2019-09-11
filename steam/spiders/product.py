import logging
import re
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ..items import ProductItem, ProductItemLoader
from w3lib.url import canonicalize_url, url_query_cleaner

logger = logging.getLogger(__name__)

def load_product(response):
    """Load a ProductItem from the product page response."""
    loader = ProductItemLoader(item=ProductItem(), response=response)
    url = url_query_cleaner(response.url, ['snr'], remove=True)
    url = canonicalize_url(url)
    loader.add_value('url', url)
    

    found_id = re.findall('/app/(.*?)/', response.url)
    if found_id:
        id = found_id[0]
        reviews_url = f'http://steamcommunity.com/app/{id}/reviews/?browsefilter=mostrecent&p=1'
        loader.add_value('reviews_url', reviews_url)
        loader.add_value('id', id)
        
    return loader.load_item()

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
        # Circumvent age selection form.
        if '/agecheck/app' in response.url:
            logger.debug(f"Form-type age check triggered for {response.url}.")

            form = response.css('#agegate_box form')

            action = form.xpath('@action').extract_first()
            name = form.xpath('input/@name').extract_first()
            value = form.xpath('input/@value').extract_first()

            formdata = {
                name: value,
                'ageDay': '1',
                'ageMonth': '1',
                'ageYear': '1955'
            }

            yield FormRequest(
                url=action,
                method='POST',
                formdata=formdata,
                callback=self.parse_product
            )

        else:
            # I moved all parsing code into its own function for clarity.
            yield load_product(response)
    
class SelectedProductSpider(CrawlSpider):
    name = 'sel_products'

    def start_requests(self):
        urls = [
            'https://store.steampowered.com/app/374320/',
            'https://store.steampowered.com/app/427520/',
            'https://store.steampowered.com/app/22320/'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        loader = ProductItemLoader(item=ProductItem(), response=response)
        
        loader.add_css('app_name', '.apphub_AppName ::text') #Here we connect the app_name field to an actual selector with .add_css().
        loader.add_css('specs', '.game_area_details_specs a ::text')
        loader.add_css('tags', '.app_tag ::text')
        loader.add_css('n_reviews', '.user_reviews_count ::text')
        return loader.load_item()
