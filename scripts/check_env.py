#!/usr/bin/env python3
"""Report runtime readiness without printing secrets."""

import importlib.metadata
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from llm_config import get_provider_config


PACKAGES = ("numpy", "pandas", "scipy", "scikit-learn", "matplotlib", "jupyterlab", "openai")


def main() -> int:
    print(f"Platform: {platform.platform()}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Virtual environment: {sys.prefix != sys.base_prefix}")
    print(f"Working directory: {Path.cwd()}")

    missing = []
    for package in PACKAGES:
        try:
            version = importlib.metadata.version(package)
            print(f"{package}: {version}")
        except importlib.metadata.PackageNotFoundError:
            missing.append(package)
            print(f"{package}: MISSING")

    gpu = shutil.which("nvidia-smi")
    if gpu:
        result = subprocess.run([gpu, "--query-gpu=name,driver_version", "--format=csv,noheader"], text=True, capture_output=True)
        print("NVIDIA GPU: " + (result.stdout.strip() or result.stderr.strip() or f"nvidia-smi exited {result.returncode}"))
    else:
        print("NVIDIA GPU: nvidia-smi not found")

    env_file = Path(__file__).resolve().parent.parent / ".env"
    print(f".env file: {'present' if env_file.is_file() else 'missing'}")
    try:
        config = get_provider_config()
        print(f"LLM provider: {config.name}")
        print(f"LLM model: {config.model or 'not set'}")
        print(f"Provider API key: {'set' if config.api_key else 'not set'}")
    except ValueError as error:
        print(f"LLM configuration: {error}")
        return 1
    return 1 if missing or not config.api_key or not config.model else 0


if __name__ == "__main__":
    raise SystemExit(main())
