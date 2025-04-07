#!/usr/bin/env python3

import json
import argparse
import boto3
import pathlib
import sys

def load_local_env(path):
    with open(path, 'r') as f:
        return json.load(f)

def get_remote_env(param_name="/aws-config/environment"):
    ssm = boto3.client("ssm")
    response = ssm.get_parameter(Name=param_name, WithDecryption=False)
    return json.loads(response['Parameter']['Value'])

def compare(expected, actual):
    mismatches = []
    for key in expected:
        if expected[key] != actual.get(key):
            mismatches.append((key, expected[key], actual.get(key)))
    return mismatches

def main():
    parser = argparse.ArgumentParser(description="Validate that the live environment param matches the expected local JSON.")
    parser.add_argument("--env", required=True, help="Name of the environment (e.g. dev, prod)")
    parser.add_argument("--path", default="account_environments", help="Directory where local JSON files are stored")
    parser.add_argument("--param-name", default="/aws-config/environment", help="SSM parameter name to validate")
    args = parser.parse_args()

    local_path = pathlib.Path(args.path) / f"{args.env}.json"
    if not local_path.exists():
        print(f"❌ Local file not found: {local_path}")
        sys.exit(1)

    expected = load_local_env(local_path)
    actual = get_remote_env(args.param_name)

    mismatches = compare(expected, actual)
    if not mismatches:
        print("✅ Environment parameter matches local JSON.")
    else:
        print("❌ Mismatch detected:")
        for key, exp, act in mismatches:
            print(f" - {key}: expected {exp}, got {act}")
        sys.exit(1)

if __name__ == "__main__":
    main()
