## Code for the summary ai in resulsults pages. User token needs to be changed for this to work.

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List
import os
import requests
import logging
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger("meal.ai_summary")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

router = APIRouter()

class PassengerGroup(BaseModel):
    nationality: str
    age_group: str
    destination: str
    meal_time: str
    weekday: str = ""
    count: int
    probabilities: Dict[str, float]  # Final weighted probabilities
    metric_probabilities: Dict[str, Dict[str, float]] = {}  # Individual metric probabilities
    reasoning: Dict[str, str] = {}  # Reasoning from CSV files for each feature

class TopNationality(BaseModel):
    nationality_code: str
    count: int
    percentage: float
    reasoning: str = ""
    sources: str = ""

class PredictionSummaryRequest(BaseModel):
    flight_number: str
    flight_date: str
    passenger_groups: List[PassengerGroup]
    weights: Dict[str, float]  # e.g., {"nationality_importance": 40, "age_importance": 20, ...}
    prediction_results: Dict[str, float]  # e.g., {"Chicken": 45.2, "Beef": 54.8}
    original_counts: Dict[str, int]  # e.g., {"Chicken": 50, "Beef": 60}
    top_nationalities: List[TopNationality] = []  # Top 5 nationalities with reasoning


# Configuration
KARIBA_API_URL = os.getenv("KARIBA_API_URL", "https://api.nonprod.kariba.de.sin.auto2.nonprod.c0.sq.com.sg/api/v2/call-llm/")
# KARIBA_API_URL = os.getenv("KARIBA_API_URL", "https://localhost:9005/api/v2/call-llm/")
DEFAULT_MODEL = "GPT5-mini"
## change to correct token here #"ccb28b2533d94af63b88052309b2c2f560ec61a6e2cdad08f7cae0587a5831c5"
USER_TOKEN = os.getenv("LLM_USER_TOKEN",'ccb28b2533d94af63b88052309b2c2f560ec61a6e2cdad08f7cae0587a5831c5') # testing purposes



