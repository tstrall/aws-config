#!/usr/bin/env python3

import json
import argparse
import boto3
import pathlib
import sys

def load_environment_config(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def get_account_id():
    return boto3.client("sts").get_caller_identity()["Account"]

def get_region():
    return boto3.Session().region_name

def write_environment_param(env_dict, param_name="/aws-config/environment"):
    ssm = boto3.client('ssm')
    print(f"📦 Writing parameter {param_name} to SSM Parameter Store...")
    ssm.put_parameter(
        Name=param_name,
        Value=json.dumps(env_dict, indent=None),
        Type='String',
        Overwrite=True,
        Tier='Standard'
    )
    print("✅ Parameter written successfully.")

def put_restrictive_policy(param_name="/aws-config/environment", allowed_role="OrgAdmin"):
    ssm = boto3.client("ssm")
    account_id = get_account_id()
    region = get_region()
    principal_arn = f"arn:aws:iam::{account_id}:role/{allowed_role}"

    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "DenyWritesToEnvironmentParamExceptOrgAdmin",
                "Effect": "Deny",
                "Action": [
                    "ssm:PutParameter",
                    "ssm:DeleteParameter"
                ],
                "Resource": "*",
                "Condition": {
                    "StringNotEquals": {
                        "aws:PrincipalArn": principal_arn
                    }
                }
            }
        ]
    }

    print(f"🔐 Applying restrictive policy to {param_name}...")
    ssm.put_resource_policy(
        ResourceArn=f"arn:aws:ssm:{region}:{account_id}:parameter{param_name}",
        Policy=json.dumps(policy)
    )
    print("✅ Policy applied successfully.")

def main():
    parser = argparse.ArgumentParser(description="Define or update the environment binding for an AWS account.")
    parser.add_argument("--env", required=True, help="Environment name (e.g. dev, prod)")
    parser.add_argument("--path", default="account_environments", help="Directory containing environment JSON files")
    parser.add_argument("--param-name", default="/aws-config/environment", help="Target SSM parameter name")
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
