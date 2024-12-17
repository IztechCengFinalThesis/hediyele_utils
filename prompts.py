import json
import openai
from typing import Dict, List
import constants

class Prompts:
    @staticmethod
    def get_scoring_prompt(product_info: dict, feature: str) -> str:
        return (
            f"Product Name: {product_info['name']}\n"
            f"Category: {product_info['category']}\n"
            f"Description: {product_info['description']}\n\n"
            f"On a scale of 0-10, score how relevant this product is for {feature}. "
            "Return just the score as a number."
        )
    
    @staticmethod
    def get_score_function_schema(field: str) -> dict:
        return {
            "type": "object",
            "properties": {
                "score": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 10,
                    "description": f"Score from 0-10 for how relevant this product is for {field}"
                }
            },
            "required": ["score"]
        }

    @staticmethod
    def get_categorization_function_schema(main_categories: List[str]) -> dict:
        return {
            "type": "object",
            "properties": {
                "categorizations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "category_name": {"type": "string"},
                            "main_category": {"type": "string", "enum": main_categories}
                        },
                        "required": ["category_name", "main_category"]
                    }
                }
            },
            "required": ["categorizations"]
        }

    @staticmethod
    def get_categorization_prompt(categories: List[str]) -> str:
        return f"Categorize these products into main categories: {', '.join(categories)}"

    @staticmethod
    def get_feature_score(client: openai.OpenAI, product_info: Dict, feature: str) -> float:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": constants.FEATURE_PROMPT},
                    {"role": "user", "content": Prompts.get_scoring_prompt(product_info, feature)}
                ],
                functions=[{
                    "name": "score_feature",
                    "description": f"Score the product's relevance for {feature}",
                    "parameters": Prompts.get_score_function_schema(feature)
                }],
                function_call={"name": "score_feature"},
                temperature=0.3
            )
            
            result = eval(response.choices[0].message.function_call.arguments)
            return float(result['score'])
            
        except Exception as e:
            print(f"Error getting feature score for {feature}: {e}")
            return 0.0

    @staticmethod
    def categorize_with_openai(client: openai.OpenAI, categories: List[str], main_categories: List[str]) -> Dict[str, str]:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": constants.CATEGORY_PROMPT},
                    {"role": "user", "content": Prompts.get_categorization_prompt(categories)},
                ],
                functions=[{
                    "name": "categorize_products",
                    "description": "Categorize products into main categories",
                    "parameters": Prompts.get_categorization_function_schema(main_categories)
                }],
                function_call={"name": "categorize_products"},
                temperature=0.2
            )
            
            result = json.loads(response.choices[0].message.function_call.arguments)
            return {item["category_name"]: item["main_category"] for item in result["categorizations"]}
                
        except Exception as e:
            print(f"Error categorizing with OpenAI: {e}")
            return {}