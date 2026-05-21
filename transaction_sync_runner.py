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

OUTPUT_FILE = "transactions_data.csv"

def fetch_transactions():
    all_transactions = []
    page = 1
    limit = 50

    while True:
        payload = {"page": page, "limit": limit}
        response = requests.post(f"{BASE_URL}/transaction/get-paging", json=payload, headers=HEADERS)
        data = response.json()

        raw = data.get("data")
        if not raw:
            break

        if isinstance(raw, list):
            items = raw
        elif isinstance(raw, dict):
            items = raw.get("data", [])
        else:
            break

        if not items:
            break

        all_transactions.extend(items)

        if len(items) < limit:
            break

        page += 1

    return all_transactions

def fetch_organizations():
    response = requests.get(f"{BASE_URL}/organization/get-all", headers=HEADERS)
    data = response.json()

    orgs = {}
    items = data.get("data", [])
    if isinstance(items, list):
        for org in items:
            orgs[org.get("_id", "")] = org.get("name", "")
    return orgs

def save_to_csv(transactions, organizations={}):
    if not transactions:
        print("No transaction data found.")
        return

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Transaction Number",
            "Type",
            "State",
            "Amount",
            "Date",
            "Payment Method",
            "Organization"
        ])

        for t in transactions:
            writer.writerow([
                t.get("number", ""),
                t.get("type", ""),
                t.get("state", ""),
                t.get("amount", 0),
                t.get("date", "")[:10] if t.get("date") else "",
                t.get("payment_method", {}).get("name", ""),
                organizations.get(t.get("organization_id", ""), t.get("organization_id", ""))
            ])

    print(f"Saved {len(transactions)} transactions to {OUTPUT_FILE}")

if __name__ == "__main__":
    print("Fetching transactions from Bito...")
    transactions = fetch_transactions()
    organizations = fetch_organizations()
    save_to_csv(transactions, organizations)
    print("Done!")