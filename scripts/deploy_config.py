#!/usr/bin/env python3

import argparse
import tempfile
import subprocess
import os
import json
import boto3
import pathlib
import sys
from botocore.exceptions import ClientError

def get_identity():
    sts = boto3.client("sts")
    ident = sts.get_caller_identity()
    return {
        "account_id": ident["Account"],
        "arn": ident["Arn"]
    }

def get_environment_config(param_name="/iac-config/environment", required=True):
    ssm = boto3.client('ssm')
    try:
        response = ssm.get_parameter(Name=param_name, WithDecryption=False)
    except ClientError as e:
        if e.response['Error']['Code'] == 'ParameterNotFound':
            if required:
                print(f"❌ Required parameter {param_name} is not set. Please run the environment bootstrap script first.")
                sys.exit(1)
            else:
                return None
        else:
            raise
    try:
        return json.loads(response['Parameter']['Value'])
    except json.JSONDecodeError:
        print(f"❌ Parameter {param_name} is not valid JSON.")
        sys.exit(1)

def clone_repo(repo_url, branch):
    temp_dir = tempfile.mkdtemp()
    subprocess.run(["git", "clone", "--depth", "1", "--branch", branch, repo_url, temp_dir], check=True)
    return pathlib.Path(temp_dir)

def load_config_instance(base_path, environment, config_path):
    config_file = base_path / environment / config_path / "config.json"
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")
    with open(config_file, "r") as f:
        return json.load(f)

def deploy_config(config):
    print(f"\n⚙️  [DRY RUN] Would deploy config instance:")
    print(json.dumps(config, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Deploy a config instance defined in aws-config.")
    parser.add_argument("--config", required=True, help="Path to the config instance (e.g. serverless-site/strall-com)")
    parser.add_argument("--config-param", default="/iac-config/environment", help="SSM parameter name for environment binding")
    parser.add_argument("--override-config-repo", help="Optional override for config repo")
    parser.add_argument("--override-config-branch", help="Optional override for config branch")
    parser.add_argument("--require-param", action="store_true", default=True, help="Fail if config param is missing (default: true)")
    args = parser.parse_args()

    ident = get_identity()
    print(f"👤 Running as: {ident['arn']}")
    print(f"🧾 AWS Account ID: {ident['account_id']}")

    env = get_environment_config(args.config_param, required=args.require_param)
    if env is None:
        print("⚠️  No environment config loaded. Skipping deployment.")
        sys.exit(0)

    environment_name = env["name"]
    config_repo = args.override_config_repo or env["config_repo"]
    config_branch = args.override_config_branch or env["config_branch"]

    print(f"\n📦 Using config repo: {config_repo}")
    print(f"🌱 Branch: {config_branch}")
    print(f"🏷️  Environment: {environment_name}")

    repo_path = clone_repo(config_repo, config_branch)
    config_instance = load_config_instance(repo_path, environment_name, args.config)

    deploy_config(config_instance)

if __name__ == "__main__":
    main()
