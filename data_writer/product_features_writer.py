from dotenv import load_dotenv
import openai
import os
from typing import Dict
from constants import ALL_FEATURES, AGE_GROUPS, GENDERS, SPECIAL_OCCASIONS, INTERESTS
from prompts import Prompts
from db_operations.dbop_feature import DatabaseOperationsFeature

class ProductFeatureWriter:
    def __init__(self):
        load_dotenv()
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.db = DatabaseOperationsFeature()
        
    def _score_feature(self, product_info: Dict, feature: str) -> float:
        return Prompts.get_feature_score(self.client, product_info, feature)

    def update_product_features(self):
        self.db.connect()
        try:
            products = self.db.get_unprocessed_products()
            
            for product in products:
                product_id, name, category, description = product
                product_info = {
                    "name": name,
                    "category": category,
                    "description": description
                }
                
                features_id = self.db.create_product_features()
                feature_updates = []
                
                age_scores = Prompts.score_feature_group(self.client, product_info, AGE_GROUPS)
                gender_scores = Prompts.score_feature_group(self.client, product_info, GENDERS)
                special_scores = Prompts.score_feature_group(self.client, product_info, SPECIAL_OCCASIONS)
                interest_scores = Prompts.score_feature_group(self.client, product_info, INTERESTS)
                
                combined_scores = {**age_scores, **gender_scores, **special_scores, **interest_scores}
                for field, score in combined_scores.items():
                    feature_updates.append((field, score))
                
                self.db.update_product_features(features_id, feature_updates)
                self.db.link_product_features(product_id, features_id)
                self.db.commit()
                
                print(f"Successfully updated features for product: {name}")
                
        except Exception as e:
            self.db.rollback()
            print(f"Error updating product features: {e}")
            
        finally:
            self.db.close()

if __name__ == "__main__":
    scorer = ProductFeatureWriter()
    scorer.update_product_features()