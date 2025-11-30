import os

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Data paths
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "telecom.db")
DOCS_DIR = os.path.join(DATA_DIR, "documents")

# API Keys (loaded from environment)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# App Settings
APP_NAME = "Telecom Service Assistant"
VERSION = "1.0.0"
