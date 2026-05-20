"""
bito_client.py  —  Bito.uz API Client
======================================
A reusable client for pulling data from the Bito 2.0 Integration API
and saving it as CSV files that Power BI can read.

BASE URL:  https://api.bito.uz/integration-api/integration/api/v2/
AUTH:      api-key header  (get yours from Bito platform → Integrations)

PRIVACY:   All data is saved locally. Nothing is sent to any cloud.
           Sensitive personal fields are excluded by default.
"""

import os
import csv
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ── Configuration ──────────────────────────────────────────────────────────
API_KEY      = os.getenv("BITO_API_KEY")            # your Bito API key
BASE_URL     = os.getenv("BITO_BASE_URL", "https://api.bito.uz/integration-api/integration/api/v2")
OUTPUT_DIR   = os.getenv("OUTPUT_DIR", "data")      # folder where CSVs are saved

os.makedirs(OUTPUT_DIR, exist_ok=True)

log = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════
# CORE HTTP HELPER
# ══════════════════════════════════════════════════════════════════════════

def _headers() -> dict:
    if not API_KEY:
        raise ValueError("BITO_API_KEY is not set. Add it to your .env file.")
    return {"api-key": API_KEY, "Content-Type": "application/json"}


def _get(endpoint: str, params: dict = None) -> dict:
    """Simple GET request."""
    url = f"{BASE_URL}/{endpoint.lstrip('/')}"
    r = requests.get(url, headers=_headers(), params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def _post_paging(endpoint: str, page: int = 1, limit: int = 50, extra: dict = None) -> dict:
    """
    POST request for paginated endpoints (get-paging pattern).
    Bito uses POST with a body for pagination instead of query params.
    """
    url = f"{BASE_URL}/{endpoint.lstrip('/')}"
    body = {"page": page, "limit": limit}
    if extra:
        body.update(extra)
    r = requests.post(url, headers=_headers(), json=body, timeout=15)
    r.raise_for_status()
    return r.json()


def _fetch_all_pages(endpoint: str, extra: dict = None) -> list[dict]:
    """
    Automatically loops through all pages of a paginated endpoint
    and returns a flat list of all records.
    """
    all_items = []
    page = 1
    while True:
        data = _post_paging(endpoint, page=page, extra=extra)
        items = data.get("data", {}).get("data", [])   # Bito wraps results in data.data
        if not items:
            break
        all_items.extend(items)
        log.info(f"  {endpoint} — page {page}: {len(items)} records")
        total   = data.get("data", {}).get("total", 0)
        fetched = page * 50
        if fetched >= total:
            break
        page += 1
    return all_items


def _save_csv(records: list[dict], filename: str) -> str:
    """Saves a list of dicts to a CSV file in OUTPUT_DIR."""
    if not records:
        log.warning(f"No records to save for {filename}")
        return ""
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)
    log.info(f"Saved {len(records)} rows → {path}")
    return path


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ══════════════════════════════════════════════════════════════════════════
# 1.  SALES / TRADES  →  trades.csv
#     Endpoint: POST /trade/get-paging
#     Use for: revenue charts, daily sales, sales by cashier
# ══════════════════════════════════════════════════════════════════════════

def fetch_sales(date_from: str = None, date_to: str = None) -> str:
    """
    Pull all sales (trades) from Bito.
    Optionally filter by date range: date_from / date_to  (format: YYYY-MM-DD)

    PRIVACY: personal customer phone numbers are excluded.
    """
    extra = {}
    if date_from:
        extra["date_from"] = date_from
    if date_to:
        extra["date_to"] = date_to

    raw = _fetch_all_pages("/trade/get-paging", extra=extra)

    cleaned = []
    for t in raw:
        cleaned.append({
            "trade_id":       t.get("_id", ""),
            "date":           (t.get("created_at") or "")[:10],
            "total_amount":   t.get("total_amount", 0),
            "paid_amount":    t.get("paid_amount", 0),
            "discount":       t.get("discount", 0),
            "status":         t.get("state", ""),
            "cashier_id":     t.get("created_by", ""),       # ID only, not personal info
            "warehouse_id":   t.get("warehouse_id", ""),
            "customer_id":    t.get("customer_id", ""),      # ID only
            "payment_type":   t.get("payment_type", ""),
            "items_count":    len(t.get("items", [])),
            "synced_at":      _now(),
        })

    return _save_csv(cleaned, "trades.csv")


# ══════════════════════════════════════════════════════════════════════════
# 2.  PRODUCTS  →  products.csv
#     Endpoint: POST /product/get-paging
#     Use for: product catalog, top selling items, price lists
# ══════════════════════════════════════════════════════════════════════════

def fetch_products() -> str:
    """Pull all products (catalog) from Bito."""
    raw = _fetch_all_pages("/product/get-paging")

    cleaned = []
    for p in raw:
        cleaned.append({
            "product_id":   p.get("_id", ""),
            "name":         p.get("name", ""),
            "sku":          p.get("sku", ""),
            "barcode":      p.get("barcode", ""),
            "category_id":  p.get("category_id", ""),
            "measure_id":   p.get("measure_id", ""),
            "is_active":    p.get("is_active", True),
            "is_compound":  p.get("is_compound", False),
            "synced_at":    _now(),
        })

    return _save_csv(cleaned, "products.csv")


# ══════════════════════════════════════════════════════════════════════════
# 3.  STOCK / INVENTORY  →  stock.csv
#     Endpoint: POST /product-stock/get-paging
#     Use for: low stock alerts, warehouse inventory levels
# ══════════════════════════════════════════════════════════════════════════

