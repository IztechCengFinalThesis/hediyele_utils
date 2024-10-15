from table_executor import TableExecutorUtil
from data_writer import DataWriter
import os

tables_folder_path = "all_tables"

data_folder_path = "data"

def main():
    print("Tablolar oluşturuluyor...")
    table_util = TableExecutorUtil()
    table_util.create_tables(tables_folder_path)
    print("Tablolar başarıyla oluşturuldu.")

    print("Veriler tabloya yazılıyor...")
    data_writer = DataWriter()
    
    for data_file in os.listdir(data_folder_path):
        table_name = data_file.split(".")[0]
        data_writer.write_data(data_folder_path, table_name)

if __name__ == "__main__":
    main()
