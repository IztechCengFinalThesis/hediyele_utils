import os
from config.db_config import get_db_connection

class TableExecutorUtil:
    def create_tables(self, tables_folder_path):
        conn = get_db_connection()
        cursor = conn.cursor()

        for sql_file in os.listdir(tables_folder_path):
            if sql_file.endswith(".sql"):
                file_path = os.path.join(tables_folder_path, sql_file)
                with open(file_path, 'r') as file:
                    create_table_query = file.read()
                    try:
                        cursor.execute(create_table_query)
                        conn.commit()
                        print(f"{sql_file} executed successfully.")
                    except Exception as e:
                        print(f"{sql_file} error while executing: {e}")
                        conn.rollback()

        cursor.close()
        conn.close()
