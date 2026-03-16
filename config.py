import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

GROQ_KEY      = os.getenv("GROQ_API_KEY", "")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt120b")

GROQ_MODELS = {
    "gpt120b":   "openai/gpt-oss-120b",
    "gpt20b":    "openai/gpt-oss-20b",
}