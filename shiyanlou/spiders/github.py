# -*- coding: utf-8 -*-
import scrapy
from shiyanlou.items import GithubItem

class GithubSpider(scrapy.Spider):
    name = 'github'
    allowed_domains = ['github.com']

    @property
    def start_urls(self):
        url_tmpl = 'https://github.com/shiyanlou?page={}&tab=repositories'
        return (url_tmpl.format(i) for i in range(1, 5))

    def parse(self, response):
        for repository in response.css('li.public'):
            item = GithubItem()
            item['name'] = repository.xpath('.//a[@itemprop="name codeRepository"]/text()').re_first("\n\s*(.*)")
            item['update_time'] = repository.xpath('.//relative-time/@datetime').extract_first() 
            
            other_url = response.urljoin(repository.xpath('.//a/@href').extract_first())

            request = scrapy.Request(other_url, callback=self.parse_other)
            request.meta['item'] = item

            yield request


    def parse_other(self, response):
        item = response.meta['item']

        for numcount in response.css('ul.numbers-summary'):

            item['commits'] = numcount.css('li.commits').xpath('.//a/span/text()').extract_first()

            item['branches'] = numcount.xpath('.//li[2]/a/span/text()').extract_first()
            item['releases'] = numcount.xpath('.//li[3]/a/span/text()').extract_first()

        yield item



