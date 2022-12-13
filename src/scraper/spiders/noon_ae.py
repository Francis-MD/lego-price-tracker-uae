from scraper.utils import read_excel_file
from scraper.items import ScraperItem
from scraper import PROJECT_ROOT_DIR
import pdb
from urllib.parse import urlencode

import scrapy
import json


class HeadersMiddleware:
    def process_request(self, request, spider):
        headers = {
            'authority': 'www.noon.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 OPR/92.0.0.0',
            'x-aby': '{"app_share_link.disabled":false,"back_in_stock.back_in_stock":1,"delivery_estimates_v2.show_new_estimates":1,"golazo.enabled":1,"golazo_entrypoint.enabled":1,"golazo_new_header.enabled":true,"golazo_refresh_button.enabled":true,"recommendations.recommendations_pdp_toggle":0,"show_ar_model.enabled":1,"wishlist_experiment_entrypoint.entry_point_wishlist":2,"wishlist_toggle.wishlist_toggle":true,"wishlist_toggle_v2.enabled":true}',
            'x-cms': 'v3',
            'x-content': 'desktop',
            'x-locale': 'en-ae',
            'x-mp': 'noon',
            'x-lat': '25.1998495',
            'x-lng': '55.2715985',
            'x-platform': 'web'
        }

        request.headers.update(headers)


class NoonAeScraper(scrapy.Spider):
    name = "noon.ae"
    custom_settings = {
        "CONCURRENT_REQUESTS": 1,
        "DOWNLOAD_DELAY": 1,
        "DOWNLOADER_MIDDLEWARES": {
            "scraper.middlewares.UserAgentMiddleware": 1000,
            HeadersMiddleware: 1100,
        },
    }

    BASE_URL = "https://www.noon.com/uae-en/"

    def start_requests(self):
        df = read_excel_file(filepath=f"{PROJECT_ROOT_DIR}/products.xlsx")

        for item in df[["Product Number", "Product Name EN"]].values.tolist():
            product_number, product_name = item
            headers = {
                'if-none-match': 'W/"1183-/nWsYuJDKgkb7JMXmR6zJzOM9sM"'
            }

            url = f"https://www.noon.com/_svc/catalog/api/v3/u/search/?q={'%20'.join(product_name.split())}"
            print(url)
            yield scrapy.Request(url=url, callback=self.parse, headers=headers, meta={'product_number':product_number, 'product_name':product_name})

    def parse(self, response):
        product_number = response.meta['product_number']
        product_url = ''
        data = json.loads(response.text)
        if data['hits']:
            for item in data['hits']:
                if str(product_number) in item['url']:
                    product_url = f"https://www.noon.com/_svc/catalog/api/v3/u/{item['url']}/{item['sku']}/p/?o={item['offer_code']}"
                    break
                else:
                    return
            headers = {
                'if-none-match': 'W/"4bd0-wsGTpbHjvMDXy10iNo24v4gj/iw"',
                }

            yield scrapy.Request(
                url=product_url,
                callback=self.get_product_info,
                headers=headers,
                meta={
                    "_product_number": product_number,
                    "_product_name": response.meta['product_name'],
                },
            )

    def get_product_info(self, response):
        data = response.json()["product"]
        price = data.get("variants")[0]['offers'][0]['price']
        discount_price = data.get("variants")[0]['offers'][0].get('sale_price')

        yield ScraperItem(
            product_number=response.meta["_product_number"],
            product_name=response.meta["_product_name"],
            discount_price=discount_price,
            price=price,
        )

