"""
BizFlow - LLM Service (Google Gemini Integration)

Handles all interactions with the Gemini API for:
- Request Classification
- Information Extraction
"""

import os
import json
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Configure Gemini client once at module load
_gemini_configured = False


def _configure_gemini():
    """Configure Gemini API with key from environment."""
    global _gemini_configured
    if not _gemini_configured:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        genai.configure(api_key=api_key)
        _gemini_configured = True


def _load_prompt(filename: str) -> str:
    """Load prompt template from the prompts directory."""
    prompt_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "prompts", filename
    )
    with open(os.path.abspath(prompt_path), "r") as f:
        return f.read()


def _call_gemini(prompt: str) -> str:
    """
    Call the Gemini API with a prompt and return the text response.
    
    Args:
        prompt: Full prompt string to send to Gemini.
    
    Returns:
        Text response from Gemini.
    """
    _configure_gemini()
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()


def classify_request(request_text: str) -> dict:
    """
    Use Gemini to classify the incoming business request.
    
    Returns:
        {
            "category": str,
            "confidence": str,
            "reasoning": str
        }
    """
    try:
        prompt_template = _load_prompt("classification_prompt.txt")
        prompt = prompt_template.replace("{{REQUEST_TEXT}}", request_text)
        raw_response = _call_gemini(prompt)

        # Try to parse JSON from response
        cleaned = raw_response.strip().strip("```json").strip("```").strip()
        result = json.loads(cleaned)

        return {
            "category": result.get("category", "General Inquiry"),
            "confidence": result.get("confidence", "Medium"),
            "reasoning": result.get("reasoning", "No reasoning provided."),
        }

    except json.JSONDecodeError:
        logger.warning("Gemini classification returned non-JSON. Parsing manually.")
        return {
            "category": "General Inquiry",
            "confidence": "Low",
            "reasoning": "Could not parse structured response from LLM.",
        }
    except Exception as e:
        logger.error(f"Classification error: {e}")
        raise


def extract_information(request_text: str) -> dict:
    """
    Use Gemini to extract structured business information from the request.
    
    Returns:
        Dictionary of extracted fields (customer name, email, amounts, etc.)
    """
    try:
        prompt_template = _load_prompt("extraction_prompt.txt")
        prompt = prompt_template.replace("{{REQUEST_TEXT}}", request_text)
        raw_response = _call_gemini(prompt)

        # Clean and parse JSON
        cleaned = raw_response.strip().strip("```json").strip("```").strip()
        result = json.loads(cleaned)
        return result

    except json.JSONDecodeError:
        logger.warning("Gemini extraction returned non-JSON.")
        return {
            "customer_name": None,
            "company_name": None,
            "amount": None,
            "invoice_id": None,
            "payment_reference": None,
            "customer_id": None,
            "email": None,
            "dates": [],
            "issue_summary": "Could not extract summary.",
        }
    except Exception as e:
        logger.error(f"Extraction error: {e}")
        raise
