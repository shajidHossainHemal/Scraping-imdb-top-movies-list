import scrapy
import logging
import re

def clean_up(input_string:str):
    if input_string is not None:
        return re.sub(r'\\xa0\\n', '', input_string).strip()

class TopMoviesSpider(scrapy.Spider):
    name = 'top_movies'
    allowed_domains = ['www.imdb.com']
    start_urls = ['https://www.imdb.com/?ref_=nv_home/']

    def parse(self, response):
        list_link = response.xpath(
            '//div[@class="V1pMcXJmaAj_xVf9Ebt4r"]/ul[@class="ipc-list _1BHmFYrYdlAF0gND-D42MO ipc-list--baseAlt"]/a[child::span[contains(text(), "Most Popular Movies")]]/@href').get()
        
        yield response.follow(list_link, callback=self.parse_movie_list)
    
    def parse_movie_list(self, response):
        movie_links = response.xpath('//td[@class="titleColumn"]/a/@href').getall()

        for movie_link in movie_links:
            full_link = response.urljoin(movie_link)
            yield scrapy.Request(url=full_link, callback=self.parse_movie)
        
    def parse_movie(self, response):
        yield {
            'film_title': clean_up(response.xpath('//div[@class="title_wrapper"]/h1/text()').get()),
            'year_released' : response.xpath('//span[@id="titleYear"]/a/text()').get(),
            'rating': response.xpath('//span[@itemprop="ratingValue"]/text()').get(),
            'censor_rating': clean_up(response.xpath('//div[@class="subtext"]/text()').get()),
            'film_duration': clean_up(response.xpath('//div[@class="subtext"]/time/text()').get()),
            'genre': response.xpath('//div[@class="subtext"]/a[contains(@href, "/search/title?genres=")]/text()').getall(),
        }
