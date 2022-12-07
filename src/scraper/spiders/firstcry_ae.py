from scraper.utils import read_excel_file
from scraper.items import ScraperItem
from scraper import PROJECT_ROOT_DIR

from urllib.parse import urlencode

import scrapy
import json


class FirstcryAeSpider(scrapy.Spider):
    name = "firstcry.ae"
    allowed_domains = ["firstcry.ae"]
    custom_settings = {
        "CONCURRENT_REQUESTS": 1,
        "DOWNLOAD_DELAY": 2,
        "DOWNLOADER_MIDDLEWARES": {
            "scraper.middlewares.UserAgentMiddleware": 1000,
        },
    }

    URL_SEARCH = "https://www.firstcry.ae/search"

    def start_requests(self):
        df = read_excel_file(filepath=f"{PROJECT_ROOT_DIR}/products.xlsx")
        for item in df[["Product Number", "Product Name EN"]].values.tolist():
            product_number, product_name = item
            params = {
                "q": f"{product_name} {product_number}",
                "ref2": f"{product_name} {product_number}",
            }

            yield scrapy.Request(
                url=f"{self.URL_SEARCH}?{urlencode(params)}",
                callback=self.parse,
                meta={
                    "_product_number": product_number,
                    "_product_name": product_name,
                },
            )

    def parse(self, response):
        discount_price = response.css("#maindiv .lft:nth-child(1) .lft .lft .M16_42::text").get()
        price = response.css("#maindiv .lft:nth-child(1) .lft .lft .R12_75::text").get()

        yield ScraperItem(
            product_number=response.meta["_product_number"],
            product_name=response.meta["_product_name"],
            discount_price=discount_price,
            price=price,
        )
