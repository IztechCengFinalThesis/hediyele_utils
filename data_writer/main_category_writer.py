from dotenv import load_dotenv
import openai 
import os
import json
from config.db_config import get_db_connection

class MainCategoryWriter:
    mainCategories = [
        'Fashion & Accessories',
        'Electronics & Gadgets',
        'Home & Kitchen',
        'Beauty & Personal Care',
        'Sports & Outdoors',
        'Books & Miscellaneous',
        'Toys & Games'
    ]

    load_dotenv()
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def categorize_with_openai(self, categories):
        prompt = f"""
        You are helping with categorizing product categories into the following main categories:
        {', '.join(self.mainCategories)}.
        
        Please match each category name to the most appropriate main category and return the result as a JSON object in the format:
        {{
            "category_name_1": "main_category_1",
            "category_name_2": "main_category_2",
            ...
        }}
        
        Here are the product categories to categorize:
        {', '.join(categories)}.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that categorizes products."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            
            categorized_data = response.choices[0].message.content.strip()
            
            try:
                return json.loads(categorized_data)
            except json.JSONDecodeError:
                print("Error: Invalid JSON response from OpenAI")
                return {}
                
        except Exception as e:
            print(f"Error categorizing with OpenAI: {e}")
            return {}

    def write_main_categories(self, category_table_name="categories"):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT category_name FROM {category_table_name};")
        category_names = [row[0] for row in cursor.fetchall()]

        if not category_names:
            print("No categories found in the database.")
            return

        categorized_mapping = self.categorize_with_openai(category_names)

        if not categorized_mapping:
            print("Failed to categorize categories. Exiting.")
            return

        for category_name, main_category in categorized_mapping.items():
            cursor.execute(
                f"""
                UPDATE {category_table_name}
                SET main_category = %s
                WHERE category_name = %s;
                """,
                (main_category, category_name)
            )
        
        conn.commit()
        print("Main categories have been successfully updated in the database.")

        cursor.close()
        conn.close()