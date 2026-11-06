#!/usr/bin/env python3
"""Change the active provider in the local .env file."""

import os
import sys
from pathlib import Path

from dotenv import set_key


PROVIDERS = {"sorux", "transformcat"}


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in PROVIDERS:
        print("Usage: python scripts/use_provider.py sorux|transformcat", file=sys.stderr)
        return 2
    env_file = Path(".env")
    if not env_file.is_file():
        print(".env is missing; run bash bootstrap.sh first", file=sys.stderr)
        return 1
    provider = sys.argv[1]
    set_key(str(env_file), "LLM_PROVIDER", provider, quote_mode="never")
    os.chmod(env_file, 0o600)
    print(f"Active provider: {provider}. API keys were not changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
