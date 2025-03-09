import json
import openai
from pydantic import BaseModel
from typing import Dict, List
import constants

class Prompts:   
    @staticmethod
    def generate_scoring_prompt(product_info, features) -> str:
        prompt = (
            f"Product Name: {product_info['name']}\n"
            f"Category: {product_info['category']}\n"
            f"Description: {product_info['description']}\n\n"
            "You are preparing the database for the gift recommendation app \n"
            "Based on the product details provided above, evaluate how well this product suitable for the gift receiver for the given features.\n"
            "Rate each feature on a scale from 0 to 10\n"
            "Please provide a score for each feature below, between 0 and 10. Each feature must be rated.\n\n"
            "In response do not include the product information \n"
            "The response format must be a dictionary which is every feature will be a key and the score of the feature is the value \n"
        )
        
        for key in features:
            prompt += f"- {key}\n"
        
        return prompt
    
    @staticmethod
    def get_group_score_function_schema() -> dict:
        return {
            "type": "object",
            "properties": {
                "scores": {
                    "type": "object",
                    "description": "Mapping from feature keys to scores (0-10)",
                    "additionalProperties": {
                        "type": "number",
                    }
                }
            },
            "required": ["scores"]
        }


    @staticmethod
    def score_feature_group(client, product_info, features):
        try:            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": constants.FEATURE_PROMPT},
                    {"role": "user", "content": Prompts.generate_scoring_prompt(product_info, features)}
                ],
                functions=[{
                    "name": "score_feature_group",
                    "description": "Score the product's relevance for a group of features",
                    "parameters": Prompts.get_group_score_function_schema() 
                }],
                function_call={"name": "score_feature_group"},
                temperature=0.2,
            )
            
            scores = json.loads(response.choices[0].message.function_call.arguments)
            return scores
        except Exception as e:
            print(f"Error scoring feature group: {e}")
            return {}

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
    
    @staticmethod
    def summarize_description(client: openai.OpenAI, description: str) -> str:
        try:
            prompt = (
                "Summarize the following product description in no more than 100 words: \n"
                f"{description}"
            )
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an assistant that specializes in concise text summarization."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            summary = response.choices[0].message.content.strip()
            return summary
        except Exception as e:
            print(f"Error summarizing description: {e}")
            return ""