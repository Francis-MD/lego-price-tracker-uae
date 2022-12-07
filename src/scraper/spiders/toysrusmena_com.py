from scraper.utils import read_excel_file
from scraper.items import ScraperItem
from scraper import PROJECT_ROOT_DIR

from urllib.parse import urlencode

import scrapy
import json


class HeadersMiddleware:
    def process_request(self, request, spider):
        headers = {
            "origin": "https://www.toysrusmena.com",
            "referer": "https://www.toysrusmena.com/",
            "content-type": "application/x-www-form-urlencoded",
        }

        request.headers.update(headers)


class ToysrusmenaComSpider(scrapy.Spider):
    name = "toysrusmena.com"
    custom_settings = {
        "CONCURRENT_REQUESTS": 1,
        "DOWNLOAD_DELAY": 3,
        "DOWNLOADER_MIDDLEWARES": {
            "scraper.middlewares.UserAgentMiddleware": 1000,
            HeadersMiddleware: 1100,
        },
    }

    BASE_URL = "https://www.toysrusmena.com/en-ae/"
    API_URL = "https://kv1fle20qb-dsn.algolia.net/1/indexes/*/queries"
    ANGOLIA_AGENTS = [
        "Algolia for JavaScript (4.10.5)",
        "Browser (lite)",
        "JS Helper (3.6.0)",
        "react (17.0.2)",
        "react-instantsearch (6.12.1)",
        "autocomplete-core (1.5.0)",
    ]

    API_BODY_PARAMS = {
        "hitsPerPage": "3",
        "highlightPreTag": "<mark>",
        "highlightPostTag": "</mark>",
    }

    API_BODY = {
        "requests": [
            {
                "indexName": "mozanta_tru_product_ae",
                "query": "",
                "params": urlencode(API_BODY_PARAMS),
            },
        ]
    }

    def _get_api_access(self, response) -> dict:
        api_key = response.xpath("//script[@id='__NEXT_DATA__']").re_first(r'SEARCH_API_KEY":"([0-9a-z]+)')
        app_id = response.xpath("//script[@id='__NEXT_DATA__']").re_first(r'APPLICATION_ID":"([0-9A-Z]+)')
    
        return {
            "x-algolia-agent": "; ".join(self.ANGOLIA_AGENTS),
            "x-algolia-api-key": api_key,
            "x-algolia-application-id": app_id,
        }

    def start_requests(self):
        yield scrapy.Request(url=self.BASE_URL, callback=self.parse)

    def parse(self, response):
        access = self._get_api_access(response)
        df = read_excel_file(filepath=f"{PROJECT_ROOT_DIR}/products.xlsx")

        for item in df[["Product Number", "Product Name EN"]].values.tolist():
            product_number, product_name = item
            body = self.API_BODY.copy()
            body["requests"][0]["query"] = f"{product_name} {product_number}"

            yield scrapy.Request(
                url=f"{self.API_URL}?{urlencode(access)}",
                method="POST",
                callback=self.get_product_info,
                body=json.dumps(body),
                meta={
                    "_product_number": product_number,
                    "_product_name": product_name,
                },
            )

    def get_product_info(self, response):
        data = response.json()["results"][0]
        if data.get("nbHits", 0) == 1:
            product = data["hits"][0]
            price = product.get("pricing", {}).get("base_price")
            discount_price = product.get("pricing", {}).get("sale_price")

            yield ScraperItem(
                product_number=response.meta["_product_number"],
                product_name=response.meta["_product_name"],
                discount_price=discount_price,
                price=price,
            )
