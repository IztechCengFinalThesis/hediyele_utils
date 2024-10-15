import os
import pandas as pd
from config.db_config import get_db_connection

class DataWriter:
    def write_data(self, data_folder_path, table_name):
        conn = get_db_connection()
        cursor = conn.cursor()

        for data_file in os.listdir(data_folder_path):
            if data_file.endswith(".xlsx"):
                file_path = os.path.join(data_folder_path, data_file)
                data_frame = pd.read_excel(file_path)

                columns = ", ".join(data_frame.columns)
                placeholders = ", ".join(["%s"] * len(data_frame.columns))
                insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});"

                try:
                    for _, row in data_frame.iterrows():
                        cursor.execute(insert_query, tuple(row))
                    conn.commit()
                    print(f"{data_file} data written to {table_name} table.")
                except Exception as e:
                    print(f"Error while writing: {e}")
                    conn.rollback()

        cursor.close()
        conn.close()
