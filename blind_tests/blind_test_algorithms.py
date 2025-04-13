import random
from db_operations.dbop_blind_test import DatabaseOperationsBlindTest

class RecommendationService:
    def __init__(self):
        self.db_ops = DatabaseOperationsBlindTest()

    def get_blind_recommendations(self, features: dict) -> list:
        recommendations = []
        id1, name1 = self.db_ops.get_recommendation_algorithm1(features)
        recommendations.append({
            "algorithm_name": "Algorithm1",
            "product_name": name1,
            "product_id": id1
        })
        id2, name2 = self.db_ops.get_recommendation_algorithm2(features)
        recommendations.append({
            "algorithm_name": "Algorithm2",
            "product_name": name2,
            "product_id": id2
        })
        id3, name3 = self.db_ops.get_recommendation_algorithm3(features)
        recommendations.append({
            "algorithm_name": "Algorithm3",
            "product_name": name3,
            "product_id": id3
        })
        random.shuffle(recommendations)
        return recommendations
