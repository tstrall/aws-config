#!/usr/bin/env python3

import argparse
import json
import pathlib
import sys

def validate_config_file(env, config_path):
    file_path = pathlib.Path("iac") / env / config_path / "config.json"
    if not file_path.exists():
        return None
    try:
        json.loads(file_path.read_text())
        return (env, True, str(file_path))
    except json.JSONDecodeError as e:
        return (env, False, f"{file_path}: {e}")

def find_environments_with_config(config_path):
    envs = []
    for env_dir in pathlib.Path("iac").iterdir():
        if not env_dir.is_dir():
            continue
        config_file = env_dir / config_path / "config.json"
        if config_file.exists():
            envs.append(env_dir.name)
    return envs

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Component/instance path (e.g. serverless-site/strall-com)")
    args = parser.parse_args()

    environments = find_environments_with_config(args.config)

    if not environments:
        print(f"No config found under any environment for: {args.config}")
        sys.exit(1)

    for env in environments:
        result = validate_config_file(env, args.config)
        if result is None:
            continue
        env_name, is_valid, message = result
        if is_valid:
            print(f"[{env_name}] ✅ Valid JSON: {message}")
        else:
            print(f"[{env_name}] ❌ Invalid JSON: {message}")
            sys.exit(1)

if __name__ == "__main__":
    main()
