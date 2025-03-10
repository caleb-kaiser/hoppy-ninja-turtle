import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Azure AI Search configuration
AZURE_SEARCH_SERVICE_ENDPOINT = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
AZURE_SEARCH_ADMIN_KEY = os.getenv("AZURE_SEARCH_ADMIN_KEY")
AZURE_SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME")

# OpenAI API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4-turbo")

# Comet ML / Opik configuration
COMET_API_KEY = os.getenv("COMET_API_KEY")
COMET_WORKSPACE = os.getenv("COMET_WORKSPACE")
COMET_PROJECT_NAME = os.getenv("COMET_PROJECT_NAME", "rag-pipeline")

# Application defaults
DEFAULT_TOP_K = 5
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 500 