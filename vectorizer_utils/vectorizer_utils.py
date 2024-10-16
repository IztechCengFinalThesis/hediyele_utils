import psycopg2
from sklearn.feature_extraction.text import TfidfVectorizer
from config.db_config import get_db_connection

class CategoryVectorizer:
    
    def __init__(self):
        self.conn = get_db_connection()
        self.cursor = self.conn.cursor()

    def vectorize_categories(self):
        self.cursor.execute("SELECT id, category_name FROM categories")
        categories = self.cursor.fetchall()

        if not categories:
            print("No categories found to vectorize.")
            return

        category_ids = [row[0] for row in categories]
        category_names = [row[1] for row in categories]

        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform(category_names).toarray()

        for idx, vector in zip(category_ids, vectors):
            vector_list = vector.tolist()  
            self.cursor.execute(
                """
                INSERT INTO categories_vectorized (category_id, vector) 
                VALUES (%s, %s)
                """,
                (idx, vector_list)
            )

        self.conn.commit()
        print("Vectorization and insertion into 'categories_vectorized' completed.")

    def close_connection(self):
        self.cursor.close()
        self.conn.close()

if __name__ == "__main__":
    vectorizer = CategoryVectorizer() 
    vectorizer.vectorize_categories() 
    vectorizer.close_connection()   
