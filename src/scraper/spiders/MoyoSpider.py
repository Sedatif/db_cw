import re
from urllib.parse import urljoin

from scrapy import Selector
from scrapy.spiders import Spider, Request


class MoyoSpider(Spider):
    name = 'moyo'
    start_urls = [
        'https://www.moyo.ua/telecommunication/smart/?perPage=96?page=1']
    last_page_num = None

    def parse(self, response):
        items = Selector(response=response) \
            .xpath('//div[@class="product-tile_inner_wrapper"]')

        for item in items:
            yield self.parse_item(item, response.url)

        if not self.last_page_num:
            last_nav_el = Selector(response).xpath('//a[@class="new-pagination-link"][last()]/text()').get()
            self.last_page_num = int(last_nav_el)

        next_page_url, next_page_num = increase_page_number(response.url)
        if next_page_num <= self.last_page_num:
            yield Request(next_page_url,
                          callback=self.parse)

    @staticmethod
    def parse_item(item, main_url):
        specs = item.xpath('.//div[@class="specifications_content"]')

        return {
            'name': parse_name(item.xpath('.//div[@class="product-tile_title ddd"]//text()').get().replace('Смартфон', '').strip()),
            'cpu_frequency': parse_cpu_freq(specs.xpath('./div[6]/text()').get()),
            #'battery': parse_battery(specs.xpath('./div[12]/text()').get()),
            'ram': parse_ram(specs.xpath('./div[5]/text()').get()),
            'memory': parse_memory(specs.xpath('./div[4]/text()').get()),
            'diagonal': parse_diagonal(specs.xpath('./div[1]/text()').get()),
            'price': parse_price(item.xpath('.//span[@class="product-tile_price-value"]/text()').get()),
            'origin_url': urljoin(main_url, item.xpath('.//a[@class="gtm-link-product"]/@href').get())
        }

def parse_name(name):
    return name.replace('Смартфон', '').strip()

def parse_cpu_freq(freq):
    return float(freq)

def parse_battery(battery):
    return int(battery)

def parse_ram(ram):
    return int(remove_non_numeric(ram))

def parse_memory(memory):
    return int(remove_non_numeric(memory))

def parse_diagonal(diagonal):
    return int(remove_non_numeric(diagonal))

def parse_price(price):
    return int(remove_non_numeric(price))

def remove_non_numeric(line):
    return re.sub('[^0-9,]', '', line)

def increase_page_number(url):
    base, page = url.split('page=')
    new_page_number = int(page) + 1
    return f'{base}page={new_page_number}', new_page_number