#!/usr/bin/env python3
"""Complete the selected key once, then launch Codex from the current project."""

import getpass
import os
import shutil
import subprocess
import sys

from dotenv import dotenv_values, set_key

from llm_config import ROOT


def main() -> int:
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and sys.argv[1] not in ("sorux", "transformcat")):
        print("Usage: bash start.sh [sorux|transformcat]", file=sys.stderr)
        return 2
    provider = sys.argv[1] if len(sys.argv) == 2 else "sorux"
    prefix = provider.upper()
    env_file = ROOT / ".env"
    if not env_file.exists():
        with open(env_file, "x", opener=lambda path, flags: os.open(path, flags, 0o600)) as output:
            output.write((ROOT / ".env.example").read_text())
    os.chmod(env_file, 0o600)
    values = dotenv_values(env_file)
    key_name = prefix + "_API_KEY"
    if not (os.getenv(key_name) or values.get(key_name)):
        partial = dotenv_values(ROOT / "api.partial.env").get(prefix + "_API_KEY_PREFIX")
        if not partial:
            print("Missing API key prefix", file=sys.stderr)
            return 1
        try:
            suffix = getpass.getpass(f"{provider}: enter the missing final character (hidden): ")
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.", file=sys.stderr)
            return 1
        if len(suffix) != 1 or not suffix.isascii() or not suffix.isalnum():
            print("Enter exactly one ASCII letter or number.", file=sys.stderr)
            return 1
        set_key(str(env_file), key_name, partial + suffix)
    set_key(str(env_file), "LLM_PROVIDER", provider, quote_mode="never")
    os.environ["LLM_PROVIDER"] = provider
    local_cli = ROOT / ".tools" / "bin" / "codex"
    if not shutil.which("codex") and not local_cli.is_file():
        if not shutil.which("npm"):
            print("Install Node.js 22+ and npm, then rerun bash start.sh.", file=sys.stderr)
            return 1
        registry = os.getenv("CODEX_NPM_REGISTRY", "https://registry.npmmirror.com")
        result = subprocess.run(["npm", "install", "--prefix", str(ROOT / ".tools"),
                                 "@openai/codex", "--registry=" + registry])
        if result.returncode:
            return result.returncode
    print(f"Starting Codex with {provider}.")
    return subprocess.call([sys.executable, str(ROOT / "scripts" / "run_codex.py")])


if __name__ == "__main__":
    raise SystemExit(main())
