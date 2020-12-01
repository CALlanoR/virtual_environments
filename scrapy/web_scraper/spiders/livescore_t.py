import scrapy

class LiveScoreT(scrapy.Spider):
    name = "LiveScoreT"
    
    start_urls = [
        "https://livescore.cz/"
    ]
    
    def parse(self, response):
        # function loop through all the matched elements that contain the tournament name, 
        # and join it together using yield.
        # Finally, we’ll receive all of the tournament names that have matches today.
        for ls in response.css('#soccer_livescore .tournament'):
            yield {
                # A point to be noted is this time I used a CSS selector instead of an XPath.
                'tournament': ls.css('.nation a::text').get()
            }