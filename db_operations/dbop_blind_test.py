import json
from config.db_config import get_db_connection

class DatabaseOperationsBlindTest:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.connect()

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

    def create_blind_test_request(self, parameters: dict) -> int:
        try:
            query = """
                INSERT INTO blind_test_requests (parameters)
                VALUES (%s)
                RETURNING id
            """
            self.cursor.execute(query, (json.dumps(parameters),))
            request_id = self.cursor.fetchone()[0]
            self.commit()
            return request_id
        except Exception as e:
            print(f"Error creating blind test request: {e}")
            self.rollback()
            return -1

    def record_recommendation(self, blind_test_request_id: int, algorithm_name: str, recommended_product_id: str) -> bool:
        try:
            query = """
                INSERT INTO blind_test_recommendations (blind_test_request_id, algorithm_name, recommended_product_id)
                VALUES (%s, %s, %s)
            """
            self.cursor.execute(query, (blind_test_request_id, algorithm_name, recommended_product_id))
            self.commit()
            return True
        except Exception as e:
            print(f"Error recording recommendation: {e}")
            self.rollback()
            return False


    def record_user_selection(self, blind_test_request_id: int, user_chosen_product_name: str, user_chosen_algorithm_name: str) -> bool:
        try:
            query = """
                UPDATE blind_test_requests
                SET user_chosen_product_id = %s,
                    user_chosen_algorithm_name = %s
                WHERE id = %s
            """
            self.cursor.execute(query, (user_chosen_product_name, user_chosen_algorithm_name, blind_test_request_id))
            self.commit()
            return True
        except Exception as e:
            print(f"Error recording user selection: {e}")
            self.rollback()
            return False

    def get_recommendation_algorithm1(self, features: dict) -> dict: 
        offset = 0.1
        expression_parts = []
        for key in features.keys():
            expression_parts.append(f"(COALESCE({key}, 0) + {offset})")
        if not expression_parts:
            return {}
        multiplication_expr = " * ".join(expression_parts)
        expr = f"LOG(1 + ({multiplication_expr}))"
        query = f"""
            SELECT p.id, p.product_name, ({expr}) AS score 
            FROM product p
            JOIN product_features pf ON p.product_features_id = pf.id
            ORDER BY score DESC
            LIMIT 1
        """
        try:
            self.cursor.execute(query)
            row = self.cursor.fetchone()
            if row:
                return row[0], row[1]
            return {}
        except Exception as e:
            print("Error in get_recommendation_algorithm1_improved:", e)
            return {}


    def get_recommendation_algorithm2(self, features: dict) -> dict:
        offset = 0.1
        expression_parts = []
        for key in features.keys():
            if key in ('gender_male', 'gender_female'):
                expression_parts.append(f"(3 * (COALESCE({key}, 0) + {offset}))")
            else:
                expression_parts.append(f"(COALESCE({key}, 0) + {offset})")
        if not expression_parts:
            return {}
        multiplication_expr = " * ".join(expression_parts)
        expr = f"LOG(1 + ({multiplication_expr}))"
        query = f"""
            SELECT p.id, p.product_name, ({expr}) AS score 
            FROM product p
            JOIN product_features pf ON p.product_features_id = pf.id
            ORDER BY score DESC
            LIMIT 1
        """
        try:
            self.cursor.execute(query)
            row = self.cursor.fetchone()
            if row:
                return row[0], row[1]
            return {}
        except Exception as e:
            print("Error in get_recommendation_algorithm2_improved:", e)
            return {}


    def get_recommendation_algorithm3(self, features: dict) -> dict:
        offset = 0.1
        weights = {
            "age_0_2": 2.0,
            "age_3_5": 2.0,
            "age_6_12": 2.0,
            "age_13_18": 2.0,
            "age_19_29": 2.0,
            "age_30_45": 2.0,
            "age_45_65": 2.0,
            "age_65_plus": 2.0,
            "gender_male": 4.0,
            "gender_female": 4.0,
            "special_birthday": 1.0,
            "special_anniversary": 1.0,
            "special_valentines": 1.0,
            "special_new_year": 1.0,
            "special_house_warming": 1.0,
            "special_mothers_day": 1.0,
            "special_fathers_day": 1.0,
            "interest_sports": 1.2,
            "interest_music": 1.0,
            "interest_books": 1.0,
            "interest_technology": 1.0,
            "interest_travel": 1.0,
            "interest_art": 1.0,
            "interest_food": 1.0,
            "interest_fitness": 1.0,
            "interest_health": 1.0,
            "interest_photography": 1.0,
            "interest_fashion": 1.0,
            "interest_pets": 1.0,
            "interest_home_decor": 1.0,
            "interest_movies_tv": 1.0
        }
        expression_parts = []
        for key in features.keys():
            w = weights.get(key, 1.0)
            expression_parts.append(f"({w} * (COALESCE({key}, 0) + {offset}))")
        if not expression_parts:
            return {}
        sum_expr = " + ".join(expression_parts)
        query = f"""
            SELECT p.id, p.product_name, ({sum_expr}) AS score
            FROM product p
            JOIN product_features pf ON p.product_features_id = pf.id
            ORDER BY score DESC
            LIMIT 1
        """
        try:
            self.cursor.execute(query)
            row = self.cursor.fetchone()
            if row:
                return row[0], row[1]
            return {}
        except Exception as e:
            print("Error in get_recommendation_algorithm3_improved:", e)
            return {}

