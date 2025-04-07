from dotenv import load_dotenv
import openai 
import os
from typing import List, Dict
from db_operations.dbop_main_category import DatabaseOperationsMainCategory
from prompts import Prompts

class MainCategoryWriter:
    def __init__(self):
        load_dotenv()
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.main_categories = self._load_main_categories()
        self.db = DatabaseOperationsMainCategory()
        self.prompts = Prompts()

    def _load_main_categories(self) -> List[str]:
        try:
            with open('main_categories.txt', 'r') as f:
                return [line.strip() for line in f.readlines() if line.strip()]
        except FileNotFoundError:
            raise FileNotFoundError("main_categories.txt file not found")

    def write_main_categories(self):
        try:
            self.db.connect()
            self.db.insert_main_categories(self.main_categories)
            categories_to_update = self.db.get_uncategorized_categories()
            
            if not categories_to_update:
                print("No categories found that need main category assignment.")
                return
            category_names = [cat[1] for cat in categories_to_update]
            categorized_mapping = Prompts.categorize_with_openai(
                client=self.client,
                categories=category_names,
                main_categories=self.main_categories
            )

            if not categorized_mapping:
                print("Failed to categorize categories. Exiting.")
                return

            self.db.process_category_updates(categorized_mapping)

        except Exception as e:
            print(f"Error in write_main_categories: {e}")
            self.db.rollback()
            raise

        finally:
            self.db.close()

    def clear_all_categories(self):
        try:
            self.db.connect()

            self.db.cursor.execute("""
                UPDATE categories SET main_category_id = NULL;
            """)

            self.db.cursor.execute("""
                DELETE FROM main_categories;
            """)

            self.db.commit()
            print("All categories and main categories have been cleared successfully.")
        except Exception as e:
            print(f"Error while clearing categories: {e}")
            self.db.rollback()
        finally:
            self.db.close()