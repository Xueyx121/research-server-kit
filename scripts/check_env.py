#!/usr/bin/env python3
"""Report runtime readiness without printing secrets."""

import importlib.metadata
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv


PACKAGES = ("numpy", "pandas", "scipy", "scikit-learn", "matplotlib", "jupyterlab", "openai")


def main() -> int:
    load_dotenv()
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

    env_file = Path(".env")
    print(f".env file: {'present' if env_file.is_file() else 'missing'}")
    print(f"OPENAI_API_KEY: {'set in process environment' if os.getenv('OPENAI_API_KEY') else 'not set in process environment'}")
    if os.getenv("OPENAI_BASE_URL"):
        print("OPENAI_BASE_URL: set")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
