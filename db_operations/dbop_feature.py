from typing import Dict, List, Tuple
from config.db_config import get_db_connection

class DatabaseOperationsFeature:
    def __init__(self):
        self.conn = None
        self.cursor = None

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

    def get_unprocessed_products(self) -> List[Tuple]:
        self.cursor.execute("""
            SELECT p.id, p.product_name, c.category_name, p.description 
            FROM product p
            JOIN categories c ON p.category_id = c.id
            LEFT JOIN product_features pf ON p.product_features_id = pf.id
            WHERE p.product_features_id IS NULL;
        """)
        return self.cursor.fetchall()

    def create_product_features(self) -> int:
        self.cursor.execute("""
            INSERT INTO product_features DEFAULT VALUES 
            RETURNING id;
        """)
        return self.cursor.fetchone()[0]

    def update_product_features(self, features_id: int, feature_updates: List[Tuple[str, float]]):
        update_query = "UPDATE product_features SET " + \
                      ", ".join([f"{field} = %s" for field, _ in feature_updates]) + \
                      " WHERE id = %s"
        
        self.cursor.execute(
            update_query,
            [score for _, score in feature_updates] + [features_id]
        )

    def link_product_features(self, product_id: int, features_id: int):
        self.cursor.execute("""
            UPDATE product 
            SET product_features_id = %s
            WHERE id = %s;
        """, (features_id, product_id))