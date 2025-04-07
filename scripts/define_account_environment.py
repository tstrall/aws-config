#!/usr/bin/env python3

import json
import argparse
import boto3
import pathlib
import sys

def load_environment_config(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def write_environment_param(env_dict, param_name="/iac-config/environment"):
    ssm = boto3.client('ssm')
    print(f"📦 Writing parameter {param_name} to SSM Parameter Store...")
    ssm.put_parameter(
        Name=param_name,
        Value=json.dumps(env_dict, indent=None),
        Type='String',
        Overwrite=True,
        Tier='Advanced'
    )
    print("✅ Parameter written successfully.")

def put_restrictive_policy(param_name="/iac-config/environment", allowed_role="OrgAdmin"):
    print("ℹ️ Skipping resource policy: SSM only supports GetParameter in resource-based policies.")
    print("🔐 Use IAM policies in the account to restrict PutParameter access instead.")

def main():
    parser = argparse.ArgumentParser(description="Define or update the environment binding for an AWS account.")
    parser.add_argument("--env", required=True, help="Environment name (e.g. dev, prod)")
    parser.add_argument("--path", default="account-environments", help="Directory containing environment JSON files")
    parser.add_argument("--param-name", default="/iac-config/environment", help="Target SSM parameter name")
    parser.add_argument("--allow-role", default="OrgAdmin", help="IAM role allowed to write/delete this param")
    parser.add_argument("--skip-policy", action="store_true", help="Skip attaching restrictive resource policy")
    args = parser.parse_args()

    env_file = pathlib.Path(args.path) / f"{args.env}.json"
    if not env_file.exists():
        print(f"❌ File not found: {env_file}")
        sys.exit(1)

    print(f"📄 Loading config from: {env_file}")
    env_config = load_environment_config(env_file)

    write_environment_param(env_config, args.param_name)

    if not args.skip_policy:
        put_restrictive_policy(args.param_name, allowed_role=args.allow_role)

if __name__ == "__main__":
    main()
