#!/usr/bin/env python3

import argparse
import json
import boto3
import pathlib
import sys

def fetch_param(param_name="/iac/environment"):
    ssm = boto3.client("ssm")
    result = ssm.get_parameter(Name=param_name, WithDecryption=False)
    return json.loads(result["Parameter"]["Value"])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", help="Expected environment name (e.g. dev)")
    parser.add_argument("--param-name", default="/iac/environment", help="Parameter Store path")
    args = parser.parse_args()

    live = fetch_param(args.param_name)
    env_name = args.env or live.get("name")

    expected_path = pathlib.Path("account_environments") / f"{env_name}.json"
    if not expected_path.exists():
        print(f"Missing local file: {expected_path}")
        sys.exit(1)

    with open(expected_path) as f:
        expected = json.load(f)

    if live == expected:
        print("✅ Environment parameter matches local file.")
    else:
        print("❌ Mismatch between environment parameter and local file.")
        print("Live value:", json.dumps(live, indent=2))
        print("Expected: ", json.dumps(expected, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()
