#!/usr/bin/env python3
"""Launch Codex CLI with the selected provider; no auth.json copy is needed."""

import json
import os
import shutil
import subprocess
import sys

from llm_config import ROOT, get_provider_config


def main() -> int:
    executable = shutil.which("codex")
    if not executable:
        local = ROOT / ".tools" / "bin" / "codex"
        if local.is_file():
            executable = str(local)
    if not executable:
        print('Codex CLI missing. See README for installation.', file=sys.stderr)
        return 1
    try:
        config = get_provider_config()
        if not config.api_key or not config.base_url or not config.model:
            raise ValueError("Selected provider needs API key, base URL and model in .env")
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 1

    # JSON strings are also valid TOML strings. Secrets travel only via env.
    prefix = config.name.upper()
    settings = {
        "model": json.dumps(config.model),
        "model_provider": json.dumps(config.name),
        "model_reasoning_effort": '"high"',
        "disable_response_storage": "true",
        "sandbox_mode": '"workspace-write"',
        "approval_policy": '"never"',
        "sandbox_workspace_write.network_access": "true",
        f"model_providers.{config.name}": '{name=' + json.dumps(config.name)
        + ',base_url=' + json.dumps(config.base_url)
        + ',wire_api="responses",env_key=' + json.dumps(prefix + "_API_KEY") + '}',
    }
    command = [executable]
    for key, value in settings.items():
        command.extend(["-c", f"{key}={value}"])
    command.extend(sys.argv[1:])
    environment = os.environ.copy()
    # The other provider's key need not be inherited by the launched CLI.
    for key in ("SORUX_API_KEY", "TRANSFORMCAT_API_KEY"):
        environment.pop(key, None)
    environment[prefix + "_API_KEY"] = config.api_key
    return subprocess.call(command, env=environment)


if __name__ == "__main__":
    raise SystemExit(main())
