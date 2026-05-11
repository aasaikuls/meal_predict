import logging
import requests
import urllib3
from app.core.config import get_settings
from app.services.llm.base import LLMProvider
from app.services.llm.kariba import SYSTEM_PROMPT, _build_prompt

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logger = logging.getLogger("meal.llm.bedrock")


class BedrockProvider(LLMProvider):
    def call(self, passenger_groups, weights, prediction_results, original_counts, top_nationalities=None) -> str:
        settings = get_settings()
        prompt = _build_prompt(passenger_groups, weights, prediction_results, original_counts, top_nationalities or [])

        bedrock_messages = [{"role": "user", "content": [{"text": prompt}]}]
        body = {
            "messages": bedrock_messages,
            "system": [{"text": SYSTEM_PROMPT}],
            "inferenceConfig": {"temperature": 0},
        }
        api_url = f"{settings.bedrock_base_url}/model/{settings.bedrock_model}/converse"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.llm_user_token}",
        }

        try:
            logger.info(f"Calling AWS Bedrock API at {api_url}...")
            response = requests.post(
                api_url,
                headers=headers,
                json=body,
                verify=False,
                timeout=60,
            )
            if response.status_code == 200:
                res = response.json()
                summary = res["output"]["message"]["content"][0]["text"]
                logger.info("Bedrock summary generated successfully")
                return summary
            else:
                logger.error(f"Bedrock API error {response.status_code}: {response.text}")
        except Exception as exc:
            logger.error(f"Bedrock request failed: {exc}")

        return "AI summary not available due to a connection error."
