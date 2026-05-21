import os
import csv
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BITO_API_KEY")
BASE_URL = "https://api.bito.uz/integration-api/integration/api/v2"

HEADERS = {
    "api-key": API_KEY,
    "Content-Type": "application/json"
}

OUTPUT_FILE = "sales_data.csv"

def fetch_sales():
    all_sales = []
    page = 1
    limit = 50

    while True:
        payload = {
            "page": page,
            "limit": limit
        }
        response = requests.post(f"{BASE_URL}/trade/get-paging", json=payload, headers=HEADERS)
        data = response.json()

        if not data.get("data") or not data["data"].get("data"):
            break

        items = data["data"]["data"]
        all_sales.extend(items)

        if len(items) < limit:
            break

        page += 1

    return all_sales

def save_to_csv(sales):
    if not sales:
        print("No sales data found.")
        return

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # === EDIT THIS: remove columns you don't need ===
        writer.writerow([
            "Sale Number",
            "Date",
            "Customer Name",
            "Total Amount",
            "Total Discount",
            "State",
            "Organization"
        ])

        for sale in sales:
            writer.writerow([
                sale.get("number", ""),
                sale.get("date", "")[:10] if sale.get("date") else "",
                sale.get("customer", {}).get("name", ""),
                sale.get("total_amount", 0),
                sale.get("total_discount", 0),
                sale.get("state", ""),
                sale.get("organization", {}).get("name", "")
            ])

    print(f"Saved {len(sales)} sales to {OUTPUT_FILE}")

if __name__ == "__main__":
    print("Fetching sales from Bito...")
    sales = fetch_sales()
    save_to_csv(sales)
    print("Done!")
