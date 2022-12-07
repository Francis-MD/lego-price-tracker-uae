from django.core.management.base import BaseCommand


from jinja2 import Environment, FileSystemLoader
from pathlib import Path

import pandas as pd
import os
PROJECT_ROOT_DIR = Path(__file__).parents[1]


def read_excel_file(filepath: str) -> pd.DataFrame:
    df = pd.read_excel(filepath, index_col=False)
    return df



def _read_csv_file(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath, index_col=False, sep=";")
    df.fillna(0.0, inplace=True)
    return df


def _find_column_value(items: list, column: str, product_number: str):
    return next(
        (item[column] for item in items if item["product_number"] == product_number),
        0.0,
    )

class Command(BaseCommand):

    def init(self):

        self.BASE_URL = "https://www.amazon.ae/stores/page/9978F790-7843-44F0-834F-92C086AC4A19/search"
        self.BASE_URL_PARAMS = {
            "ref_": "ast_bln",
            "terms": "",
        }

    # def handle(self,*args,**options):

    
    def start_requests(self):
        params = self.BASE_URL_PARAMS.copy()
        df = read_excel_file(filepath=f"{PROJECT_ROOT_DIR}/products.xlsx")
        for item in df[["Product Number", "Product Name EN"]].values.tolist():
            product_number, product_name = item
            params["terms"] = product_number
            yield scrapy.Request(
                url=f"{self.BASE_URL}?{urlencode(params)}",
                callback=self.parse,
                meta={
                    "_product_number": product_number,
                    "_product_name": product_name,
                },
            )
