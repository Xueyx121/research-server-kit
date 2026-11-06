"""Load the selected OpenAI-compatible provider without exposing its key."""

import os
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


PROVIDERS = {
    "sorux": {
        "prefix": "SORUX",
        "default_base_url": "https://ai.soruxgpt.com/v1",
    },
    "transformcat": {
        "prefix": "TRANSFORMCAT",
        "default_base_url": "https://www.transformcat.cn/",
    },
}
ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class ProviderConfig:
    name: str
    base_url: str
    model: str
    api_key: str = field(repr=False)


def get_provider_config() -> ProviderConfig:
    load_dotenv(ROOT / ".env")
    name = os.getenv("LLM_PROVIDER", "sorux").strip().lower()
    if name not in PROVIDERS:
        choices = ", ".join(PROVIDERS)
        raise ValueError(f"Unknown LLM_PROVIDER {name!r}; choose one of: {choices}")

    provider = PROVIDERS[name]
    prefix = provider["prefix"]
    return ProviderConfig(
        name=name,
        base_url=os.getenv(f"{prefix}_BASE_URL", provider["default_base_url"]).strip(),
        model=os.getenv(f"{prefix}_MODEL", "").strip(),
        api_key=os.getenv(f"{prefix}_API_KEY", "").strip(),
    )


def create_client(config: Optional[ProviderConfig] = None) -> OpenAI:
    config = config or get_provider_config()
    if not config.api_key:
        raise ValueError(f"Set {config.name.upper()}_API_KEY in .env before making requests")
    if not config.base_url or not config.model:
        raise ValueError("Provider base URL and model must be set in .env")
    return OpenAI(api_key=config.api_key, base_url=config.base_url)
