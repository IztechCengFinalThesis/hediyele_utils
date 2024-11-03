import os
import pandas as pd
from config.db_config import get_db_connection

class DataWriter:
    def write_data(self, data_folder_path, product_table_name="product", category_table_name="categories"):
        conn = get_db_connection()
        cursor = conn.cursor()

        unique_categories = set()

        for data_file in os.listdir(data_folder_path):
            if data_file.endswith(".xlsx"):
                file_path = os.path.join(data_folder_path, data_file)
                print(f"Processing file: {data_file} located at {file_path}")
                data_frame = pd.read_excel(file_path)

                required_columns = {"Category", "Link", "Product Name", "Price", "Description", "Rating"}
                if not required_columns.issubset(data_frame.columns):
                    print(f"Skipping {data_file}: missing required columns {required_columns - set(data_frame.columns)}.")
                    continue

                for row_index, row in data_frame.iterrows():
                    category_name = row["Category"]
                    unique_categories.add(category_name)

                    price_str = str(row["Price"])
                    try:
                        price = float(price_str.replace(".", "").replace(",", "."))
                    except ValueError as e:
                        print(f"Skipping row {row_index} in '{data_file}': unable to convert price '{price_str}' to float. Error: {e}")
                        continue

                    insert_query = f"""
                        INSERT INTO {product_table_name} (category, link, product_name, price, description, rating)
                        VALUES (%s, %s, %s, %s, %s, %s);
                    """
                    try:
                        cursor.execute(insert_query, (
                            row["Category"],      # category
                            row["Link"],          # link
                            row["Product Name"],  # product_name
                            price,                # price (converted)
                            row["Description"],   # description
                            row["Rating"]         # rating
                        ))
                        conn.commit()
                        print(f"Inserted row {row_index + 1} from '{data_file}' into '{product_table_name}'")
                    except Exception as e:
                        print(f"Error while inserting row {row_index + 1} from '{data_file}': {e}")
                        conn.rollback()

            print(f"Finished processing file '{data_file}'. All valid rows inserted into '{product_table_name}' table.")

        category_insert_query = f"""
            INSERT INTO {category_table_name} (category_name)
            VALUES (%s) ON CONFLICT DO NOTHING;
        """
        try:
            cursor.executemany(category_insert_query, [(category,) for category in unique_categories])
            conn.commit()
            print(f"Inserted {len(unique_categories)} unique categories into '{category_table_name}' table:")
            for category in unique_categories:
                print(f"    - {category}")
        except Exception as e:
            print(f"Error while inserting unique categories into '{category_table_name}' table: {e}")
            conn.rollback()

        cursor.close()
        conn.close()
        print("Database connection closed.")
