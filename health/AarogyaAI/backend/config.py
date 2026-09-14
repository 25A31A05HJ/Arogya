import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    JWT_EXP_HOURS = int(os.getenv("JWT_EXP_HOURS", "72"))

    # Optional: set LLM_API_KEY + LLM_API_URL to plug in a real LLM
    # (OpenAI-compatible chat-completions endpoint). If unset, the
    # chat engine automatically falls back to the built-in rule-based
    # responses, so the app runs fully offline out of the box.
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_API_URL = os.getenv("LLM_API_URL", "https://api.openai.com/v1/chat/completions")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
