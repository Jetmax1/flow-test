"""
BizFlow - Validation Service

Rule-based validation engine for extracted request data.
Checks for missing fields, invalid formats, and completeness.
"""

import re
import logging

logger = logging.getLogger(__name__)

# Fields that are considered critical depending on request category
REQUIRED_FIELDS_BY_CATEGORY = {
    "Refund Request": ["customer_name", "email", "amount", "invoice_id", "payment_reference"],
    "Invoice Query": ["customer_name", "email", "invoice_id"],
    "Payment Failure": ["customer_name", "email", "amount", "payment_reference"],
    "Contract Review": ["customer_name", "company_name", "email"],
    "Technical Support": ["customer_name", "email"],
    "General Inquiry": ["customer_name", "email"],
}

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$")


def validate_extracted_data(extracted: dict, category: str) -> dict:
    """
    Validate extracted fields against required fields for the category.
    
    Args:
        extracted: Dictionary of extracted fields from LLM.
        category: Classified request category.
    
    Returns:
        {
            "status": "complete" | "warning" | "incomplete",
            "missing_fields": [...],
            "warnings": [...],
            "errors": [...],
            "field_status": { field: "present" | "missing" | "invalid" }
        }
    """
    required_fields = REQUIRED_FIELDS_BY_CATEGORY.get(category, ["customer_name", "email"])

    missing_fields = []
    warnings = []
    errors = []
    field_status = {}

    # Check all known fields
    all_fields = [
        "customer_name", "company_name", "amount", "invoice_id",
        "payment_reference", "customer_id", "email", "dates", "issue_summary"
    ]

    for field in all_fields:
        value = extracted.get(field)
        is_required = field in required_fields

        # Handle empty/None values
        if value is None or value == "" or value == [] or value == "null":
            field_status[field] = "missing"
            if is_required:
                missing_fields.append(field)
            else:
                warnings.append(f"Optional field '{field}' not found.")
        else:
            # Special validation: email format
            if field == "email":
                if not EMAIL_REGEX.match(str(value)):
                    field_status[field] = "invalid"
                    errors.append(f"Email format invalid: '{value}'")
                else:
                    field_status[field] = "present"
            # Special validation: amount should be numeric
            elif field == "amount":
                try:
                    float(str(value).replace(",", "").replace("INR", "").replace("$", "").strip())
                    field_status[field] = "present"
                except ValueError:
                    field_status[field] = "invalid"
                    errors.append(f"Amount value could not be parsed: '{value}'")
            else:
                field_status[field] = "present"

    # Determine overall status
    if missing_fields or errors:
        status = "incomplete"
    elif warnings:
        status = "warning"
    else:
        status = "complete"

    return {
        "status": status,
        "missing_fields": missing_fields,
        "warnings": warnings,
        "errors": errors,
        "field_status": field_status,
    }
