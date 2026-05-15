"""
BizFlow - Flask Application Entry Point
"""

from flask import Flask
from flask_cors import CORS
from app.routes.workflow_routes import workflow_bp
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    CORS(app)

    # Register blueprints
    app.register_blueprint(workflow_bp)

    @app.route("/health", methods=["GET"])
    def health_check():
        """Health check endpoint."""
        return {"status": "ok", "service": "BizFlow API"}, 200

    logger.info("BizFlow Flask app initialized.")
    return app
