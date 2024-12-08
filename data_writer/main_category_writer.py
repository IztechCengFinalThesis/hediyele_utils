from dotenv import load_dotenv
import openai 
import os
import json
from config.db_config import get_db_connection
from typing import List, Dict

class MainCategoryWriter:
    def __init__(self):
        load_dotenv()
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.main_categories = self._load_main_categories()

    def _load_main_categories(self) -> List[str]:
        try:
            with open('main_categories.txt', 'r') as f:
                return [line.strip() for line in f.readlines() if line.strip()]
        except FileNotFoundError:
            raise FileNotFoundError("main_categories.txt file not found")

    def categorize_with_openai(self, categories: List[str]) -> Dict[str, str]:
        prompt = {
            "type": "object",
            "properties": {
                "categorizations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "category_name": {"type": "string"},
                            "main_category": {"type": "string", "enum": self.main_categories}
                        },
                        "required": ["category_name", "main_category"]
                    }
                }
            },
            "required": ["categorizations"]
        }

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that categorizes products."},
                    {"role": "user", "content": f"Categorize these products into main categories: {', '.join(categories)}"},
                ],
                functions=[{
                    "name": "categorize_products",
                    "description": "Categorize products into main categories",
                    "parameters": prompt
                }],
                function_call={"name": "categorize_products"},
                temperature=0.2
            )
            
            result = json.loads(response.choices[0].message.function_call.arguments)
            return {item["category_name"]: item["main_category"] for item in result["categorizations"]}
                
        except Exception as e:
            print(f"Error categorizing with OpenAI: {e}")
            return {}

    def write_main_categories(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            for main_category in self.main_categories:
                cursor.execute(
                    """
                    INSERT INTO main_categories (name)
                    VALUES (%s)
                    ON CONFLICT (name) DO NOTHING;
                    """,
                    (main_category,)
                )
            
            cursor.execute("SELECT id, category_name FROM categories WHERE main_category_id IS NULL;")
            categories_to_update = cursor.fetchall()
            
            if not categories_to_update:
                print("No categories found that need main category assignment.")
                return

            category_names = [cat[1] for cat in categories_to_update]
            categorized_mapping = self.categorize_with_openai(category_names)

            if not categorized_mapping:
                print("Failed to categorize categories. Exiting.")
                return

            cursor.execute("SELECT id, name FROM main_categories;")
            main_category_ids = {row[1]: row[0] for row in cursor.fetchall()}

            for category_id, category_name in categories_to_update:
                if category_name in categorized_mapping:
                    main_category_name = categorized_mapping[category_name]
                    main_category_id = main_category_ids.get(main_category_name)
                    
                    if main_category_id:
                        cursor.execute(
                            """
                            UPDATE categories
                            SET main_category_id = %s
                            WHERE id = %s;
                            """,
                            (main_category_id, category_id)
                        )
                    else:
                        print(f"Warning: Main category '{main_category_name}' not found in database")

            conn.commit()
            print("Main categories have been successfully updated in the database.")

        except Exception as e:
            conn.rollback()
            print(f"Error updating categories: {e}")
        
        finally:
            cursor.close()
            conn.close()