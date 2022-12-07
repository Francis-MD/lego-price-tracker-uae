# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass


@dataclass
class ScraperItem:
    product_number: str
    product_name: str
    discount_price: float
    price: float
