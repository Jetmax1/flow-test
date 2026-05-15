"""
BizFlow - Application Runner

Run this file to start the Flask backend server.
Usage: python run.py
"""

from app.app import create_app
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
