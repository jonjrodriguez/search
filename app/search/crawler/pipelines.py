import time
from app import app
from app.database import store_crawl
from scrapy import signals
from scrapy.exporters import JsonLinesItemExporter

class DownloadPipeline(object):

    def __init__(self):
        self.file = None

    @classmethod
    def from_crawler(cls, crawler):
         pipeline = cls()
         crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
         crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
         return pipeline

    def spider_opened(self, spider):
        filepath = app.config['DOCS_PATH'] + '/%s_%d.json' % (spider.allowed_domains[0], time.time())
        self.file = open(filepath, 'w+b')
        self.exporter = JsonLinesItemExporter(self.file)
        self.exporter.start_exporting()
        store_crawl(filepath)

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        
        return item

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        self.file.close()