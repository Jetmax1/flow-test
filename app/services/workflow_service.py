"""
BizFlow - Workflow Orchestration Service

Orchestrates the full business request processing pipeline:
1. Classification (Gemini)
2. Extraction (Gemini)
3. Validation (Rule-based)
4. Risk/Priority Assessment (Rule-based)
5. Next Action Recommendation (Hybrid)
6. Workflow Trace
"""

import logging
from datetime import datetime, timezone
from app.services.llm_service import classify_request, extract_information
from app.services.validation_service import validate_extracted_data
from app.services.risk_service import assess_risk

logger = logging.getLogger(__name__)


def _recommend_next_action(
    category: str,
    validation: dict,
    risk: dict,
    extracted: dict,
) -> dict:
    """
    Determine the recommended next action based on workflow results.
    
    Returns:
        {
            "action": str,
            "reason": str,
            "auto_processable": bool
        }
    """
    priority = risk["priority"]
    status = validation["status"]
    missing = validation["missing_fields"]

    # Missing critical info → request more details
    if status == "incomplete" and missing:
        return {
            "action": "Request Missing Information",
            "reason": f"Required fields are missing: {', '.join(missing)}. "
                       "Cannot process until complete.",
            "auto_processable": False,
        }

    # Legal/escalation keywords with high risk
    if priority == "High" and category in ("Refund Request", "Payment Failure"):
        return {
            "action": "Escalate to Finance Team",
            "reason": "High-priority financial request. Requires finance team review and approval.",
            "auto_processable": False,
        }

    if priority == "High" and category == "Contract Review":
        return {
            "action": "Send to Legal Team",
            "reason": "High-risk contract matter. Legal team review required.",
            "auto_processable": False,
        }

    if priority == "High":
        return {
            "action": "Escalate for Manual Review",
            "reason": "High-risk request requiring human oversight before processing.",
            "auto_processable": False,
        }

    # Medium priority — standard processing
    if priority == "Medium":
        if category == "Invoice Query":
            return {
                "action": "Route to Billing Department",
                "reason": "Invoice-related query with complete information. Billing can handle.",
                "auto_processable": True,
            }
        return {
            "action": "Mark for Manual Review",
            "reason": "Medium-priority request. Assign to available agent for review.",
            "auto_processable": False,
        }

    # Low priority with complete info → auto approve or standard queue
    if status == "complete":
        return {
            "action": "Auto-Approve & Queue",
            "reason": "Low-risk request with all required information. Safe to process automatically.",
            "auto_processable": True,
        }

    return {
        "action": "Standard Processing Queue",
        "reason": "Route to standard support queue for handling.",
        "auto_processable": False,
    }


def _build_trace(timestamps: dict) -> list:
    """Build the workflow trace timeline entries."""
    steps = [
        ("📥", "Request Received", "request_received"),
        ("🏷️", "Classification Complete", "classification_done"),
        ("🔍", "Information Extracted", "extraction_done"),
        ("✅", "Validation Complete", "validation_done"),
        ("⚠️", "Risk Assessed", "risk_done"),
        ("💡", "Recommendation Generated", "recommendation_done"),
    ]
    trace = []
    for icon, label, key in steps:
        trace.append({
            "icon": icon,
            "label": label,
            "timestamp": timestamps.get(key, ""),
        })
    return trace


def run_workflow(request_text: str) -> dict:
    """
    Run the complete BizFlow processing pipeline.
    
    Args:
        request_text: Raw business request text from user.
    
    Returns:
        Full structured workflow result dictionary.
    """
    timestamps = {}

    # Step 1: Record receipt
    timestamps["request_received"] = datetime.now(timezone.utc).isoformat()
    logger.info("Workflow started.")

    # Step 2: Classification (Gemini)
    classification = classify_request(request_text)
    timestamps["classification_done"] = datetime.now(timezone.utc).isoformat()
    logger.info(f"Classified as: {classification['category']}")

    # Step 3: Information Extraction (Gemini)
    extracted = extract_information(request_text)
    timestamps["extraction_done"] = datetime.now(timezone.utc).isoformat()
    logger.info("Extraction complete.")

    # Step 4: Validation (Rule-based)
    validation = validate_extracted_data(extracted, classification["category"])
    timestamps["validation_done"] = datetime.now(timezone.utc).isoformat()
    logger.info(f"Validation status: {validation['status']}")

    # Step 5: Risk Assessment (Rule-based)
    risk = assess_risk(request_text, extracted, classification["category"])
    timestamps["risk_done"] = datetime.now(timezone.utc).isoformat()
    logger.info(f"Risk priority: {risk['priority']}, score: {risk['risk_score']}")

    # Step 6: Next Action Recommendation
    recommendation = _recommend_next_action(
        classification["category"], validation, risk, extracted
    )
    timestamps["recommendation_done"] = datetime.now(timezone.utc).isoformat()
    logger.info(f"Recommendation: {recommendation['action']}")

    # Step 7: Build trace
    trace = _build_trace(timestamps)

    # Assemble final result
    result = {
        "request_text": request_text,
        "classification": classification,
        "extracted_data": extracted,
        "validation": validation,
        "risk_assessment": risk,
        "recommendation": recommendation,
        "workflow_trace": trace,
        "processed_at": timestamps["recommendation_done"],
    }

    return result
