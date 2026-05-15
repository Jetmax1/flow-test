"""
BizFlow - Database Utility

MongoDB connection management and data persistence.
"""

import os
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

logger = logging.getLogger(__name__)

_client = None
_db = None


def init_db():
    """
    Initialize MongoDB connection.
    Called once at app startup.
    """
    global _client, _db
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    try:
        _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Verify connection
        _client.admin.command("ping")
        _db = _client["bizflow"]
        logger.info("MongoDB connected successfully.")
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.warning(f"MongoDB connection failed: {e}. Running without persistence.")
        _client = None
        _db = None


def get_db():
    """Return the database instance (may be None if connection failed)."""
    return _db


def save_workflow_result(result: dict):
    """
    Save a completed workflow result to MongoDB.
    
    Args:
        result: Full workflow result dictionary.
    
    Raises:
        Exception if DB is unavailable or write fails.
    """
    if _db is None:
        raise ConnectionError("MongoDB is not connected.")

    # Use a separate copy without the _id field for clean insertion
    doc = dict(result)
    collection = _db["workflow_results"]
    collection.insert_one(doc)
    logger.info("Workflow result saved to MongoDB.")


def get_recent_results(limit: int = 20) -> list:
    """
    Retrieve the most recent workflow results from MongoDB.
    
    Args:
        limit: Maximum number of records to return.
    
    Returns:
        List of workflow result dictionaries.
    """
    if _db is None:
        return []

    collection = _db["workflow_results"]
    results = list(
        collection.find({}, {"_id": 0})
        .sort("processed_at", -1)
        .limit(limit)
    )
    return results
