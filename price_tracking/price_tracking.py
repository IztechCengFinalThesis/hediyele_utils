from datetime import datetime
import streamlit as st
from db_operations.dbop_price_tracking import DatabaseOperationsPriceTracking
from constants import WEB_SITES
from typing import Dict

class PriceTracker:
    def __init__(self):
        self.db = DatabaseOperationsPriceTracking()

    def track_prices(self) -> Dict[str, int]:
        try:
            products = self.db.get_products_for_tracking()
            stats = {"total": len(products), "updated": 0, "unchanged": 0, "failed": 0}

            # Show initial information and prepare placeholders for dynamic updates in Streamlit UI
            st.write(f"Total products to check: {stats['total']}")
            progress_bar = st.progress(0)
            status_placeholder = st.empty()

            for idx, (product_id, link, current_price, site) in enumerate(products, start=1):
                # Update status for the currently processed product
                status_placeholder.text(f"Processing product {idx}/{stats['total']} (ID: {product_id})")
                progress_bar.progress(int(idx / stats['total'] * 100))

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
                    
                    if new_price <= 0:
                        print(f"Skipping zero or negative price for product {product_id}")
                        stats["failed"] += 1
                        continue
                        
                    success = self.db.record_price_change(product_id, current_price, new_price)

                    if not success:
                        stats["failed"] += 1
                        continue

                    if current_price != new_price:
                        stats["updated"] += 1
                    else:
                        stats["unchanged"] += 1

                except Exception as e:
                    # Show error in Streamlit and also keep printing to console for debugging purposes
                    error_msg = f"Error tracking price for product {product_id}: {e}"
                    st.error(error_msg)
                    print(error_msg)
                    stats["failed"] += 1

            # Final update after processing all products
            status_placeholder.text("Price tracking completed.")
            progress_bar.progress(100)

            return stats
            
        finally:
            self.db.close()