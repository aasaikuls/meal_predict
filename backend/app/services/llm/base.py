from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    """Abstract base class for all LLM providers."""

    @abstractmethod
    def call(
        self,
        passenger_groups: list,
        weights: dict,
        prediction_results: dict,
        original_counts: dict,
        top_nationalities: list | None = None,
    ) -> str:
        """
        Generate an AI summary for a meal prediction.
        Returns the summary string.
        """
