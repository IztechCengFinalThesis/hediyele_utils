from typing import List, Dict, Set, Optional
from config.db_config import get_db_connection

class DatabaseOperationsData:
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
        
    def fetch_products(self, limit=1, offset=0):
        """
        Veritabanından ürünleri belirli bir limit ve offset ile getirir
        """
        try:
            query = """
            SELECT p.id, c.category_name, m.name AS main_category_name, p.link, p.product_name, p.price, p.rating
            FROM product p
            JOIN categories c ON p.category_id = c.id
            JOIN main_categories m ON c.main_category_id = m.id
            ORDER BY p.id ASC
            LIMIT %s OFFSET %s
            """
            self.cursor.execute(query, (limit, offset))
            products = self.cursor.fetchall()

            fixed_products = []
            for product in products:
                fixed_products.append(tuple(
                    item.decode('utf-8', 'ignore') if isinstance(item, bytes) else item
                    for item in product
                ))

            return fixed_products
        except Exception as e:
            print(f"Database Error: {e}")
            return []

    def get_total_product_count(self):
        try:
            self.cursor.execute("SELECT COUNT(*) FROM product")
            total_count = self.cursor.fetchone()[0]
            return total_count
        except Exception as e:
            print(f"Database Error: {e}")
            return 0

    def add_product_to_database(self, product_name, category_id, link, price, description, rating, site) -> Optional[int]:
        product_id = None
        try:
            self.cursor.execute(
                "SELECT id FROM product WHERE link = %s",
                (link,)
            )
            existing_product = self.cursor.fetchone()
            
            if existing_product:
                print(f"Product with link '{link}' already exists in the database.")
                return None 
                
            self.cursor.execute(
                """
                INSERT INTO product (category_id, link, product_name, price, description, rating, site)
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;
                """,
                (category_id, link, product_name, price, description, rating, site)
            )
            product_id = self.cursor.fetchone()[0]
            self.conn.commit()
            return product_id 
        except Exception as e:
            print(f"An error occurred while adding the product: {e}")
            self.conn.rollback()
            return None

    def add_product_image(self, product_id: int, image_data: bytes, image_order: int = 0) -> bool:
        try:
            self.cursor.execute(
                """
                INSERT INTO product_images (product_id, image_data, image_order)
                VALUES (%s, %s, %s)
                """,
                (product_id, image_data, image_order)
            )
            self.commit()
            return True
        except Exception as e:
            print(f"Error inserting product image for product_id {product_id}: {e}")
            self.rollback()
            return False

    def add_category_if_not_exists(self, category_name):
        try:
            self.cursor.execute("SELECT id FROM categories WHERE category_name = %s", (category_name,))
            result = self.cursor.fetchone()

            if result is None:
                self.cursor.execute(
                    "INSERT INTO categories (category_name) VALUES (%s) RETURNING id",
                    (category_name,)
                )
                category_id = self.cursor.fetchone()[0]
                self.conn.commit()
            else:
                category_id = result[0]

            return category_id
        except Exception as e:
            print(f"An error occurred while checking/inserting category: {e}")
            self.conn.rollback()
            return None

    def delete_product_from_database(self, product_id):
        try:
            self.cursor.execute("SELECT product_features_id FROM product WHERE id = %s", (product_id,))
            product_features_id = self.cursor.fetchone()

            if product_features_id:
                self.cursor.execute("DELETE FROM product_features WHERE id = %s", (product_features_id,))
            self.cursor.execute("DELETE FROM product WHERE id = %s", (product_id,))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"An error occurred while deleting the product: {e}")
            self.conn.rollback()
            return False

    def last_inserted_id(self) -> int:
        try:
            self.cursor.execute("SELECT lastval()")
            return self.cursor.fetchone()[0]
        except Exception as e:
            print(f"Error getting last inserted ID: {e}")
            return None
