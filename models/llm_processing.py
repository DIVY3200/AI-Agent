import os
from typing import List, Dict, Any
import groq
from dotenv import load_dotenv
import json
import time
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LLMProcessor:
    def __init__(self):
        load_dotenv()
        self.groq_api_key = os.getenv('API_KEY_GROQ')
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")

        self.client = groq.Client(api_key=self.groq_api_key)
        self.model = "mixtral-8x7b-32768"

    def create_extraction_prompt(self, entity: str, search_results: List[Dict], prompt_template: str) -> str:
        base_prompt = f"""Please analyze the following search results about {entity} and extract the information according to this prompt: "{prompt_template.format(company=entity)}".

Search Results:
"""
        for result in search_results:
            base_prompt += f"\nSource: {result.get('displayed_link', 'N/A')}\n"
            base_prompt += f"Title: {result.get('title', 'N/A')}\n"
            base_prompt += f"Content: {result.get('snippet', 'N/A')}\n"

        base_prompt += """
Please extract the requested information in the following JSON format:
{
    "extracted_info": "The specific information requested",
    "confidence": "HIGH/MEDIUM/LOW based on the quality and reliability of the sources",
    "source": "URL of the most reliable source used"
}

Rules for extraction:
1. If multiple sources provide the information, use the most reliable one.
2. Set confidence as:
   - HIGH: Information from official company website or verified sources
   - MEDIUM: Information from reliable third-party sources
   - LOW: Information from unclear sources or when information is partial
3. If no reliable information is found, respond with:
   {
       "extracted_info": "Information not found",
       "confidence": "LOW",
       "source": "None"
   }
"""
        return base_prompt

    def process_search_results(self, entity: str, search_results: List[Dict], prompt_template: str) -> Dict[str, Any]:
        try:
            extraction_prompt = self.create_extraction_prompt(entity, search_results, prompt_template)

            chat_completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a precise data extraction assistant."},
                    {"role": "user", "content": extraction_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )

            response_content = chat_completion.choices[0].message.content.strip()

            # Extract JSON from response content using regex
            json_match = re.search(r'{.*}', response_content, re.DOTALL)
            if json_match:
                extracted_data = json.loads(json_match.group())
                if self.validate_result(extracted_data, prompt_template):
                    return extracted_data

            return {
                "extracted_info": "Information not found",
                "confidence": "LOW",
                "source": "None"
            }

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing LLM response for {entity}: {str(e)}")
            return {
                "extracted_info": "Error parsing LLM response",
                "confidence": "LOW",
                "source": "Error"
            }
        except Exception as e:
            logger.error(f"Error during LLM processing for {entity}: {str(e)}")
            return {
                "extracted_info": f"Error during LLM processing: {str(e)}",
                "confidence": "LOW",
                "source": "Error"
            }

    def validate_result(self, result: Dict[str, Any], prompt_template: str) -> bool:
        required_fields = ["extracted_info", "confidence", "source"]
        return all(field in result for field in required_fields) and result["confidence"] in ["HIGH", "MEDIUM",
                                                                                              "LOW"] and result[
            "extracted_info"].strip()