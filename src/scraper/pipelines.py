# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import requests
from airtable import Airtable


AIRTABLE_TOKEN = "key4tAin2SiTbzEII"
AIRTABLE_BASE_ID = "appQGfKDrk8F5SjW8"
TABLE_NAME = "Main Table"
endpoint= f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{TABLE_NAME}"
airtable = Airtable(AIRTABLE_BASE_ID,TABLE_NAME,AIRTABLE_TOKEN) 


class LegoScraperPipeline:
    def process_item(self, item, spider):
     	if spider.name == "amazon.ae":  
        	self.site_name = "Amazon"

      	elif spider.name == 'firstcry.ae':   
        	self.site_name = "Firstcry"
        
      	elif spider.name == 'lego.saudiblocks.com':    
        	self.site_name = "SoudiBlocks"
       
      	elif spider.name ==  "lego.yellowblocks.me":
        	self.site_name = "YellowBlocks"
        
      	elif spider.name == 'toysrusmena.com':  
        	self.site_name = "Toysrusmena"

      	elif spider.name == "noon.ae":
        	self.site_name = "Noon"
      
      	self.price_key = f"{self.site_name} Price"
      	adapter = ItemAdapter(item)
      	product_number = int(adapter['product_number'])     
      	product_name = adapter['product_name']     
      	discount_price = float(adapter['discount_price'])   
      	price = int(adapter['price'])
      

      	record = airtable.search('Product Number',product_number )
      	if record:
          id = record[0]['id']
          self.update_to_airtable(id,price)
      	else:
          self.add_to_airtable(product_name,product_number,discount_price,price)
      	return item
       

    def add_to_airtable(self,product_name,product_number,discount_price,price):
        headers = {
        "Authorization":f"Bearer {AIRTABLE_TOKEN}" ,
        "Content-Type": "application/json"
        }      
        data ={
                "records": [
                  {
                    "fields": {
                      "Product Name": product_name,
                      "Product Number": product_number,
                      "Discount Price": discount_price,
                      self.price_key: price,
                    }
                  }
                ]
              }
        r = requests.post(endpoint,json=data,headers=headers)

   def update_to_airtable(self,id,price):
        headers = {
        "Authorization":f"Bearer {AIRTABLE_TOKEN}" ,
        "Content-Type": "application/json"
        }
        data ={
                "records": [
                   
                  {
                    "id": str(id),
                    "fields": {
                      self.price_key: price,
                    }
                  }
                ]
              }
        r = requests.patch(endpoint,json=data,headers=headers)
