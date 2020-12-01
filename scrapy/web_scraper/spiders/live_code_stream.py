import scrapy

class LiveCodeStreamSpider(scrapy.Spider):

    # to define a unique name for your spider using a variable called name
    #  It must be unique throughout this project.
    name = "lcs"

    # we passed the website URL using the start_urls list
    start_urls = [
        "https://livecodestream.dev/"
    ]
    
    # Locate the logo inside HTML code and extract its text. 
    # In Scrapy, there are two methods to find HTML elements inside source code: CSS and XPath.
    # You can even use some external libraries like BeautifulSoup and lxml, but for this example, we’ve used XPath.
    def parse(self, response):
        yield {
            'logo': response.xpath("/html/body/header/nav/a[1]/text()").get()
        }

    # Note:
    # A quick way to determine the XPath of any HTML element is to open it inside Chrome DevTools. 
    # Now, simply right-click on the HTML code of that element, and hover the mouse cursor over “Copy”
    # inside the pop-up menu that appears. Finally, click the “Copy XPath” menu item.

    # I used /text() after the actual XPath of the element to only retrieve the text from that element 
    # instead of the full element code.