from scraper.utils import read_excel_file
from scraper.items import ScraperItem
from scraper import PROJECT_ROOT_DIR

from urllib.parse import urlencode

import scrapy
import re


class HeadersMiddleware:
    def process_request(self, request, spider):
        headers = {
            "authority": "cmslego.saudiblocks.com",
            "accept": "application/json",
            "access-control-allow-origin": "*",
            "cache-control": "no-cache",
            "origin": "https://lego.saudiblocks.com",
            "referer": "https://lego.saudiblocks.com/",
        }

        request.headers.update(headers)


class LegoSaudiblocksComSpider(scrapy.Spider):
    name = "lego.saudiblocks.com"
    custom_settings = {
        "CONCURRENT_REQUESTS": 1,
        "DOWNLOAD_DELAY": 3,
        "DOWNLOADER_MIDDLEWARES": {
            "scraper.middlewares.UserAgentMiddleware": 1000,
            HeadersMiddleware: 1100,
        },
    }

    BASE_URL = "https://lego.saudiblocks.com"
    API_URL = "https://cmslego.saudiblocks.com/index.php/rest/V1/app/searchresult"
    API_URL_PARAMS = {"customerid": "", "storeid": "2", "q": ""}

    def _get_api_authorization(self, response):
        key = re.findall(r',p="([0-9a-z]+)"', response.text)
        return {"authorization": f"Bearer {key[0] if key else ''}"}

    def start_requests(self):
        yield scrapy.Request(url=self.BASE_URL, callback=self.parse)

    def parse(self, response):
        next_page = response.xpath("//script[@src]").re_first(r"/static/js/main\.[0-9a-z]+\.chunk\.js")
        yield scrapy.Request(
            url=f"{self.BASE_URL}/{next_page}",
            callback=self.search_product_data,
        )

    def search_product_data(self, response):
        api_authorization = self._get_api_authorization(response)
        self.logger.debug(f"{api_authorization=}")

        params = self.API_URL_PARAMS.copy()
        df = read_excel_file(filepath=f"{PROJECT_ROOT_DIR}/products.xlsx")
        for item in df[["Product Number", "Product Name EN"]].values.tolist():
            product_number, product_name = item
            params["q"] = product_number
            yield scrapy.Request(
                url=f"{self.API_URL}?{urlencode(params)}",
                callback=self.get_product_data,
                headers=api_authorization,
                meta={
                    "_product_number": product_number,
                    "_product_name": product_name,
                },
            )

    def get_product_data(self, response):
        data = response.json()["data"]
        if data.get("total_count") == 1:
            product = data.get("product_data", {}).get("1", {})
            price = product.get("price", 0)

            offers = product.get("json", {}).get("offers", {})
            discount_price = offers.get("data", {}).get("1", 0)

            yield ScraperItem(
                product_number=response.meta["_product_number"],
                product_name=response.meta["_product_name"],
                discount_price=discount_price,
                price=price,
            )
