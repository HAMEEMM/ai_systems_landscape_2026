"""
shared/utils/llm_client.py

Central helper for initialising LLM clients from .env keys.
Import this in any phase instead of repeating boilerplate.

Usage:
    from shared.utils.llm_client import get_openai_client, get_anthropic_client

    client, model = get_openai_client()
    response = client.chat.completions.create(model=model, messages=[...])
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load shared/config/.env first; fall back to any .env in parent dirs
_CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
load_dotenv(_CONFIG_DIR / ".env", override=False)
load_dotenv(Path(__file__).resolve().parents[3] / ".env", override=False)


def get_env(key: str, required: bool = True) -> str:
    """Get an environment variable; raise a clear error if missing and required."""
    value = os.getenv(key)
    if required and not value:
        raise EnvironmentError(
            f"Environment variable '{key}' is not set.\n"
            f"Copy shared/config/.env.example → shared/config/.env and fill in your keys."
        )
    return value or ""


def get_openai_client(model: str = "gpt-4o"):
    """Return an (OpenAI client, model name) tuple. Fails fast if key is missing."""
    from openai import OpenAI

    api_key = get_env("OPENAI_API_KEY")
    if api_key.startswith("sk-your"):
        raise EnvironmentError(
            "OPENAI_API_KEY is still the placeholder value. "
            "Edit shared/config/.env and set your real key."
        )
    return OpenAI(api_key=api_key), model


def get_anthropic_client(model: str = "claude-opus-4-5"):
    """Return an (Anthropic client, model name) tuple."""
    import anthropic

    api_key = get_env("ANTHROPIC_API_KEY")
    if api_key.startswith("sk-ant-your"):
        raise EnvironmentError(
            "ANTHROPIC_API_KEY is still the placeholder value. "
            "Edit shared/config/.env and set your real key."
        )
    return anthropic.Anthropic(api_key=api_key), model
