from typing import List, Tuple, Dict
from config.db_config import get_db_connection
from constants import WEB_SITES

class DatabaseOperationsPriceTracking:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        self.conn = get_db_connection()
        self.cursor = self.conn.cursor()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def get_products_for_tracking(self) -> List[Tuple]:
        try:
            self.cursor.execute("""
                SELECT p.id, p.link, p.price, p.site 
                FROM product p
                WHERE NOT EXISTS (
                    SELECT 1 FROM price_changes pc 
                    WHERE pc.product_id = p.id 
                    AND pc.created_date = CURRENT_DATE
                )
                AND p.site = ANY(%s)
            """, (list(WEB_SITES.keys()),))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting products for tracking: {e}")
            return []

    def record_price_change(self, product_id: int, old_price: float, new_price: float) -> bool:
        try:
            self.cursor.execute("""
                INSERT INTO price_changes (product_id, old_price, new_price)
                VALUES (%s, %s, %s)
            """, (product_id, old_price, new_price))

            update_query = """
                UPDATE product
                SET
                    price = %s,
                    is_last_7_days_lower_price = (%s <= COALESCE((
                        SELECT MIN(pc.new_price)
                        FROM price_changes pc
                        WHERE pc.product_id = %s
                          AND pc.created_date >= CURRENT_DATE - INTERVAL '6 days'
                    ), %s)),
                    is_last_30_days_lower_price = (%s <= COALESCE((
                        SELECT MIN(pc.new_price)
                        FROM price_changes pc
                        WHERE pc.product_id = %s
                          AND pc.created_date >= CURRENT_DATE - INTERVAL '29 days'
                    ), %s))
                WHERE id = %s
            """
            params = (new_price, new_price, product_id, new_price, new_price, product_id, new_price, product_id)
            self.cursor.execute(update_query, params)
            self.commit()
            return True
        except Exception as e:
            print(f"Error recording price change for product {product_id}: {e}")
            self.rollback()
            return False

    def get_price_history(self, product_id: int) -> List[Dict]:
        try:
            self.cursor.execute("""
                SELECT created_date, old_price, new_price
                FROM price_changes
                WHERE product_id = %s
                ORDER BY created_date DESC
            """, (product_id,))
            
            return [
                {
                    'date': row[0],
                    'old_price': row[1],
                    'new_price': row[2]
                }
                for row in self.cursor.fetchall()
            ]
        except Exception as e:
            print(f"Error getting price history: {e}")
            return []

    def get_today_tracked_count(self) -> int:
        try:
            self.cursor.execute("""
                SELECT COUNT(DISTINCT product_id)
                FROM price_changes
                WHERE created_date = CURRENT_DATE
            """)
            return self.cursor.fetchone()[0]
        except Exception as e:
            print(f"Error getting today's tracked count: {e}")
            return 0

    def get_products_with_price_changes(self) -> List[Tuple]:
        try:
            self.cursor.execute("""
                SELECT p.id, p.product_name, p.site
                FROM product p
                WHERE EXISTS (
                    SELECT 1 FROM price_changes pc 
                    WHERE pc.product_id = p.id
                )
                ORDER BY p.product_name
            """)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting products with price changes: {e}")
            return []
