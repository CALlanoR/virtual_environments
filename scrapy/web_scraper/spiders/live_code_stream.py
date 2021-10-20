import scrapy

class LiveCodeStreamSpider(scrapy.Spider):
    name = "lcs"
    
    start_urls = [
        "https://livecodestream.dev/"
    ]
    
    def parse(self, response):
        yield {
            'logo': response.xpath("/html/body/header/nav/a[1]/text()").get()
        }
