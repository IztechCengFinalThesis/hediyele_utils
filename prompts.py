import json
import openai
from pydantic import BaseModel
from typing import Dict, List
import constants

class Prompts:   
    @staticmethod
    def generate_scoring_prompt(product_info, features) -> str:
        feature_list = "\n".join([f'- "{key}"' for key in features])
        prompt = (
            "You are an AI assistant tasked with evaluating a product for a gift recommendation system.\n\n"
            "### Product Information\n"
            f"- **Product Name:** {product_info['name']}\n"
            f"- **Category:** {product_info['category']}\n"
            f"- **Description:** {product_info['description']}\n\n"
            "### Task Instructions\n"
            "Based on the product details provided above, evaluate how suitable this product is for the gift receiver based on the given features.\n"
            "You must assign a score from **0 to 10** for each feature. **0** means 'Not Relevant At All' and **10** means 'Perfectly Relevant'.\n"
            "**Every feature must be scored.**\n\n"
            "### Scoring Criteria\n"
            "Consider the relevance of the product in relation to each feature. The scores should be integers between 0 and 10.\n\n"
            "### Output Format\n"
            "Your response must be a **valid JSON object** following this exact structure:\n"
            "```\n"
            "{\n"
            '    "feature1": score1,\n'
            '    "feature2": score2,\n'
            '    "feature3": score3\n'
            "}\n"
            "```\n"
            "**Important Notes:**\n"
            "- Do **not** include any product information in your response.\n"
            "- Do **not** provide explanations, just return the JSON object.\n"
            "- Ensure every feature is included in the response with a valid score.\n\n"
            "### Features to Score\n"
            f"{feature_list}\n\n"
            "Now, return the JSON object containing the scores."
        )
        return prompt


    @staticmethod
    def score_feature_group(client: openai.OpenAI, product_info, features):
        try:            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": constants.FEATURE_PROMPT},
                    {"role": "user", "content": Prompts.generate_scoring_prompt(product_info, features)}
                ],
                temperature=0.0,
            )
            scores = json.loads(response.choices[0].message.content)
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