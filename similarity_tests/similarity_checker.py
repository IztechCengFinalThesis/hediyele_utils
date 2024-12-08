import openai
from config.db_config import get_db_connection
import json
import os
from typing import List, Dict, Tuple
from dotenv import load_dotenv
import numpy as np
import tiktoken

class SimilarityChecker:
    def __init__(self):
        load_dotenv()
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.db_connection = get_db_connection()
        self.tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")
        self.MAX_TOKENS = 14000 
        
        with self.db_connection.cursor() as cursor:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            self.db_connection.commit()

    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for the given text using OpenAI's API"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []

    def find_similar_categories(self, prompt: str, limit: int = 3) -> List[str]:
        """Find the most similar categories to the given prompt"""
        prompt_embedding = self.get_embedding(prompt)
        if not prompt_embedding:
            return []
        
        with self.db_connection.cursor() as cursor:
            embedding_str = f"[{','.join(str(x) for x in prompt_embedding)}]"
            
            cursor.execute("""
                SELECT c.category_name, 
                       1 - (cv.vector <=> %s::vector) as similarity
                FROM categories_vectorized cv
                JOIN categories c ON c.id = cv.category_id
                ORDER BY similarity DESC
                LIMIT %s
            """, (embedding_str, limit))
            
            return [row[0] for row in cursor.fetchall()]

    def get_products_by_categories(self, categories: List[str]) -> List[Dict]:
        """Get products from the specified categories"""
        if not categories:
            return []
            
        with self.db_connection.cursor() as cursor:
            placeholders = ','.join(['%s'] * len(categories))
            cursor.execute(f"""
                SELECT p.* 
                FROM product p
                JOIN categories c ON p.category_id = c.id
                WHERE c.category_name IN ({placeholders})
                ORDER BY p.rating DESC
                LIMIT 50  -- Limit initial product pool
            """, categories)
            
            columns = ['id', 'category_id', 'link', 'product_name', 'price', 'description', 'rating']
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in a text string"""
        return len(self.tokenizer.encode(text))

    def filter_and_chunk_products(self, products: List[Dict], user_prompt: str) -> List[Dict]:
        """Filter and chunk products to fit within token limits"""
        # Calculate base tokens (system message, user prompt, function definition)
        base_prompt = f"User's gift requirements: {user_prompt}\n\nAvailable products:\n"
        base_tokens = self.count_tokens(base_prompt) + 500
        
        filtered_products = []
        current_tokens = base_tokens
        
        for product in sorted(products, key=lambda x: float(x['rating']) if x['rating'] else 0, reverse=True):
            # Create product text representation
            product_text = (
                f"Product ID: {product['id']}\n"
                f"Name: {product['product_name']}\n"
                f"Price: ${product['price']}\n"
                f"Description: {product['description']}\n"
                f"Rating: {product['rating']}\n"
            )
            
            product_tokens = self.count_tokens(product_text)
            
            if current_tokens + product_tokens < self.MAX_TOKENS:
                filtered_products.append(product)
                current_tokens += product_tokens
            else:
                break
                
        return filtered_products

    def select_best_product(self, prompt: str, products: List[Dict]) -> Dict:
        """Select the best product using OpenAI's API"""
        if not products:
            return None
            
        try:
            filtered_products = self.filter_and_chunk_products(products, prompt)
            
            if not filtered_products:
                raise Exception("No products fit within token limits")

            selection_prompt = {
                "type": "object",
                "properties": {
                    "selected_product": {
                        "type": "object",
                        "properties": {
                            "product_id": {"type": "integer"},
                            "reasoning": {"type": "string"}
                        },
                        "required": ["product_id", "reasoning"]
                    }
                },
                "required": ["selected_product"]
            }

            products_context = "\n".join([
                f"Product ID: {p['id']}\n"
                f"Name: {p['product_name']}\n"
                f"Price: ${p['price']}\n"
                f"Description: {p['description']}\n"
                f"Rating: {p['rating']}\n"
                for p in filtered_products
            ])

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a gift recommendation expert. Select the best product based on the user's requirements."},
                    {"role": "user", "content": f"User's gift requirements: {prompt}\n\nAvailable products:\n{products_context}"}
                ],
                functions=[{
                    "name": "select_best_product",
                    "description": "Select the best product based on user requirements",
                    "parameters": selection_prompt
                }],
                function_call={"name": "select_best_product"},
                temperature=0.2
            )

            result = json.loads(response.choices[0].message.function_call.arguments)
            selected_id = result["selected_product"]["product_id"]
            reasoning = result["selected_product"]["reasoning"]
            
            selected_product = next((p for p in filtered_products if p['id'] == selected_id), None)
            if selected_product:
                selected_product['reasoning'] = reasoning
                return selected_product
            return None

        except Exception as e:
            print(f"Error selecting best product: {e}")
            return None

    def recommend_gift(self, user_prompt: str) -> Dict:
        """Main function to process gift recommendation"""
        try:
            similar_categories = self.find_similar_categories(user_prompt)
            if not similar_categories:
                raise Exception("No similar categories found")
                
            products = self.get_products_by_categories(similar_categories)
            if not products:
                raise Exception("No products found in similar categories")
            
            best_product = self.select_best_product(user_prompt, products)
            if not best_product:
                raise Exception("Could not select best product")
            
            return {
                "similar_categories": similar_categories,
                "best_product": best_product,
                "total_products_considered": len(products)
            }
        except Exception as e:
            print(f"Error in gift recommendation process: {e}")
            return {
                "error": str(e),
                "similar_categories": [],
                "best_product": None,
                "total_products_considered": 0
            }

    def __del__(self):
        """Clean up database connection"""
        if hasattr(self, 'db_connection'):
            self.db_connection.close()