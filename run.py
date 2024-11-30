from table_executor.table_executor_utils import TableExecutorUtil
from data_writer.data_writer_utils import DataWriter
from vectorizer_utils.vectorizer_utils import CategoryVectorizer
import os
import subprocess

tables_folder_path = "all_tables"
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

    data_writer = DataWriter()
    data_writer.write_data(data_folder_path)

    #CategoryVectorizer().vectorize_categories()

if __name__ == "__main__":
    main()
