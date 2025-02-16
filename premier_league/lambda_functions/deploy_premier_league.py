import argparse
import os
import subprocess

import premier_league


def get_serverless_path():
    package_root = os.path.dirname(premier_league.__file__)
    return os.path.join(package_root, "lambda", "serverless.yml")


def deploy(aws_profile=None, region=None):
    serverless_path = get_serverless_path()
    command = ["serverless", "deploy", "--config", serverless_path]

    if aws_profile:
        command.extend(["--aws-profile", aws_profile])

    if region:
        command.extend(["--region", region])

    subprocess.run(command)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Deploy Premier League functions to AWS Lambda"
    )
    parser.add_argument("--aws-profile", help="AWS profile to use for deployment")
    parser.add_argument(
        "--region", help="AWS region to deploy to (e.g., us-east-1, eu-west-1)"
    )
    args = parser.parse_args()
    deploy(args.aws_profile, args.region)
