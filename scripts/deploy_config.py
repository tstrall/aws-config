#!/usr/bin/env python3

import argparse
import json
import pathlib
import boto3
import sys


def get_current_environment(param_name="/iac/environment"):
    ssm = boto3.client("ssm")
    try:
        response = ssm.get_parameter(Name=param_name, WithDecryption=False)
        param_value = json.loads(response["Parameter"]["Value"])
        env = param_value.get("name")
        if not env:
            print(f"Missing 'name' field in {param_name}")
            sys.exit(1)
        return env
    except Exception as e:
        print(f"Failed to load {param_name}: {e}")
        sys.exit(1)


def load_config(env, component, nickname):
    config_file = pathlib.Path("iac") / env / component / nickname / "config.json"
    if not config_file.exists():
        print(f"Missing config file: {config_file}")
        sys.exit(1)
    return json.loads(config_file.read_text())


def write_param(param_name, config_data):
    ssm = boto3.client("ssm")
    ssm.put_parameter(
        Name=param_name,
        Value=json.dumps(config_data, separators=(",", ":")),
        Type="String",
        Overwrite=True,
        Tier="Standard"
    )
    print(f"✅ Deployed config to {param_name}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--component", required=True, help="Component name (e.g. serverless-site)")
    parser.add_argument("--nickname", required=True, help="Nickname or instance name (e.g. strall-com)")
    args = parser.parse_args()

    env = get_current_environment()
    param_name = f"/iac/{args.component}/{args.nickname}/config"
    config = load_config(env, args.component, args.nickname)
    write_param(param_name, config)


if __name__ == "__main__":
    main()
