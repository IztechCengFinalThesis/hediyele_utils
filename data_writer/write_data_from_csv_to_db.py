import os
import pandas as pd
from typing import List, Set, Dict
from db_operations.dbop_data import DatabaseOperationsData
from dotenv import load_dotenv
from prompts import Prompts
import openai

class WriteDataToDbFromCSV:
    def __init__(self, batch_size: int = 1000):
        load_dotenv()
        self.batch_size = batch_size
        self.db = DatabaseOperationsData()
        self.required_columns = {"Category", "Link", "Product Name", "Price", "Description", "Rating"}
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.prompts = Prompts()


    def write_data(self, data_folder_path: str, product_table_name: str = "product", 
                  category_table_name: str = "categories") -> None:
        try:
            self.db.connect()
            self.db.add_category_constraint(category_table_name)
            processed_files = self.db.get_processed_files()
            category_map = self.db.get_category_map(category_table_name)
            new_categories = self._find_new_categories(data_folder_path, category_map, processed_files)
            if new_categories:
                category_map = self._process_new_categories(new_categories, category_table_name)
            
            self._process_files_for_products(
                data_folder_path, 
                processed_files, 
                category_map, 
                product_table_name
            )
            
        finally:
            self.db.close()
            print("Database connection closed.")

    def _find_new_categories(self, data_folder_path: str, 
                           category_map: Dict[str, int], 
                           processed_files: Set[str]) -> Set[str]:
        new_categories: Set[str] = set()
        
        for data_file in os.listdir(data_folder_path):
            if not self._is_valid_file(data_file, processed_files):
                continue
                
            df = self._read_excel_file(os.path.join(data_folder_path, data_file))
            if df is not None:
                file_categories = set(df["Category"].unique())
                new_categories.update(file_categories - set(category_map.keys()))
                
        return new_categories

    def _process_new_categories(self, new_categories: Set[str], 
                              category_table_name: str) -> Dict[str, int]:
        for category in new_categories:
            self.db.insert_category(category, category_table_name)
        return self.db.get_category_map(category_table_name)

    def _process_files_for_products(self, data_folder_path: str, 
                                  processed_files: Set[str],
                                  category_map: Dict[str, int], 
                                  product_table_name: str) -> None:
        products_batch: List[tuple] = []
        
        for data_file in os.listdir(data_folder_path):
            if not self._is_valid_file(data_file, processed_files):
                continue
                
            df = self._read_excel_file(os.path.join(data_folder_path, data_file))
            if df is None:
                continue
            df_cleaned = self._clean_dataframe(df)
            df_cleaned["Description"] = df_cleaned["Description"].apply(self._summarize_description)
            products_batch.extend(self._create_product_tuples(df_cleaned, category_map))
            
            if len(products_batch) >= self.batch_size:
                self.db.insert_products_batch(products_batch, product_table_name)
                products_batch = []
            
            self.db.mark_file_as_processed(data_file)
        
        if products_batch:
            self.db.insert_products_batch(products_batch, product_table_name)

    def _is_valid_file(self, filename: str, processed_files: Set[str]) -> bool:
        return filename.endswith(".xlsx") and filename not in processed_files

    def _read_excel_file(self, file_path: str) -> pd.DataFrame:
        print(f"Processing file: {os.path.basename(file_path)}")
        df = pd.read_excel(file_path)
        
        if not self.required_columns.issubset(df.columns):
            print(f"Skipping {file_path}: missing required columns "
                  f"{self.required_columns - set(df.columns)}.")
            return None
            
        return df

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        df["Price"] = pd.to_numeric(
            df["Price"].astype(str).str.replace(".", "").str.replace(",", "."),
            errors="coerce"
        )
        df = df.dropna(subset=["Price"])
        
        df["Rating"] = df["Rating"].apply(lambda x: 2 if x == "Not yet evaluated" else x)
        df["Rating"] = pd.to_numeric(
            df["Rating"].astype(str).str.replace(".", "").str.replace(",", "."),
            errors="coerce"
        )
        
        return df.dropna(subset=["Rating"])

    def _create_product_tuples(self, df: pd.DataFrame, 
                             category_map: Dict[str, int]) -> List[tuple]:
        return [
            (
                category_map[row["Category"]],
                row["Link"],
                row["Product Name"],
                float(row["Price"]),
                row["Description"],
                row["Rating"]
            )
            for _, row in df.iterrows()
        ]
    
    def _summarize_description(self, description: str) -> str:
        try:
            return Prompts.summarize_description(self.openai_client, description)
        except Exception as e:
            print(f"Error summarizing description: {e}")
            return description