def fetch_stock() -> str:
    """
    Pull current stock levels from Bito.
    This shows how many units of each product are in each warehouse.
    """
    raw = _fetch_all_pages("/product-stock/get-paging")

    cleaned = []
    for s in raw:
        cleaned.append({
            "product_id":    s.get("product_id", ""),
            "product_name":  s.get("product", {}).get("name", ""),
            "warehouse_id":  s.get("warehouse_id", ""),
            "quantity":      s.get("amount", 0),
            "reserved":      s.get("reserved", 0),
            "available":     s.get("available", 0),
            "synced_at":     _now(),
        })

    return _save_csv(cleaned, "stock.csv")


# ══════════════════════════════════════════════════════════════════════════
# 4.  CUSTOMERS  →  customers.csv
#     Endpoint: POST /customer/get-paging
#     Use for: customer count, top customers by spend, customer categories
#
#     PRIVACY NOTE: We exclude phone numbers and personal details.
#     Only business-relevant fields are kept.
# ══════════════════════════════════════════════════════════════════════════

def fetch_customers() -> str:
    """
    Pull customer list from Bito.
    Personal data (phone, address) is intentionally excluded.
    """
    raw = _fetch_all_pages("/customer/get-paging")

    cleaned = []
    for c in raw:
        cleaned.append({
            "customer_id":       c.get("_id", ""),
            "name":              c.get("name", ""),           # business name or first name
            "category_id":       c.get("category_id", ""),
            "balance":           c.get("balance", 0),
            "cashback_balance":  c.get("cashback_balance", 0),
            "state":             c.get("state", "active"),
            "created_date":      (c.get("created_at") or "")[:10],
            "synced_at":         _now(),
            # EXCLUDED: phone_number, address (personal data)
        })

    return _save_csv(cleaned, "customers.csv")


# ══════════════════════════════════════════════════════════════════════════
# 5.  SALE ORDERS  →  sale_orders.csv
#     Endpoint: POST /sale-order/get-paging
#     Use for: order pipeline, pending vs fulfilled orders
# ══════════════════════════════════════════════════════════════════════════

def fetch_sale_orders() -> str:
    """Pull sale orders (pre-sale orders, not completed trades)."""
    raw = _fetch_all_pages("/sale-order/get-paging")

    cleaned = []
    for o in raw:
        cleaned.append({
            "order_id":      o.get("_id", ""),
            "date":          (o.get("created_at") or "")[:10],
            "customer_id":   o.get("customer_id", ""),
            "total_amount":  o.get("total_amount", 0),
            "state":         o.get("state", ""),
            "warehouse_id":  o.get("warehouse_id", ""),
            "created_by":    o.get("created_by", ""),
            "synced_at":     _now(),
        })

    return _save_csv(cleaned, "sale_orders.csv")


# ══════════════════════════════════════════════════════════════════════════
# 6.  PURCHASES (incoming stock)  →  purchases.csv
#     Endpoint: POST /purchase/get-paging
#     Use for: procurement tracking, supplier spend
# ══════════════════════════════════════════════════════════════════════════

def fetch_purchases() -> str:
    """Pull purchase orders (stock coming in from suppliers)."""
    raw = _fetch_all_pages("/purchase/get-paging")

    cleaned = []
    for p in raw:
        cleaned.append({
            "purchase_id":   p.get("_id", ""),
            "date":          (p.get("created_at") or "")[:10],
            "supplier_id":   p.get("supplier_id", ""),
            "total_amount":  p.get("total_amount", 0),
            "state":         p.get("state", ""),
            "warehouse_id":  p.get("warehouse_id", ""),
            "synced_at":     _now(),
        })

    return _save_csv(cleaned, "purchases.csv")


# ══════════════════════════════════════════════════════════════════════════
# 7.  REPORT: SALES BY PRODUCT  →  report_sales_by_item.csv
#     Endpoint: POST /sales/by-item
#     Use for: best-selling products, revenue by category
# ══════════════════════════════════════════════════════════════════════════

def fetch_report_sales_by_item(date_from: str = None, date_to: str = None) -> str:
    """
    Pull the Bito built-in report: sales grouped by product.
    This is the most useful report for a Power BI sales dashboard.
    """
    url  = f"{BASE_URL}/sales/by-item"
    body = {}
    if date_from:
        body["date_from"] = date_from
    if date_to:
        body["date_to"] = date_to

    r = requests.post(url, headers=_headers(), json=body, timeout=20)
    r.raise_for_status()
    raw = r.json().get("data", [])

    cleaned = []
    for item in raw:
        cleaned.append({
            "product_id":      item.get("product_id", ""),
            "product_name":    item.get("product_name", ""),
            "category":        item.get("category_name", ""),
            "quantity_sold":   item.get("quantity", 0),
            "total_revenue":   item.get("total_amount", 0),
            "avg_price":       item.get("avg_price", 0),
            "synced_at":       _now(),
        })

    return _save_csv(cleaned, "report_sales_by_item.csv")


# ══════════════════════════════════════════════════════════════════════════
# 8.  WAREHOUSES  →  warehouses.csv
#     Endpoint: POST /warehouse/get-all
#     Use for: lookup table for warehouse names in Power BI
# ══════════════════════════════════════════════════════════════════════════

def fetch_warehouses() -> str:
    """Pull all warehouse definitions (used as a lookup table in Power BI)."""
    url = f"{BASE_URL}/warehouse/get-all"
    r   = requests.post(url, headers=_headers(), json={}, timeout=15)
    r.raise_for_status()
    raw = r.json().get("data", [])

    cleaned = [{"warehouse_id": w.get("_id"), "name": w.get("name")} for w in raw]
    return _save_csv(cleaned, "warehouses.csv")
