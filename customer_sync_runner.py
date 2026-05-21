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

OUTPUT_FILE = "customers_data.csv"

def fetch_customers():
    all_customers = []
    page = 1
    limit = 50

    while True:
        payload = {
            "page": page,
            "limit": limit
        }
        response = requests.post(f"{BASE_URL}/customer/get-paging", json=payload, headers=HEADERS)
        data = response.json()

        if not data.get("data") or not data["data"].get("data"):
            break

        items = data["data"]["data"]
        all_customers.extend(items)

        if len(items) < limit:
            break

        page += 1

    return all_customers

def save_to_csv(customers):
    if not customers:
        print("No customer data found.")
        return

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # === EDIT THIS: remove columns you don't need ===
        writer.writerow([
            "Customer Name",
            "Type",
            "State",
            "Total Sales",
            "Balance",
            "Created Date"
        ])

        for c in customers:
            writer.writerow([
                c.get("name", ""),
                c.get("type", ""),
                c.get("state", ""),
                c.get("total_sale", 0),
                c.get("balance", 0),
                c.get("created_at", "")[:10] if c.get("created_at") else ""
            ])

    print(f"Saved {len(customers)} customers to {OUTPUT_FILE}")

if __name__ == "__main__":
    print("Fetching customers from Bito...")
    customers = fetch_customers()
    save_to_csv(customers)
    print("Done!")