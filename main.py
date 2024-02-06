import json
import requests
from database.sqlite_client import SQLiteClient
from bs4 import BeautifulSoup

HUMBLE_URL = "https://www.humblebundle.com"

def insert_bundle(bundle, db_client):
    """
    Insert a bundle into the database
    """
    bundle_exists = db_client.bundle_exists(bundle["machine_name"])
    if not bundle_exists:
        db_client.insert_bundle(bundle)

def insert_bundle_item(bundle_item, db_client):
    """
    Insert a bundle item into the database
    """
    bundle_item_exists = db_client.bundle_item_exists(bundle_item["machine_name"], bundle_item["human_name"], bundle_item["bundle_name"])
    if not bundle_item_exists:
        db_client.insert_bundle_item(bundle_item)

def get_bundle_price(tier_pricing_data):
    """
    Get the price of a bundle
    """
    max_price = tier_pricing_data[list(tier_pricing_data.keys())[0]]['price|money']['amount']

    for tier in tier_pricing_data.values():
        if tier['price|money']['amount'] > max_price:
            max_price = tier['price|money']['amount']

    return max_price
    

def fetch_bundle_items(bundle_url, db_client):
    """
    Scrape the items from a bundle
    """
    page = requests.get(bundle_url)
    soup = BeautifulSoup(page.content, "lxml")
    select_match = soup.select_one("#webpack-bundle-page-data")

    if select_match:
        result_element = select_match.get_text()
        result = json.loads(result_element)

        bundle_data = result["bundleData"]

        msrp_price = bundle_data["basic_data"]["msrp|money"]["amount"]
        bundle_price = get_bundle_price(bundle_data["tier_pricing_data"])

        db_client.update_bundle_price(bundle_data["machine_name"], bundle_price, msrp_price)
        
        product_data = bundle_data["tier_item_data"]

        for product in product_data.values():
            product_msrp = product["msrp_price|money"]["amount"] if "msrp_price|money" in product else 0

            product_details = {
                "machine_name": product["machine_name"],
                "human_name": product["human_name"],
                "description_text": product["description_text"],
                "bundle_name": bundle_data["machine_name"],
                "msrp_price": product_msrp,
            }

            try:
                insert_bundle_item(product_details, db_client)
            except Exception as e:
                db_client.delete_bundle_items(bundle_data["machine_name"])
                db_client.delete_bundle(bundle_data["machine_name"])
                raise e

def fetch_bundles(bundle_type, db_client):
    """
    Scrape the bundles from the Humble Bundle website
    """
    url = HUMBLE_URL + "/" + bundle_type
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "lxml")
    select_match = soup.select_one("#landingPage-json-data")

    if select_match:
        result_element = select_match.get_text()
        result = json.loads(result_element)

        bundle_mosaic = result["data"][bundle_type]["mosaic"]
        products = bundle_mosaic[0]["products"]

        for bundle in products:
            bundle_url = HUMBLE_URL + bundle["product_url"]
            bundle_details = {
                "machine_name": bundle["machine_name"],
                "tile_name": bundle["tile_name"],
                "detailed_marketing_blurb": bundle["detailed_marketing_blurb"],
                "tile_image": bundle["tile_image"],
                "tile_logo": bundle["tile_logo"],
                "tile_stamp": bundle["tile_stamp"],
                "start_date": bundle["start_date|datetime"],
                "end_date": bundle["end_date|datetime"],
                "product_url": bundle_url
            }

            try:
                insert_bundle(bundle_details, db_client)
                fetch_bundle_items(bundle_url, db_client)

            except Exception as e:
                db_client.delete_bundle(bundle["machine_name"])
                db_client.delete_bundle_items(bundle["machine_name"])
                raise e
            
def main():
    """
    Main function
    """
    db_client = SQLiteClient("database/data.db")
    db_client.migrate_up()
    fetch_bundles("games", db_client)
    fetch_bundles("software", db_client)
    fetch_bundles("books", db_client)
    db_client.close()

if __name__ == "__main__":
    print("Running scraper")
    main()
    print("Finished running scraper")
    exit(0)
