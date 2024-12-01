import psycopg2
import openai
import os
from dotenv import load_dotenv
from config.db_config import get_db_connection

class CategoryVectorizer:
    load_dotenv()
    
    def __init__(self):
        self.conn = get_db_connection()
        self.cursor = self.conn.cursor()
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def get_embedding(self, text):
        """Get embedding for a single text using OpenAI's API"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding for '{text}': {e}")
            return None

    def vectorize_categories(self, batch_size=100):
        self.cursor.execute("SELECT id, category_name FROM categories")
        categories = self.cursor.fetchall()

        if not categories:
            print("No categories found to vectorize.")
            return

        for i in range(0, len(categories), batch_size):
            batch = categories[i:i + batch_size]
            
            for category_id, category_name in batch:
                vector = self.get_embedding(category_name)
                
                if vector:
                    try:
                        self.cursor.execute(
                            """
                            INSERT INTO categories_vectorized (category_id, vector) 
                            VALUES (%s, %s)
                            ON CONFLICT (category_id) 
                            DO UPDATE SET vector = EXCLUDED.vector
                            """,
                            (category_id, vector)
                        )
                        print(f"Processed category: {category_name}")
                    except Exception as e:
                        print(f"Error inserting vector for category '{category_name}': {e}")
                        self.conn.rollback()
                        continue

            self.conn.commit()
            print(f"Completed batch {i//batch_size + 1} of {(len(categories)-1)//batch_size + 1}")

        print("Vectorization and insertion into 'categories_vectorized' completed.")

    def close_connection(self):
        """Close database connections"""
        self.cursor.close()
        self.conn.close()

if __name__ == "__main__":
    vectorizer = CategoryVectorizer()
    vectorizer.vectorize_categories()
    vectorizer.close_connection()