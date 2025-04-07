#!/usr/bin/env python3

import argparse
import tempfile
import subprocess
import json
import boto3
import pathlib
import sys

def get_environment_config(param_name="/aws-config/environment"):
    ssm = boto3.client("ssm")
    try:
        param = ssm.get_parameter(Name=param_name, WithDecryption=False)
        return json.loads(param['Parameter']['Value'])
    except Exception as e:
        print(f"❌ Failed to load environment config from SSM: {e}")
        sys.exit(1)

def clone_repo(repo_url, branch):
    tmp_dir = tempfile.mkdtemp()
    subprocess.run(["git", "clone", "--depth", "1", "--branch", branch, repo_url, tmp_dir], check=True)
    return pathlib.Path(tmp_dir)

def validate_config_exists(repo_path, env, config_path):
    config_file = repo_path / env / config_path / "config.json"
    if not config_file.exists():
        print(f"❌ Config file not found: {config_file}")
        return False
    try:
        with open(config_file) as f:
            json.load(f)
        print("✅ Config file is valid and parsable.")
        return True
    except json.JSONDecodeError:
        print(f"❌ Config file exists but contains invalid JSON: {config_file}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Validate config instance exists and is readable.")
    parser.add_argument("--config", required=True, help="Path to config instance (e.g. serverless-site/strall-com)")
    parser.add_argument("--param-name", default="/aws-config/environment", help="SSM parameter name with environment info")
    args = parser.parse_args()

    env_config = get_environment_config(args.param_name)
    repo = env_config["config_repo"]
    branch = env_config["config_branch"]
    env_name = env_config["name"]

    print(f"🔍 Validating config instance for env: {env_name}")
    repo_path = clone_repo(repo, branch)
    ok = validate_config_exists(repo_path, env_name, args.config)
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
