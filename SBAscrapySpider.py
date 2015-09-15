__author__ = 'elisabethpaulson'


# THIS FILE SCRAPES CONTENT FROM FEMA'S WEBSITE USING SCRAPY. RUN IN TERMINAL AS "scrapy runspider SBAscrapySpider.py -o SBA-web-content.json"

import scrapy

class FEMASpider(scrapy.Spider):
    name = 'SBA'
    allowed_domains=["sba.gov"]
    start_urls = ['https://www.sba.gov',
                  'https://www.sba.gov/content/what-sba-offers-help-small-businesses-grow',
                  'https://www.sba.gov/loanprograms',
                  'https://www.sba.gov/category/navigation-structure/loans-grants/small-business-loans/how-prepare-your-loan-application',
                  'https://www.sba.gov/content/connect-sba-lenders',
                  'https://www.sba.gov/content/facts-about-government-grants',
                  'https://www.sba.gov/content/research-grants-small-businesses',
                  'https://www.sba.gov/content/find-grants']

    def parse(self, response):
        i=0
        for href in response.css('a::attr(href)'):
        #for href in response.css('a[href*="/"]::attr(href)'):
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_question)

    def parse_question(self, response):
        yield {
            #'title': response.css('a::attr(title)').extract()[0],
            #'text': response.css('h3::text|p::text').extract(),
            'text': response.css('p::text').extract(),
            #'description': response.css('meta[name="description"]::attr(content)').extract(),
            'description': response.css('title::text').extract(),
            'link': response.url,
        }
