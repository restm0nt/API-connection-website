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

OUTPUT_FILE = "invoices_data.csv"

def fetch_invoices():
    all_invoices = []
    page = 1
    limit = 50

    while True:
        payload = {
            "page": page,
            "limit": limit
        }
        response = requests.post(f"{BASE_URL}/invoice/get-paging", json=payload, headers=HEADERS)
        data = response.json()

        # TO:
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

        all_invoices.extend(items)

        if len(items) < limit:
            break

        page += 1

    return all_invoices

def save_to_csv(invoices):
    if not invoices:
        print("No invoice data found.")
        return

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # === EDIT THIS: remove columns you don't need ===
        writer.writerow([
            "Invoice Number",
            "Date",
            "State",
            "Amount to Pay",
            "Paid",
            "Customer Name",
            "Organization"
        ])

        for inv in invoices:
            writer.writerow([
                inv.get("number", ""),
                inv.get("date", "")[:10] if inv.get("date") else "",
                inv.get("state", ""),
                inv.get("to_be_paid", 0),
                inv.get("paid", 0),
                inv.get("customer", {}).get("name", ""),
                inv.get("organization", {}).get("name", "")
            ])

    print(f"Saved {len(invoices)} invoices to {OUTPUT_FILE}")

if __name__ == "__main__":
    print("Fetching invoices from Bito...")
    invoices = fetch_invoices()
    save_to_csv(invoices)
    print("Done!")