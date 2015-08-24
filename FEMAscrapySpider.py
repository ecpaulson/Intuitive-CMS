__author__ = 'elisabethpaulson'


# THIS FILE SCRAPES CONTENT FROM FEMA'S WEBSITE USING SCRAPY. RUN IN TERMINAL AS "scrapy crawl FEMASpider -o filename.json"

import scrapy

class FEMASpider(scrapy.Spider):
    name = 'FEMA'
    #allowed_domains=["FEMA.gov"]
    start_urls = ['http://FEMA.gov']

    def parse(self, response):
        i=0
        for href in response.css('a[href*="/"]::attr(href)'):
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_question)

    def parse_question(self, response):
        yield {
            #'title': response.css('a::attr(title)').extract()[0],
            'text': response.css('h2::text|p::text').extract(),
            'description': response.css('meta[name="description"]::attr(content)').extract(),
            'link': response.url,
        }
