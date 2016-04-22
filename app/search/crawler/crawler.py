from app import app
from urlparse import urlsplit
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

extractor = LinkExtractor(allow_domains=app.config['ALLOWED_DOMAINS'])

class Crawler(CrawlSpider):
    name = 'crawler'
    
    allowed_domains = app.config['ALLOWED_DOMAINS']
    start_urls = app.config['START_URLS']

    custom_settings = {
    	'DEPTH_LIMIT': app.config['DEPTH_LIMIT']
    }

    rules = (
        Rule(extractor, callback='parse_item', follow=True),
    )

    def parse_start_url(self, response):
        outlinks = [outlink.url for outlink in extractor.extract_links(response)]

        url = response.url
        if 'redirect_urls' in response.meta:
            url = response.meta['redirect_urls'][0]

        return {
        	'url': url,
        	'html': response.body,
        	'outlinks': outlinks
    	}

    def parse_item(self, response):
        if not 'text/html' in response.headers['Content-Type']:
            return None

        if not any(domain in urlsplit(response.url).netloc for domain in app.config['ALLOWED_DOMAINS']):
            return None

        outlinks = [outlink.url for outlink in extractor.extract_links(response)]

        url = response.url
        if 'redirect_urls' in response.meta:
            url = response.meta['redirect_urls'][0]
        
        return {
        	'url': url,
        	'html': response.body,
        	'outlinks': outlinks
    	}\