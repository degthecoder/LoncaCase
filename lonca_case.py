import xml.etree.ElementTree as ET
import re
from datetime import datetime, timezone
from pymongo import MongoClient
import html

class ProductParser:
    def __init__(self, xml_file_path):
        self.xml_file_path = xml_file_path

    def description_info(self, description):
        if not description:
            return None

        description = html.unescape(description)
        
        key_map = {
            "Ürün Bilgisi": "product_info",
            "Kumaş Bilgisi": "fabric",
            "Ürün Ölçüleri": "product_measurements",
            "Model Ölçüleri": "model_measurements",
        }

        matches = re.findall(r"<li><strong>(.*?):\s*</strong>(.*?)(?:</li>|$)", description)

        description_dict = {}
        for key, value in matches:
            key = key.strip() 
            value = value.strip()  
            # print(key, ": " ,value)
            
            # To map the key even if the name is wrong due to Model Olculeri sometimes being recorded with anomalies
            new_key = next(
                (abbr for tr_name, abbr in key_map.items() if key.startswith(tr_name)),
                key
            )
            
            description_dict[new_key] = value
        
        
        # To get the size manually
        get_strong = re.findall(r"<strong>(.*?)</strong>", description)
        size = get_strong[-1] if get_strong else None
        if size != list(key_map.keys())[-1]:
            description_dict["sample_size"] = size
        
        # print("PM: ", description_dict.get("product_measurements"), "\n")
        
        return description_dict


    def parse_product(self, product):
        product_id = product.attrib.get("ProductId")
        name = product.attrib.get("Name").capitalize()
        
        images = [img.attrib.get("Path") for img in product.find("Images")]
        details = {
            detail.attrib.get("Name"): detail.attrib.get("Value")
            for detail in product.find("ProductDetails")
        }

        price = float(details.get("Price", "0").replace(",", "."))
        discounted_price = float(details.get("DiscountedPrice", "0").replace(",", "."))

        is_discounted = discounted_price < price
        
        is_active = "Active" if int(details.get("Quantity", "0")) > 0 else "Inactive"

        description_data = self.description_info(product.find("Description").text)

        stock_code = product_id.lower().split("-")[0] + "-" + details.get("Color", "").lower()
        # print(stock_code, description_data.get("product_measurements"))

        return {
            "stock_code": stock_code,
            "color": [details.get("Color", "").capitalize()],
            "discounted_price": discounted_price,
            "images": images,
            "is_discounted": is_discounted,
            "name": name,
            "price": price,
            "price_unit": "USD", 
            "product_type": details.get("ProductType", "").capitalize(),
            "quantity": int(details.get("Quantity", "0")),
            "sample_size": description_data.get("sample_size"),  
            "series": details.get("Series", ""),
            "status": is_active,
            "fabric": description_data.get("fabric"),  
            "model_measurements": description_data.get("model_measurements"),  
            "product_measurements": description_data.get("product_measurements"), 
            "createdAt": datetime.now(timezone.utc).isoformat(timespec='milliseconds'),
            "updatedAt": datetime.now(timezone.utc).isoformat(timespec='milliseconds'),
        }

    def parse_products(self):
        try: 
            tree = ET.parse(self.xml_file_path)
            root = tree.getroot()

            products = []
            for product in root.findall("Product"):
                products.append(self.parse_product(product))
            return products
        except ET.ParseError as e: 
            print("Error parsing the xml file", e)


class DatabaseConnection:
    def __init__(self, db_name, collection_name, mongo_uri="mongodb://localhost:27017/"):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.unique_stock_code()
        
    def unique_stock_code(self):
        self.collection.create_index("stock_code", unique=True)
        
    def create_entry(self, products):
        try:
            self.collection.insert_many(products, ordered=False)
            print("Inserted " , len(products) , " products.")
        except Exception as e:
            print("Bulk write error.")


if __name__ == "__main__":
    parser = ProductParser("lonca-sample.xml")
    products = parser.parse_products()

    db_conn = DatabaseConnection(db_name="lonca", collection_name="products")
    db_conn.create_entry(products)
    