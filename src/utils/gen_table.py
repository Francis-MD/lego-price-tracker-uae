from jinja2 import Environment, FileSystemLoader
from pathlib import Path

import pandas as pd
import os

PROJECT_ROOT_DIR = Path(__file__).parents[1]


def _read_excel_file(filepath: str) -> pd.DataFrame:
    df = pd.read_excel(filepath, index_col=False)
    df.fillna(0.0, inplace=True)
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


def get_product_list() -> list:
    products = _read_excel_file(
        filepath=f"{PROJECT_ROOT_DIR}/products.xlsx",
    ).to_dict(orient="records")

    for result_file in os.listdir(f"{PROJECT_ROOT_DIR}/results/"):
        domain = result_file.replace(".csv", "")

        items = _read_csv_file(
            filepath=f"{PROJECT_ROOT_DIR}/results/{result_file}",
        ).to_dict(orient="records")

        for i, product in enumerate(products):
            product_number = product["Product Number"]
            discount_price = _find_column_value(items, "discount_price", product_number)
            price = _find_column_value(items, "price", product_number)

            product[domain] = discount_price if discount_price != 0 else price
            products[i] = product

    return products


def gen_html_table(products: list):
    env = Environment(loader=FileSystemLoader(f"{PROJECT_ROOT_DIR}/templates/"))
    template = env.get_template("table.html")
    print(products)
    html = template.render(products=products)
    with open("index.html", "w") as f:
        f.write(html)


if __name__ == "__main__":
    products = get_product_list()
    gen_html_table(products)
