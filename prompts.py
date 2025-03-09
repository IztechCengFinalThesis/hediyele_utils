import json
import openai
from typing import Dict, List
import constants

class Prompts:
    @staticmethod
    def get_group_scoring_prompt(product_info: dict, features: dict) -> str:
        prompt = (
            f"Product Name: {product_info['name']}\n"
            f"Category: {product_info['category']}\n"
            f"Description: {product_info['description']}\n\n"
            "For each of the following features, evaluate the product's relevance on a scale from 0 to 10. "
            "Return the results as structured output according to the schema. The key in your output should be 'scores', "
            "which maps each feature key to its corresponding score.\n"
        )
        for key, desc in features.items():
            prompt += f"- {key}: {desc}\n"
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
                        "minimum": 0,
                        "maximum": 10
                    }
                }
            },
            "required": ["scores"]
        }


    @staticmethod
    def score_feature_group(client: openai.OpenAI, product_info: Dict, features: Dict[str, str]) -> Dict[str, float]:
        try:
            prompt = Prompts.get_group_scoring_prompt(product_info, features)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": constants.FEATURE_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                functions=[{
                    "name": "score_feature_group",
                    "description": "Score the product's relevance for a group of features",
                }],
                function_call={"name": "score_feature_group"},
                temperature=0.2,
            )
            result = response.choices[0].message.function_call.arguments
            return result['scores']
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