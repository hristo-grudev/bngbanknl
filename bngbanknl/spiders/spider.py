import json

import scrapy
from scrapy import Selector

from scrapy.loader import ItemLoader

from ..items import BngbanknlItem
from itemloaders.processors import TakeFirst


class BngbanknlSpider(scrapy.Spider):
	name = 'bngbanknl'
	start_urls = ['https://www.bngbank.nl//sxa/search/results/?s={7B1D4B4D-7DD4-41F9-89D8-013D2B6F96BB}&itemid={B8B05CFC-E90F-432B-819A-EFD19407FE1C}&sig=&autoFireSearch=true&v=%7B502E34CC-A269-48E8-B356-3A54BD614CAD%7D&p=1000000&o=News%20Page%20Date%20Time%2CDescending']

	def parse(self, response):
		data = json.loads(response.text)
		for item in data['Results']:
			url = item["Url"]
			raw_data = item["Html"]
			date = Selector(text=raw_data).xpath('//span[@class="field-searchitemnewsdatetime"]//text()').get()
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date})

	def parse_post(self, response, date):
		title = response.xpath('//h1/text()').get()
		description = response.xpath('//main//div[@class="component content col-12"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=BngbanknlItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
