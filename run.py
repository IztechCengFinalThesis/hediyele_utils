from table_executor.table_executor_utils import TableExecutorUtil
from data_writer.data_writer_utils import DataWriter
from vectorizer_utils.vectorizer_utils import CategoryVectorizer
from data_writer.main_category_writer import MainCategoryWriter
from similarity_tests.similarity_checker import SimilarityChecker
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

    #table_util = TableExecutorUtil()
    #table_util.create_tables(tables_folder_path)
    
    #data_writer = DataWriter()
    #data_writer.write_data(data_folder_path)

    #categoryVectorizer = CategoryVectorizer()
    #categoryVectorizer.vectorize_categories()

    #mainCategoryWriter = MainCategoryWriter()
    #mainCategoryWriter.write_main_categories()

    checker = SimilarityChecker()
    result = checker.recommend_gift("Arkadaşım osmana bir hediye almak istiyorum telefonu çok kötü ama telefon istemiyor teknoloji meraklısı aynı zamanda da kötü kokan birisi ona belki bir parfüm hediye alabilirim ama parfüm hakaret gibi olur aslında sporlar ilgilense de fena olmaz ne yapabilirim bilmiyorum bana hediye için bir tavsiye verir misin?")
    print(result)


if __name__ == "__main__":
    main()
