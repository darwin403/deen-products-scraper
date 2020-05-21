# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import pyodbc
import json
import os
from urllib.parse import urlparse
from scrapy.pipelines.images import ImagesPipeline
from scrapy.http import Request


class SQLPipeline(object):
    def __init__(self, driver, server, user, password, database, table):
        self.driver = driver
        self.server = server
        self.user = user
        self.password = password
        self.database = database
        self.table = table

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            driver=crawler.settings.get('SQL_DRIVER'),
            server=crawler.settings.get('SQL_SERVER'),
            user=crawler.settings.get('SQL_USER'),
            password=crawler.settings.get('SQL_PASSWORD'),
            database=crawler.settings.get('SQL_DATABASE'),
            table=crawler.settings.get('SQL_TABLE'),
        )

    def open_spider(self, spider):
        # establish connection
        self.conn = pyodbc.connect(
            "DRIVER={{{driver}}};SERVER={server};UID={user};PWD={password}".format(driver=self.driver, server=self.server, user=self.user, password=self.password), autocommit=True)
        self.cursor = self.conn.cursor()

        # create database
        self.cursor.execute("""
            IF NOT EXISTS (SELECT name FROM master.dbo.sysdatabases WHERE name = N'{database}')
                CREATE DATABASE [{database}];
        """.format(database=self.database))

        # create table
        self.cursor.execute("""
            USE {database}
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='{database}' and xtype='U')
            CREATE TABLE {table}
                (
                _id int IDENTITY(1,1) PRIMARY KEY,
                id int,
                title nvarchar(255),
                category nvarchar(255),
                price decimal(10,2),
                link nvarchar(max),
                image_urls nvarchar(max),
                images nvarchar(max)
                );
        """.format(database=self.database, table=self.table))

    def process_item(self, product, spider):
        # insert/update product
        self.cursor.execute("""
            SET NOCOUNT ON
            USE {database}
            UPDATE {table}
            SET
                id = {id},
                title = '{title}',
                category = '{category}',
                price = {price},
                link = '{link}',
                image_urls = N'{image_urls}',
                images = N'{images}'
            WHERE id = {id}
            IF @@ROWCOUNT = 0
                INSERT INTO {table}
                ("id","title", "category", "price", "link", "image_urls", "images")
                VALUES
                ({id} , '{title}', '{category}', {price}, '{link}', N'{image_urls}', N'{images}');
        """.format(database=self.database, table=self.table, id=product["id"], title=product["title"], category=product["category"], price=product["price"], link=product["link"], image_urls=json.dumps(product["image_urls"]), images=json.dumps(product["images"])))

        return product


class MyImagesPipeline(ImagesPipeline):
    # pass item id down into request
    def get_media_requests(self, item, info):
        return [Request(x, meta={'item': item}) for x in item.get(self.images_urls_field, [])]

    # custom downloaded image filename
    def file_path(self, request, response=None, info=None):
        item = request.meta['item']
        if item['id']:
            image_path = urlparse(request.url).path.split('/')[-1]
            image_ext = os.path.splitext(image_path)[1]
            image_location = str(item['id']) + image_ext
            return image_location
        else:
            image_guid = request.url.split('/')[-1]
            return 'full/%s' % (image_guid)
