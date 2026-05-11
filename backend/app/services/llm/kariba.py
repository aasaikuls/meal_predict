import logging
import requests
import urllib3
from app.core.config import get_settings
from app.services.llm.base import LLMProvider

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logger = logging.getLogger("meal.llm.kariba")

SYSTEM_PROMPT = (
    "You are a strategic advisor for airline meal planning. "
    "Write clear, simple explanations for ASEAN business users in plain English. "
    "Avoid complex corporate jargon. Write exactly 2 paragraphs without bullet points. "
    "Focus on practical business insights that anyone can understand."
)

USER_PROMPT_TEMPLATE = """You are explaining meal predictions to airline executives.

TOTAL PASSENGERS: {total_passengers}{top_nat_section}

MEAL CHANGES:
{comparison_text}

TOP PASSENGER GROUPS:
{groups_text}

TASK:
Write a professional executive summary explaining WHY the AI recommends these meal quantities. Write exactly 2 paragraphs (30-50 words each, 60-100 words total) that flow naturally. Focus on business insights and strategic implications, not technical details.

RULES:
1. Write in prose paragraphs, NOT bullet points or numbered lists
2. Use simple, clear English suitable for ASEAN business users - avoid complex corporate jargon
3. Use straightforward words: say "order" not "provision", "groups" not "cohorts", "prefer" not "skew toward", "need" not "shortfalls"
4. Describe passengers naturally: "business travelers," "families with children," "senior passengers," "leisure travelers" - NOT "31-50 age group"
5. Present counts as natural percentages: "Indian travelers make up 45% of passengers" instead of "(68 out of 154)"
6. Integrate cultural insights naturally: "Saturday timing aligns with Hindu vegetarian traditions"
7. Connect insights to business outcomes: "keeps guests happy", "reduces food waste", "improves service", "saves costs"
8. Focus on PRIMARY demographic drivers
9. DO NOT repeat the final meal counts or percentages
10. DO NOT make up numbers - only use data provided above
11. Each paragraph should be 30-50 words
12. Avoid words like: cluster, provision, cohorts, skew, provisioning, shortfalls, erode, leverage, optimize
"""


def _build_prompt(passenger_groups, weights, prediction_results, original_counts, top_nationalities):
    total_passengers = sum(g.count for g in passenger_groups)

    # Top nationalities section
    top_nat_section = ""
    if top_nationalities:
        lines = []
        for nat in top_nationalities[:5]:
            line = f"- {nat.nationality_code}: {nat.count} passengers ({nat.percentage:.1f}%)"
            if nat.reasoning:
                line += f"\n  Cultural Insight: {nat.reasoning}"
            if nat.sources:
                line += f"\n  Source: {nat.sources}"
            lines.append(line)
        top_nat_section = "\n\nTOP NATIONALITIES ON THIS FLIGHT:\n" + "\n\n".join(lines)

    # Comparison text
    comparison_lines = []
    for protein in sorted(set(list(original_counts.keys()) + list(prediction_results.keys()))):
        old = original_counts.get(protein, 0)
        new = prediction_results.get(protein, 0)
        change = new - old
        pct = (change / old * 100) if old > 0 else 0
        comparison_lines.append(f"- {protein}: {old:.0f} → {new:.0f} ({change:+.0f}, {pct:+.1f}%)")
    comparison_text = "\n".join(comparison_lines)

    # Passenger group details (top 10)
    sorted_groups = sorted(passenger_groups, key=lambda g: g.count, reverse=True)[:10]
    group_details = []
    for group in sorted_groups:
        detail = (
            f"Passenger Group: {group.count} passengers\n"
            f"- Profile: Nationality={group.nationality}, Age Group={group.age_group}, "
            f"Destination={group.destination}, Meal Time={group.meal_time}, Weekday={group.weekday}\n"
            f"- Final Weighted Probabilities: "
            + ", ".join(f"{p}: {v * 100:.1f}%" for p, v in group.probabilities.items())
        )
        if group.reasoning:
            insights = "\n- Cultural/Behavioral Insights:"
            for feature, reason in group.reasoning.items():
                if reason and reason.strip():
                    insights += f"\n  * {feature.replace('_', ' ').title()}: {reason}"
            if insights != "\n- Cultural/Behavioral Insights:":
                detail += insights
        group_details.append(detail)

    return USER_PROMPT_TEMPLATE.format(
        total_passengers=total_passengers,
        top_nat_section=top_nat_section,
        comparison_text=comparison_text,
        groups_text="\n\n".join(group_details),
    )


class KaribaProvider(LLMProvider):
    def call(self, passenger_groups, weights, prediction_results, original_counts, top_nationalities=None) -> str:
        settings = get_settings()
        prompt = _build_prompt(passenger_groups, weights, prediction_results, original_counts, top_nationalities or [])

        body = {
            "engine": settings.kariba_model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0,
            "user": "talk-with-data",
            "pii_type": ["no_pii"],
        }
        headers = {
            "x-kariba-user-token": settings.llm_user_token,
            "Content-Type": "application/json",
        }

        try:
            logger.info("Calling Kariba LLM API...")
            response = requests.post(
                settings.kariba_api_url,
                headers=headers,
                json=body,
                verify=False,
                timeout=30,
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("choices"):
                    summary = data["choices"][0]["message"]["content"]
                    logger.info("Kariba summary generated successfully")
                    return summary
            elif response.status_code == 403:
                logger.error("Kariba auth failed (403)")
                return "AI summary not available - authentication issue."
            else:
                logger.error(f"Kariba API error {response.status_code}: {response.text}")
        except Exception as exc:
            logger.error(f"Kariba request failed: {exc}")

        return "AI summary not available due to a connection error."
