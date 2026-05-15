"""
BizFlow - Risk & Priority Assessment Service

Rule-based engine to determine request priority and risk score.
Uses keyword matching and amount thresholds.
"""

import logging
import re

logger = logging.getLogger(__name__)

# High-priority trigger keywords
HIGH_PRIORITY_KEYWORDS = [
    "refund", "failed payment", "legal", "urgent", "escalation",
    "complaint", "fraud", "dispute", "chargeback", "sue", "lawsuit",
    "overdue", "critical", "emergency", "immediately", "asap",
]

MEDIUM_PRIORITY_KEYWORDS = [
    "invoice", "query", "review", "pending", "delayed", "follow up",
    "clarification", "update", "status", "check",
]

# Amount thresholds (in base currency units)
AMOUNT_HIGH_THRESHOLD = 50000
AMOUNT_MEDIUM_THRESHOLD = 10000


def _parse_amount(amount_value) -> float:
    """Safely parse an amount value to float."""
    if amount_value is None:
        return 0.0
    try:
        cleaned = str(amount_value)
        cleaned = re.sub(r"[^\d.]", "", cleaned)
        return float(cleaned) if cleaned else 0.0
    except (ValueError, TypeError):
        return 0.0


def assess_risk(request_text: str, extracted: dict, category: str) -> dict:
    """
    Assess risk and priority of the business request.
    
    Args:
        request_text: Original request text.
        extracted: Extracted fields dictionary.
        category: Classified category.
    
    Returns:
        {
            "priority": "High" | "Medium" | "Low",
            "risk_score": int (0–100),
            "trigger_reasons": [str, ...],
        }
    """
    text_lower = request_text.lower()
    trigger_reasons = []
    score = 0

    # --- Keyword-based scoring ---
    for keyword in HIGH_PRIORITY_KEYWORDS:
        if keyword in text_lower:
            score += 25
            trigger_reasons.append(f"High-priority keyword detected: '{keyword}'")

    for keyword in MEDIUM_PRIORITY_KEYWORDS:
        if keyword in text_lower:
            score += 10
            trigger_reasons.append(f"Medium-priority keyword detected: '{keyword}'")

    # --- Category-based scoring ---
    category_scores = {
        "Refund Request": 20,
        "Payment Failure": 20,
        "Contract Review": 15,
        "Invoice Query": 10,
        "Technical Support": 10,
        "General Inquiry": 5,
    }
    cat_score = category_scores.get(category, 5)
    score += cat_score
    trigger_reasons.append(f"Category '{category}' base score: +{cat_score}")

    # --- Amount-based scoring ---
    amount = _parse_amount(extracted.get("amount"))
    if amount >= AMOUNT_HIGH_THRESHOLD:
        score += 30
        trigger_reasons.append(f"High-value transaction: {amount:,.0f} (≥ 50,000)")
    elif amount >= AMOUNT_MEDIUM_THRESHOLD:
        score += 15
        trigger_reasons.append(f"Medium-value transaction: {amount:,.0f} (10,000–50,000)")
    elif amount > 0:
        score += 5
        trigger_reasons.append(f"Low-value transaction: {amount:,.0f} (< 10,000)")

    # Cap at 100
    risk_score = min(score, 100)

    # Determine priority label
    if risk_score >= 50:
        priority = "High"
    elif risk_score >= 25:
        priority = "Medium"
    else:
        priority = "Low"

    return {
        "priority": priority,
        "risk_score": risk_score,
        "trigger_reasons": trigger_reasons,
    }
