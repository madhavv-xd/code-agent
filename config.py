#configs of my app 
import os
from dotenv import load_dotenv

load_dotenv()

PROVIDER     = os.getenv("MODEL_PROVIDER", "ollama")
GEMINI_KEY   = os.getenv("GEMINI_API_KEY", "") #returns empty if gemini api key is not found
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b") 