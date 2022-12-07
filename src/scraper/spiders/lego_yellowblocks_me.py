from scraper.utils import read_excel_file
from scraper.items import ScraperItem
from scraper import PROJECT_ROOT_DIR

from urllib.parse import urlencode

import scrapy


class HeadersMiddleware:
    def process_request(self, request, spider):
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://lego.yellowblocks.me/",
        }

        request.headers.update(headers)


class LegoYellowblocksMeSpider(scrapy.Spider):
    name = "lego.yellowblocks.me"
    custom_settings = {
        "CONCURRENT_REQUESTS": 1,
        "DOWNLOAD_DELAY": 3,
        "DOWNLOADER_MIDDLEWARES": {
            HeadersMiddleware: 1100,
        },
    }

    API_URL = "https://lapi.yellowblocks.me/rest/v2/lego/products/search"
    API_URL_PARAMS = {
        "fields": "keywordRedirectUrl,products(code,sellable,name,urlName,availableToPreOrder,summary,price(FULL),badges(code,name),images(DEFAULT),stock(FULL),averageRating,crossedPrice(FULL),categories(name,code,url),maxOrderQuantity),facets,pagination(DEFAULT),sorts(DEFAULT),freeTextSearch",
        "query": "",
        "pageSize": "1",
        "lang": "en",
        "curr": "AED",
    }

    def start_requests(self):
        params = self.API_URL_PARAMS.copy()
        df = read_excel_file(filepath=f"{PROJECT_ROOT_DIR}/products.xlsx")
        for item in df[["Product Number", "Product Name EN"]].values.tolist():
            product_number, product_name = item
            params["query"] = product_number
            yield scrapy.Request(
                url=f"{self.API_URL}?{urlencode(params)}",
                callback=self.parse,
                meta={
                    "_product_number": product_number,
                    "_product_name": product_name,
                },
            )

    def parse(self, response):
        data = response.json()
        if data.get("products"):
            product = data["products"][0]
            price = product.get("crossedPrice", {}).get("value", 0)
            discount_price = product.get("price", {}).get("value", 0)

            yield ScraperItem(
                product_number=response.meta["_product_number"],
                product_name=response.meta["_product_name"],
                discount_price=discount_price,
                price=price,
            )
