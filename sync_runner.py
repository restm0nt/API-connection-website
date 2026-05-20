"""
sync_runner.py  —  Bito → Power BI Sync Runner
================================================
Run this file to start syncing your Bito data to Power BI every 30 minutes.

SETUP:
  1. pip install requests python-dotenv schedule
  2. Create a .env file (copy .env.example)
  3. Add your Bito API key to .env
  4. Run:  python sync_runner.py

WHAT IT DOES:
  - Pulls sales, products, stock, customers from your Bito account
  - Saves them as CSV files in the /data folder
  - Power BI reads those CSV files for its dashboard
  - Repeats every 30 minutes automatically
"""

import logging
import schedule
import time
from bito_client import (
    fetch_sales,
    fetch_products,
    fetch_stock,
    fetch_customers,
    fetch_sale_orders,
    fetch_report_sales_by_item,
    fetch_warehouses,
)

# ── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[
        logging.FileHandler("sync.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════
# CHOOSE WHAT TO SYNC
# ══════════════════════════════════════════════════════════════════════════
# Set True/False for each data type you want to include in your dashboard.
# Students: this is where you customize what data goes to Power BI.

SYNC_CONFIG = {
    "sales":             True,   # daily trades / sales transactions
    "products":          True,   # product catalog
    "stock":             True,   # current inventory levels
    "customers":         True,   # customer list (no personal data)
    "sale_orders":       False,  # pending orders (enable if you need pipeline)
    "report_by_item":    True,   # built-in sales-by-product report
    "warehouses":        True,   # lookup table for warehouse names
}


# ══════════════════════════════════════════════════════════════════════════
# MAIN SYNC JOB
# ══════════════════════════════════════════════════════════════════════════

def run_sync():
    log.info("=" * 55)
    log.info("Starting Bito → Power BI sync...")

    results = {}

    try:
        if SYNC_CONFIG["warehouses"]:
            results["warehouses"] = fetch_warehouses()

        if SYNC_CONFIG["products"]:
            results["products"] = fetch_products()

        if SYNC_CONFIG["sales"]:
            results["sales"] = fetch_sales()

        if SYNC_CONFIG["stock"]:
            results["stock"] = fetch_stock()

        if SYNC_CONFIG["customers"]:
            results["customers"] = fetch_customers()

        if SYNC_CONFIG["sale_orders"]:
            results["sale_orders"] = fetch_sale_orders()

        if SYNC_CONFIG["report_by_item"]:
            results["report_by_item"] = fetch_report_sales_by_item()

        log.info("Sync complete ✓")
        log.info(f"Files saved: {list(results.values())}")

    except Exception as e:
        log.error(f"Sync failed: {e}", exc_info=True)


# ══════════════════════════════════════════════════════════════════════════
# SCHEDULER
# ══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    log.info("Bito → Power BI sync service started.")
    log.info("Data will sync every 30 minutes.")

    run_sync()                                  # run immediately on start

    schedule.every(30).minutes.do(run_sync)     # then every 30 min

    while True:
        schedule.run_pending()
        time.sleep(60)
