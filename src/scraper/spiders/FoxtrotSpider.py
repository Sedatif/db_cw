import re
from urllib.parse import urljoin

from scrapy import Selector
from scrapy.spiders import Spider, Request


class FoxtrotSpider(Spider):
    name = 'foxtrot'
    start_urls = ['https://www.foxtrot.com.ua/ru/shop/mobilnye_telefony.html']
    url = ['https://www.foxtrot.com.ua']

    def parse(self, response):
        root = Selector(response=response)

        links = root \
            .xpath('//a[@title]/@href').getall()
        for link in links:
            yield Request(urljoin(url, link), callback=self.parse_smartphone_page, dont_filter=True)

        next_page_url = root.xpath('//li[@class="listing__pagination-nav"][last()]/a/@href').get()
        yield Request(urljoin(response.url, next_page_url), callback=self.parse)

    @staticmethod
    def parse_smartphone_page(response):
        root = Selector(response)
        content = root.xpath('//div[@class="popup__content"]')
        name = content.xpath('//span[@title]/@title').get()
        cpu_frequency = content.xpath('.//*[contains(text(), "частота процессора")]/../../td[2]/a/text()').get()
        battery = content.xpath('.//*[contains(text(), "Аккумулятор")]/../../td[2]/a/text()').get()
        ram = content.xpath('.//*[contains(text(), "ОЗУ")]/../../td[2]/a/text()').get()
        memory = content.xpath('.//p[contains(text(), "Встроенная память")]/../../td[2]/a/text()').get()
        diagonal = content.xpath('.//p[contains(text(), "Диагональ дисплея")]/../../td[2]/a/text()').get()
        price = root.xpath('//div[@class="card-price"]/text()').get()

        return {
            'name': parse_name(name),
            'cpu_frequency': parse_cpu_freq(cpu_frequency),
            'battery': parse_battery(battery),
            'ram': parse_ram(ram),
            'memory': parse_memory(memory),
            'diagonal': parse_diagonal(diagonal),
            'price': parse_price(price),
            'origin_url': response.url
        }


def parse_name(name):
    return name.replace('Смартфон', '').strip()

def parse_cpu_freq(freq):
    return float(remove_non_numeric(freq).replace(',', '.'))

def parse_battery(battery):
    return int(remove_non_numeric(battery))

def parse_ram(ram):
    if not ram:
        return 0
    coef = 1024 if 'Мб' in ram else 1
    return int(remove_non_numeric(ram)) / coef

def parse_memory(memory):
    return int(remove_non_numeric(memory))

def parse_diagonal(diagonal):
    return float(remove_non_numeric(diagonal).replace(',', '.'))

def parse_price(price):
    return int(remove_non_numeric(price))

def remove_non_numeric(line):
    return re.sub('[^0-9.]', '', line)