def call_kariba_llm(passenger_groups, weights, prediction_results, original_counts, top_nationalities=None):
    """Call Kariba LLM API to analyze meal prediction trends."""
    
    # Build feature weights text
    weights_text = "\n".join([f"- {k.replace('_', ' ').title()}: {v}%" for k, v in weights.items()])
    
    # Build top nationalities section
    top_nationalities_text = ""
    if top_nationalities and len(top_nationalities) > 0:
        top_nat_lines = []
        for nat in top_nationalities[:5]:  # Top 5 only
            nat_line = f"- {nat.nationality_code}: {nat.count} passengers ({nat.percentage:.1f}%)"
            if nat.reasoning:
                nat_line += f"\n  Cultural Insight: {nat.reasoning}"
            if nat.sources:
                nat_line += f"\n  Source: {nat.sources}"
            top_nat_lines.append(nat_line)
        top_nationalities_text = "\n\n".join(top_nat_lines)
    
    # Build passenger groups details - LIMIT to top groups to avoid prompt being too long
    group_details = []
    # Sort by count descending and take top 10 groups
    sorted_groups = sorted(passenger_groups, key=lambda g: g.count, reverse=True)[:10]
    
    for group in sorted_groups:
        # Clean text - remove any problematic characters
        nationality = str(group.nationality).replace('"', '').replace("'", "")
        destination = str(group.destination).replace('"', '').replace("'", "")
        age_group = str(group.age_group).replace('"', '').replace("'", "")
        meal_time = str(group.meal_time).replace('"', '').replace("'", "")
        weekday = str(group.weekday).replace('"', '').replace("'", "")
        
        detail = f"""Passenger Group: {group.count} passengers
- Profile: Nationality={nationality}, Age Group={age_group}, Destination={destination}, Meal Time={meal_time}, Weekday={weekday}
- Final Weighted Probabilities: {', '.join([f'{protein}: {prob*100:.1f}%' for protein, prob in group.probabilities.items()])}"""
        
        # Add reasoning insights if available
        if group.reasoning:
            reasoning_text = "\n- Cultural/Behavioral Insights:"
            for feature, reason in group.reasoning.items():
                if reason and reason.strip():
                    reasoning_text += f"\n  * {feature.replace('_', ' ').title()}: {reason}"
            if reasoning_text != "\n- Cultural/Behavioral Insights:":
                detail += reasoning_text
        
        group_details.append(detail)
    
    groups_text = "\n\n".join(group_details)
    
    # Calculate total passengers
    total_passengers = sum([g.count for g in passenger_groups])
    
    # Build comparison: old vs new with changes
    comparison_lines = []
    for protein in sorted(set(list(original_counts.keys()) + list(prediction_results.keys()))):
        old_count = original_counts.get(protein, 0)
        new_count = prediction_results.get(protein, 0)
        change = new_count - old_count
        pct_change = (change / old_count * 100) if old_count > 0 else 0
        comparison_lines.append(f"- {protein}: {old_count:.0f} → {new_count:.0f} ({change:+.0f}, {pct_change:+.1f}%)")
    
    comparison_text = "\n".join(comparison_lines)
    
    # Build top nationalities section for prompt
    top_nat_section = ""
    if top_nationalities_text:
        top_nat_section = f"""\n\nTOP NATIONALITIES ON THIS FLIGHT:
{top_nationalities_text}"""
    
    prompt = f"""You are explaining meal predictions to airline executives.

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
4. Describe passengers naturally: "business travelers," "families with children," "senior passengers," "leisure travelers" - NOT "31-50 age group" or "age_group_3"
5. Present counts as natural percentages: "Indian travelers make up 45% of passengers" instead of "(68 out of 154)"
6. Integrate cultural insights naturally: "Saturday timing aligns with Hindu vegetarian traditions" not "due to Shani observance"
7. Connect insights to business outcomes using simple language: "keeps guests happy", "reduces food waste", "improves service", "saves costs"
8. Focus on PRIMARY demographic drivers - don't try to list every feature
9. DO NOT repeat the final meal counts or percentages - they're already shown in charts above
10. DO NOT make up numbers - only use data provided above
11. Each paragraph should be 30-50 words for balanced reading
12. Avoid words like: cluster, provision, cohorts, skew, provisioning, shortfalls, erode, leverage, optimize - use simpler alternatives

GOOD EXECUTIVE SUMMARY (do this):
✅ "Most passengers on this flight are from New Zealand, making up about 65% of travelers. These passengers prefer chicken and fish over beef and lamb, which is why the AI recommends ordering more chicken meals.

The lunch timing also matters because passengers typically choose lighter meals at midday. By matching meal choices with what passengers prefer, we keep guests happy and reduce wasted food."

BAD EXECUTIVE SUMMARY (don't do this):
❌ "New Zealand travelers dominate this route and cluster around lunch service, where demographic cohorts skew toward poultry provisioning to avoid shortfalls and optimize catering efficiency."
(This uses too much jargon: cluster, cohorts, skew, provisioning, shortfalls, optimize - too complex for ASEAN business users)

❌ "- Key driver 1: NZ nationality passengers (87 of 154) favor poultry over red meat culturally
- Key driver 2: Lunch meal time drives lighter chicken preference for midday comfort"
(This is too technical and uses bullet points)

❌ "The 31-50 age group (65 out of 154) prefer seafood. SIN destination shows high chicken probability."
(This uses technical age labels and doesn't explain WHY)
"""

    # Log the full prompt to see what's being sent
    logger.info("=" * 80)
    logger.info("FULL PROMPT BEING SENT TO LLM:")
    logger.info("=" * 80)
    logger.info(prompt)
    logger.info("=" * 80)

    body = {
        "engine": DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": "You are a strategic advisor for airline meal planning. Write clear, simple explanations for ASEAN business users in plain English. Avoid complex corporate jargon. Write exactly 2 paragraphs without bullet points. Focus on practical business insights that anyone can understand."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0,
        "user": "talk-with-data",
        "pii_type": ["no_pii"]
    }
    
    headers = {
        "x-kariba-user-token": USER_TOKEN,
        "Content-Type": "application/json"
    }
    
    try:
        logger.info("Calling Kariba API......Let's see if it works :)))")
        
        response = requests.post(
            url=KARIBA_API_URL,
            headers=headers,
            json=body,
            verify=False,
            timeout=30
        )
        
        logger.info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                summary = data["choices"][0]["message"]["content"]
                logger.info("AI summary generated successfully")
                return summary
        elif response.status_code == 403:
            logger.error(f"Authentication failed (403): {response.text}")
            return "AI summary not available - application access issue!"
        else:
            logger.error(f"API error {response.status_code}: {response.text}")
            
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
    
    return "AI summary not available due to connection error. Please check network connectivity."


@router.post("/api/ai-summary")
async def ai_prediction_summary(request: PredictionSummaryRequest):
    """ Generate AI summary for meal prediction. """
    logger.info(f"AI summary request for {request.flight_number} on {request.flight_date}")
    logger.info(f"Top nationalities provided: {len(request.top_nationalities)}")
    
    summary = call_kariba_llm(
        request.passenger_groups,
        request.weights,
        request.prediction_results,
        request.original_counts,
        request.top_nationalities
    )
    
    return {"summary": summary}
