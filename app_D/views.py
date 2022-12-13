from django.shortcuts import render

# Create your views here.
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


def get_product_list(product_id) -> list:
    products = _read_excel_file(
        filepath=f"{PROJECT_ROOT_DIR}/src/products.xlsx",
    ).to_dict(orient="records")

    for result_file in os.listdir(f"{PROJECT_ROOT_DIR}/src/results/"):
        domain = result_file.replace(".csv", "")

        items = _read_csv_file(
            filepath=f"{PROJECT_ROOT_DIR}/src/results/{result_file}",
        ).to_dict(orient="records")

        for i, product in enumerate(products):
            product_number = product["Product Number"]
            discount_price = _find_column_value(items, "discount_price", product_number)
            price = _find_column_value(items, "price", product_number)

            product[domain] = discount_price if discount_price != 0 else price
            products[i] = product
    final_product = []
    if product_id != None:
        for i in products:
            product_id = str(product_id).lower().strip()
            for _key in i:
                if type(i[_key]) != str:
                    i[_key] = float(i[_key])
                
            if i[product_id] == 0  or i[product_id] == 0.0:

                products.pop(products.index(i))
            else:
                print(i[product_id])
                final_product.append(i)
    else:
        for i in products:
            for _key in i:
                if type(i[_key]) != str:
                    i[_key] = float(i[_key])
            final_product.append(i)


    return final_product


def gen_html_table(products: list,product_name= 'all'):
    env = Environment(loader=FileSystemLoader(f"{PROJECT_ROOT_DIR}/src/templates/"))
    template = env.get_template("table.html")
    # print(products)
    html = template.render(products=products)
    with open("src/index.html", "w") as f:
        f.write(html)

def home(request):
    product_id = request.GET.get('web_name', None)
    print("---->",product_id)
    products = get_product_list(product_id)
    gen_html_table(products)
    return render(request, 'index.html')

def airtableview(request):
    return render(request,"airtableview.html")
