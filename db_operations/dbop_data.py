from typing import List, Dict, Set, Optional
from config.db_config import get_db_connection

class DatabaseOperationsData:
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

    def add_category_constraint(self, category_table_name: str) -> bool:
        try:
            self.cursor.execute(f"""
                ALTER TABLE {category_table_name} 
                ADD CONSTRAINT category_name_unique UNIQUE (category_name);
            """)
            self.commit()
            return True
        except Exception:
            self.rollback()
            return False

    def get_processed_files(self) -> Set[str]:
        self.cursor.execute("SELECT FILE_NAME FROM ADDED_FILE_NAMES;")
        return {row[0] for row in self.cursor.fetchall()}

    def get_category_map(self, category_table_name: str) -> Dict[str, int]:
        self.cursor.execute(f"SELECT id, category_name FROM {category_table_name};")
        return {row[1]: row[0] for row in self.cursor.fetchall()}

    def insert_category(self, category: str, category_table_name: str) -> bool:
        try:
            self.cursor.execute(f"""
                INSERT INTO {category_table_name} (category_name)
                VALUES (%s)
                ON CONFLICT (category_name) DO NOTHING;
            """, (category,))
            self.commit()
            return True
        except Exception as e:
            print(f"Error inserting category {category}: {e}")
            self.rollback()
            return False

    def get_categories_by_names(self, category_names: List[str], category_table_name: str) -> Dict[str, int]:
        self.cursor.execute(
            f"SELECT id, category_name FROM {category_table_name} WHERE category_name = ANY(%s);",
            (category_names,)
        )
        return {row[1]: row[0] for row in self.cursor.fetchall()}

    def insert_products_batch(self, products_batch: List[tuple], product_table_name: str) -> bool:
        try:
            insert_query = f"""
                INSERT INTO {product_table_name} 
                (category_id, link, product_name, price, description, rating)
                VALUES (%s, %s, %s, %s, %s, %s);
            """
            self.cursor.executemany(insert_query, products_batch)
            self.commit()
            print(f"Inserted batch of {len(products_batch)} products")
            return True
        except Exception as e:
            print(f"Error inserting product batch: {e}")
            self.rollback()
            return False

    def mark_file_as_processed(self, file_name: str) -> bool:
        try:
            self.cursor.execute(
                "INSERT INTO ADDED_FILE_NAMES (FILE_NAME) VALUES (%s);",
                (file_name,)
            )
            self.commit()
            print(f"Marked file as processed: {file_name}")
            return True
        except Exception as e:
            print(f"Error marking file as processed: {e}")
            self.rollback()
            return False

    def update_product(self, product_id: int, updates: Dict[str, any], product_table_name: str) -> bool:
        try:
            set_clause = ", ".join(f"{key} = %s" for key in updates.keys())
            values = list(updates.values()) + [product_id]
            
            self.cursor.execute(f"""
                UPDATE {product_table_name}
                SET {set_clause}
                WHERE id = %s
            """, values)
            self.commit()
            return True
        except Exception as e:
            print(f"Error updating product {product_id}: {e}")
            self.rollback()
            return False

    def delete_product(self, product_id: int, product_table_name: str) -> bool:
        try:
            self.cursor.execute(f"""
                DELETE FROM {product_table_name}
                WHERE id = %s
            """, (product_id,))
            self.commit()
            return True
        except Exception as e:
            print(f"Error deleting product {product_id}: {e}")
            self.rollback()
            return False

    def get_product_by_id(self, product_id: int, product_table_name: str) -> Optional[Dict]:
        try:
            self.cursor.execute(f"""
                SELECT category_id, link, product_name, price, description, rating
                FROM {product_table_name}
                WHERE id = %s
            """, (product_id,))
            result = self.cursor.fetchone()
            if result:
                return {
                    'category_id': result[0],
                    'link': result[1],
                    'product_name': result[2],
                    'price': result[3],
                    'description': result[4],
                    'rating': result[5]
                }
            return None
        except Exception as e:
            print(f"Error fetching product {product_id}: {e}")
            return None