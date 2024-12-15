from table_executor.table_executor_utils import TableExecutorUtil
from data_writer.write_data_from_csv_to_db import WriteDataToDbFromCSV
from vectorizer_utils.vectorizer_utils import CategoryVectorizer
from data_writer.main_category_writer import MainCategoryWriter
from data_writer.product_features_writer import ProductFeatureWriter
import os
import subprocess

tables_folder_path = "table_executor/all_tables"
requirements_file = "requirements.txt"
data_folder_path = "data"

def main():
    """
    if os.path.exists(requirements_file):
        print(f"Installing packages from {requirements_file}")
        subprocess.check_call([os.sys.executable, "-m", "pip", "install", "-r", requirements_file])
    else:
        print(f"{requirements_file} not found, skipping package installation.")
    """

    table_util = TableExecutorUtil()
    table_util.create_tables(tables_folder_path)
    
    data_writer = WriteDataToDbFromCSV()
    data_writer.write_data(data_folder_path)

    categoryVectorizer = CategoryVectorizer()
    categoryVectorizer.vectorize_categories()

    mainCategoryWriter = MainCategoryWriter()
    mainCategoryWriter.write_main_categories()

    product_features_writer = ProductFeatureWriter()
    product_features_writer.update_product_features()

if __name__ == "__main__":
    main()
