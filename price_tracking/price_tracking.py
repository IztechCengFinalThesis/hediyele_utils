from datetime import datetime
import streamlit as st
from db_operations.dbop_price_tracking import DatabaseOperationsPriceTracking
from constants import WEB_SITES
from typing import Dict

class PriceTracker:
    def __init__(self):
        self.db = DatabaseOperationsPriceTracking()

    def track_prices(self) -> Dict[str, int]:
        """Track prices for all products and return statistics"""
        try:
            products = self.db.get_products_for_tracking()
            stats = {"total": len(products), "updated": 0, "unchanged": 0, "failed": 0}

            for product_id, link, current_price, site in products:
                try:
                    scraper_class = WEB_SITES.get(site)
                    if not scraper_class:
                        stats["failed"] += 1
                        continue

                    scraper = scraper_class()
                    product_details = scraper.get_product_details(link)
                    scraper.quit()

                    if not product_details or "Price" not in product_details:
                        stats["failed"] += 1
                        continue

                    new_price = float(product_details["Price"])
                    success = self.db.record_price_change(product_id, current_price, new_price)

                    if not success:
                        stats["failed"] += 1
                        continue

                    if current_price != new_price:
                        stats["updated"] += 1
                    else:
                        stats["unchanged"] += 1

                except Exception as e:
                    print(f"Error tracking price for product {product_id}: {e}")
                    stats["failed"] += 1

            return stats
            
        finally:
            self.db.close()