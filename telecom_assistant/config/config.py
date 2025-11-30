import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Data paths
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "telecom.db")
DOCS_DIR = os.path.join(DATA_DIR, "documents")

# API Keys
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Model Configuration
LLM_MODEL = "gpt-3.5-turbo"
LLM_TEMPERATURE = 0.1

# App Settings
APP_NAME = "Telecom Service Assistant"
VERSION = "1.0.0"
