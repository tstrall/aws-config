#!/usr/bin/env python3

import argparse
import boto3
import json
import sys

def read_param(name):
    ssm = boto3.client("ssm")
    try:
        response = ssm.get_parameter(Name=name, WithDecryption=False)
        value = response["Parameter"]["Value"]
        try:
            parsed = json.loads(value)
            print(json.dumps(parsed, indent=2))
        except json.JSONDecodeError:
            print(value)
    except ssm.exceptions.ParameterNotFound:
        print(f"❌ Parameter not found: {name}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error retrieving parameter: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="Parameter name (e.g. /iac/environment)")
    args = parser.parse_args()
    read_param(args.name)

if __name__ == "__main__":
    main()
