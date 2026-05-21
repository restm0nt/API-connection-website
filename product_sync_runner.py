import os
import csv
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BITO_API_KEY")
BASE_URL = "https://api.bito.uz/integration-api/integration/api/v2"

HEADERS = {
    "api-key": API_KEY,
    "Content-Type": "application/json"
}

OUTPUT_FILE = "products_data.csv"

def fetch_products():
    all_products = []
    page = 1
    limit = 50

    while True:
        payload = {
            "page": page,
            "limit": limit,
            "is_product": True
        }
        response = requests.post(f"{BASE_URL}/product/get-paging", json=payload, headers=HEADERS)
        data = response.json()

        if not data.get("data") or not data["data"].get("data"):
            break

        items = data["data"]["data"]
        all_products.extend(items)

        if len(items) < limit:
            break

        page += 1

    return all_products

def save_to_csv(products):
    if not products:
        print("No product data found.")
        return

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # === EDIT THIS: remove columns you don't need ===
        writer.writerow([
            "Product Name",
            "SKU",
            "Category",
            "Measure Unit",
            "Barcode",
            "Created Date"
        ])

        for p in products:
            writer.writerow([
                p.get("name", ""),
                p.get("sku", ""),
                p.get("category", {}).get("name", ""),
                p.get("measure", {}).get("short_name", ""),
                p.get("barcode", ""),
                p.get("created_at", "")[:10] if p.get("created_at") else ""
            ])

    print(f"Saved {len(products)} products to {OUTPUT_FILE}")

if __name__ == "__main__":
    print("Fetching products from Bito...")
    products = fetch_products()
    save_to_csv(products)
    print("Done!")