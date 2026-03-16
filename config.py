import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

GROQ_KEY      = os.getenv("GROQ_API_KEY", "")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt120b")

GROQ_MODELS = {
    "gpt120b":   "openai/gpt-oss-120b",
    "gpt20b":    "openai/gpt-oss-20b",
}

VALID_ALIASES = set(GROQ_MODELS.keys())

def validate():
    """Validate config at startup. Raises EnvironmentError with a clear message."""
    if not GROQ_KEY:
        raise EnvironmentError(
            "GROQ_API_KEY is not set.\n"
            "  1. Get a free key at https://console.groq.com\n"
            "  2. Add it to a .env file:  GROQ_API_KEY=gsk_...\n"
            "  3. Or export it:           export GROQ_API_KEY=gsk_..."
        )
    # Warn if DEFAULT_MODEL is not a known alias or raw model string
    if DEFAULT_MODEL not in GROQ_MODELS and DEFAULT_MODEL not in GROQ_MODELS.values():
        import warnings
        warnings.warn(
            f"DEFAULT_MODEL='{DEFAULT_MODEL}' is not a known alias. "
            f"Known aliases: {', '.join(VALID_ALIASES)}"
        )