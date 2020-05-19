# -*- coding: utf-8 -*-
import scrapy
import re


class ProductsSpider(scrapy.Spider):
    name = 'products'
    allowed_domains = ['deen.nl']
    start_urls = ['https://www.deen.nl/boodschappen']

    custom_settings = {
        "ROBOTSTXT_OBEY": False,

        # images pipeline config
        "IMAGES_STORE": 'dumps/images',

        # feed pipeline config
        "FEED_URI": 'dumps/data.jl',

        # sql pipeline config
        'SQL_DRIVER': 'ODBC Driver 17 for SQL Server',
        'SQL_SERVER': 'localhost',
        'SQL_USER': 'sa',
        'SQL_PASSWORD': 'yourStrong(!)Password',
        'SQL_DATABASE': 'deen',
        'SQL_TABLE': 'products',

        # enable pipelines
        'ITEM_PIPELINES': {
            'scrapy.pipelines.images.ImagesPipeline': 1, # enables image pipeline
            # 'scrapy_deen.pipelines.SQLPipeline': 2 # enables sql pipeline
        },

        # log config 
        "LOG_LEVEL": 'ERROR',
        "LOG_FILE": 'logs/results.log'
    }

    # get product categories links
    def parse(self, response):
        category_links = response.css(
            'a.c-categorylist__link::attr(href)').getall()
        for category_link in category_links:
            yield response.follow(category_link+'?items=10000', self.parse_products)

    # parse product items
    def parse_products(self, response):
        product_category = response.css('h1::text').get()
        products = response.css('ul.c-productgrid > li.js-productgrid-item')

        for product in products:
            product_id = product.css(
                'div[data-product-itemcode]::attr(data-product-itemcode)').get()
            product_title = product.css('h3::text').get()
            product_image = product.css('img::attr(src)').get()
            product_price = product.css('.c-price::text').get()
            product_link = product.css('a::attr(href)').get()

            # cleanse and return product
            yield {
                "category": product_category.strip() if product_category else None,
                "id": int(re.findall(r'\d+', product_id)[0]) if product_id else None,
                "title": product_title.strip() if product_title else None,
                "image": "https://www.deen.nl%s" % product_image if product_image else None,
                "price": float(product_price.strip().replace(',', '.')) if product_price else None,
                "link": "https://www.deen.nl%s" % product_link if product_link else None,
                "image_urls": ["https://www.deen.nl%s" % product_image] if product_image else []
            }
