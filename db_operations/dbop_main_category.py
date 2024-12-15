from typing import Dict, List, Tuple
from config.db_config import get_db_connection

class DatabaseOperationsMainCategory:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = get_db_connection()
        self.cursor = self.conn.cursor()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def insert_main_categories(self, main_categories: List[str]) -> None:
        try:
            for main_category in main_categories:
                self.cursor.execute(
                    """
                    INSERT INTO main_categories (name)
                    VALUES (%s)
                    ON CONFLICT (name) DO NOTHING;
                    """,
                    (main_category,)
                )
        except Exception as e:
            print(f"Error inserting main categories: {e}")
            raise

    def get_uncategorized_categories(self) -> List[Tuple[int, str]]:
        self.cursor.execute(
            """
            SELECT id, category_name 
            FROM categories 
            WHERE main_category_id IS NULL;
            """
        )
        return self.cursor.fetchall()

    def get_main_category_mapping(self) -> Dict[str, int]:
        self.cursor.execute("SELECT id, name FROM main_categories;")
        return {row[1]: row[0] for row in self.cursor.fetchall()}

    def update_category_main_category(self, category_id: int, main_category_id: int) -> None:
        self.cursor.execute(
            """
            UPDATE categories
            SET main_category_id = %s
            WHERE id = %s;
            """,
            (main_category_id, category_id)
        )

    def process_category_updates(self, categorized_mapping: Dict[str, str]) -> None:
        try:
            categories_to_update = self.get_uncategorized_categories()
            if not categories_to_update:
                print("No categories found that need main category assignment.")
                return

            main_category_ids = self.get_main_category_mapping()

            for category_id, category_name in categories_to_update:
                if category_name in categorized_mapping:
                    main_category_name = categorized_mapping[category_name]
                    main_category_id = main_category_ids.get(main_category_name)
                    
                    if main_category_id:
                        self.update_category_main_category(category_id, main_category_id)
                    else:
                        print(f"Warning: Main category '{main_category_name}' not found in database")

            self.commit()
            print("Main categories have been successfully updated in the database.")

        except Exception as e:
            self.rollback()
            print(f"Error processing category updates: {e}")
            raise