from scraper.utils import read_excel_file
from scraper.items import ScraperItem
from scraper import PROJECT_ROOT_DIR

from urllib.parse import urlencode

import scrapy
import json
import re


class HeadersMiddleware:
    def process_request(self, request, spider):
        headers = {
            "authority": "www.amazon.ae",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "cache-control": "max-age=0",
            "device-memory": "8",
            "downlink": "7.65",
            "dpr": "2",
            "ect": "4g",
            "rtt": "150",
            "sec-ch-device-memory": "8",
            "sec-ch-dpr": "2",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-viewport-width": "865",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "viewport-width": "865",
        }

        request.headers.update(headers)


class AmazonSpider(scrapy.Spider):
    name = "amazon.ae"
    allowed_domains = ["amazon.ae"]
    custom_settings = {
        "CONCURRENT_REQUESTS": 1,
        "DOWNLOAD_DELAY": 10,
        "DOWNLOADER_MIDDLEWARES": {
            "scraper.middlewares.UserAgentMiddleware": 1000,
            HeadersMiddleware: 1100,
        },
    }

    BASE_URL = "https://www.amazon.ae/stores/page/9978F790-7843-44F0-834F-92C086AC4A19/search"
    BASE_URL_PARAMS = {
        "ref_": "ast_bln",
        "terms": "",
    }

    def start_requests(self):
        params = self.BASE_URL_PARAMS.copy()
        df = read_excel_file(filepath=f"{PROJECT_ROOT_DIR}/products.xlsx")
        for item in df[["Product Number", "Product Name EN"]].values.tolist():
            product_number, product_name = item
            params["terms"] = product_number
            print(f"{self.BASE_URL}?{urlencode(params)}",'--=========================')
            yield scrapy.Request(
                url=f"{self.BASE_URL}?{urlencode(params)}",
                callback=self.parse,
                meta={
                    "_product_number": product_number,
                    "_product_name": product_name,
                },
            )

    def parse(self, response):
        products = re.findall(r"products\":(\[.+\"version\":\"2.0\"}]),", response.text)
        products = products[0] if products else "[]"
        products = json.loads(products)

        product = products[0] if products else {}
        buy_options = product.get("buyingOptions")
        buy_option = buy_options[0].get("price", {}) if buy_options else {}

        try:
            discount_price = buy_option.get("priceToPay", {}).get("moneyValueOrRange", {}).get("value", {}).get("amount", 0)
            price = buy_option.get("basisPrice", {}).get("moneyValueOrRange", {}).get("value", {}).get("amount", 0)

            yield ScraperItem(
                product_number=response.meta["_product_number"],
                product_name=response.meta["_product_name"],
                discount_price=discount_price,
                price=price,
            )

        except AttributeError:
            pass
