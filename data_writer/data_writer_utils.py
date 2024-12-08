import os
import pandas as pd
from config.db_config import get_db_connection
from typing import List, Dict, Set
from collections import defaultdict

class DataWriter:
    def __init__(self, batch_size: int = 1000):
        self.batch_size = batch_size
        
    def write_data(self, data_folder_path: str, product_table_name: str = "product", category_table_name: str = "categories") -> None:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            try:
                cursor.execute(f"""
                    ALTER TABLE {category_table_name} 
                    ADD CONSTRAINT category_name_unique UNIQUE (category_name);
                """)
                conn.commit()
            except Exception as e:
                conn.rollback()
            
            cursor.execute("SELECT FILE_NAME FROM ADDED_FILE_NAMES;")
            processed_files = {row[0] for row in cursor.fetchall()}
            
            cursor.execute(f"SELECT id, category_name FROM {category_table_name};")
            category_map = {row[1]: row[0] for row in cursor.fetchall()}
            
            new_categories: Set[str] = set()
            products_batch: List[tuple] = []
            
            for data_file in os.listdir(data_folder_path):
                if not data_file.endswith(".xlsx") or data_file in processed_files:
                    continue
                    
                file_path = os.path.join(data_folder_path, data_file)
                print(f"Processing file: {data_file}")
                
                df = pd.read_excel(file_path)
                required_columns = {"Category", "Link", "Product Name", "Price", "Description", "Rating"}
                if not required_columns.issubset(df.columns):
                    print(f"Skipping {data_file}: missing required columns {required_columns - set(df.columns)}.")
                    continue
                    
                new_categories.update(set(df["Category"].unique()) - set(category_map.keys()))
            
            if new_categories:
                for category in new_categories:
                    try:
                        cursor.execute(f"""
                            INSERT INTO {category_table_name} (category_name)
                            VALUES (%s)
                            ON CONFLICT (category_name) DO NOTHING;
                        """, (category,))
                    except Exception as e:
                        print(f"Error inserting category {category}: {e}")
                        conn.rollback()
                
                conn.commit()
                
                cursor.execute(f"SELECT id, category_name FROM {category_table_name} WHERE category_name = ANY(%s);", 
                             (list(new_categories),))
                category_map.update({row[1]: row[0] for row in cursor.fetchall()})
            
            for data_file in os.listdir(data_folder_path):
                if not data_file.endswith(".xlsx") or data_file in processed_files:
                    continue
                    
                file_path = os.path.join(data_folder_path, data_file)
                df = pd.read_excel(file_path)
                
                if not required_columns.issubset(df.columns):
                    continue
                
                df["Price"] = pd.to_numeric(
                    df["Price"].astype(str).str.replace(".", "").str.replace(",", "."),
                    errors="coerce"
                )
                
                df = df.dropna(subset=["Price"])
                
                for _, row in df.iterrows():
                    products_batch.append((
                        category_map[row["Category"]],
                        row["Link"],
                        row["Product Name"],
                        float(row["Price"]),
                        row["Description"],
                        row["Rating"]
                    ))
                    
                    if len(products_batch) >= self.batch_size:
                        self._insert_products_batch(cursor, products_batch, product_table_name)
                        products_batch = []
                        conn.commit()
                
                cursor.execute("INSERT INTO ADDED_FILE_NAMES (FILE_NAME) VALUES (%s);", (data_file,))
                conn.commit()
                print(f"Processed file: {data_file}")
            
            if products_batch:
                self._insert_products_batch(cursor, products_batch, product_table_name)
                conn.commit()
                
        finally:
            cursor.close()
            conn.close()
            print("Database connection closed.")
    
    def _insert_products_batch(self, cursor, products_batch: List[tuple], product_table_name: str) -> None:
        insert_query = f"""
            INSERT INTO {product_table_name} 
            (category_id, link, product_name, price, description, rating)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        cursor.executemany(insert_query, products_batch)
        print(f"Inserted batch of {len(products_batch)} products")