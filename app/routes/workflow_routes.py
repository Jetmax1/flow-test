"""
BizFlow - Workflow API Routes
"""

from flask import Blueprint, request, jsonify
from app.services.workflow_service import run_workflow
import logging

logger = logging.getLogger(__name__)
workflow_bp = Blueprint("workflow", __name__)


@workflow_bp.route("/process-request", methods=["POST"])
def process_request():
    """
    Main endpoint to process a business request through the full workflow.
    
    Expected JSON body:
        { "request_text": "..." }
    
    Returns full structured workflow result.
    """
    data = request.get_json()

    if not data or not data.get("request_text", "").strip():
        return jsonify({"error": "request_text is required and cannot be empty."}), 400

    request_text = data["request_text"].strip()

    try:
        result = run_workflow(request_text)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Workflow processing error: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
