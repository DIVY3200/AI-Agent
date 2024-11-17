# search_api.py
import requests
import time
from typing import List, Dict, Optional
import pandas as pd
from config import API_KEY_SERPAPI
import logging
from ratelimit import limits, sleep_and_retry
from pathlib import Path
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CALLS_PER_MINUTE = 10
RATE_LIMIT = 60 / CALLS_PER_MINUTE


@sleep_and_retry
@limits(calls=CALLS_PER_MINUTE, period=60)
def make_serpapi_request(params: Dict) -> Dict:
    base_url = "https://serpapi.com/search"
    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"SerpAPI request failed: {str(e)}")
        raise


class SearchService:
    def __init__(self, api_key: str = API_KEY_SERPAPI):
        self.api_key = api_key
        self.cache_dir = Path('data/search_cache')
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, entity: str, query_type: str) -> Path:
        safe_name = "".join(c for c in f"{entity}_{query_type}" if c.isalnum() or c in (' ', '-', '_')).rstrip()
        return self.cache_dir / f"{safe_name}.json"

    def _load_from_cache(self, entity: str, query_type: str) -> Optional[Dict]:
        cache_path = self._get_cache_path(entity, query_type)
        if cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    cached_data = json.load(f)
                if cached_data.get('timestamp'):
                    cache_time = time.strptime(cached_data['timestamp'], "%Y-%m-%d %H:%M:%S")
                    if time.time() - time.mktime(cache_time) < 86400:
                        return cached_data
            except Exception as e:
                logger.warning(f"Cache read error for {entity}: {str(e)}")
        return None

    def _save_to_cache(self, entity: str, query_type: str, data: Dict):
        cache_path = self._get_cache_path(entity, query_type)
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Cache write error for {entity}: {str(e)}")

    def parse_query_type(self, prompt: str) -> str:
        lower_prompt = prompt.lower()
        if 'email' in lower_prompt:
            return 'email'
        elif 'address' in lower_prompt:
            return 'address'
        elif 'phone' in lower_prompt:
            return 'phone'
        elif 'website' in lower_prompt:
            return 'website'
        return 'general'

    def search_entity(self, entity: str, prompt: str) -> Dict:
        query_type = self.parse_query_type(prompt)

        cached_results = self._load_from_cache(entity, query_type)
        if cached_results:
            logger.info(f"Cache hit for {entity} - {query_type}")
            return cached_results

        query = prompt.format(company=entity)

        params = {
            "q": query,
            "api_key": self.api_key,
            "engine": "google",
            "num": 5,
            "hl": "en",
            "gl": "us",
            "safe": "active"
        }

        try:
            search_response = make_serpapi_request(params)
            organic_results = search_response.get("organic_results", [])

            structured_results = {
                "entity": entity,
                "query_type": query_type,
                "query": query,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "results": [
                    {
                        "title": result.get("title", ""),
                        "link": result.get("link", ""),
                        "snippet": result.get("snippet", ""),
                        "position": idx + 1,
                        "displayed_link": result.get("displayed_link", "")
                    }
                    for idx, result in enumerate(organic_results[:5])
                ]
            }

            self._save_to_cache(entity, query_type, structured_results)
            return structured_results

        except Exception as e:
            error_msg = f"Error searching for entity {entity}: {str(e)}"
            logger.error(error_msg)
            return {
                "entity": entity,
                "query_type": query_type,
                "query": query,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "error": error_msg,
                "results": []
            }

    def search_entities(self, entities: List[str], prompt: str) -> pd.DataFrame:
        all_results = []
        total_entities = len(entities)

        for idx, entity in enumerate(entities, 1):
            logger.info(f"Processing {idx}/{total_entities}: {entity} with prompt: {prompt}")

            try:
                result = self.search_entity(entity, prompt)
                all_results.append(result)

                if idx < total_entities:
                    time.sleep(RATE_LIMIT)

            except Exception as e:
                error_msg = f"Failed to process entity {entity}: {str(e)}"
                logger.error(error_msg)
                all_results.append({
                    "entity": entity,
                    "error": error_msg,
                    "results": []
                })

        # Flatten results for tabular DataFrame output
        flattened_results = [
            {**{"entity": res["entity"], "query": res["query"]}, **result}
            for res in all_results for result in res.get("results", [])
        ]

        return pd.DataFrame(flattened_results)
