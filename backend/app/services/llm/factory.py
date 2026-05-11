from app.core.config import get_settings
from app.services.llm.base import LLMProvider


def get_llm_provider() -> LLMProvider:
    """
    Return the correct LLM provider based on LLM_PROVIDER env var.
    Defaults to 'kariba'. Set LLM_PROVIDER=bedrock to use AWS Bedrock.
    """
    settings = get_settings()
    provider = settings.llm_provider.lower().strip()

    if provider == "bedrock":
        from app.services.llm.bedrock import BedrockProvider
        return BedrockProvider()

    # Default: kariba
    from app.services.llm.kariba import KaribaProvider
    return KaribaProvider()
