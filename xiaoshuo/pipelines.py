# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json

class XiaoshuoPipeline(object):
    def open_spider(self, spider):
        self.f = open("qidian.db", "w", encoding="utf8")

    def process_item(self, item, spider):
        json_item = json.dumps(item, ensure_ascii=False)
        self.f.write(json_item)
        self.f.write("\n")
        return item

    def close_spider(self, spider):
        self.f.close()
