#!/usr/bin/env python3

import boto3
import argparse
import sys
import json
from typing import Dict, List, Union
from botocore.exceptions import ClientError


def get_parameter_value(parameter_name: str) -> str:
    try:
        ssm_client = boto3.client('ssm')
        response = ssm_client.get_parameter(
            Name=parameter_name,
            WithDecryption=True
        )
        return response['Parameter']['Value']
    except ClientError as e:
        print(f"Error getting parameter {parameter_name}: {e}")
        return f"ERROR_FETCHING_PARAMETER_{parameter_name}"


def get_secret_value(secret_arn: str) -> str:

    try:
        secrets_client = boto3.client('secretsmanager')
        response = secrets_client.get_secret_value(
            SecretId=secret_arn
        )
        
        if 'SecretBinary' in response:
            return base64.b64decode(response['SecretBinary'])
        
        secret = response['SecretString']
        
        try:
            secret_dict = json.loads(secret)
            return secret if isinstance(secret_dict, dict) else secret_dict
        except json.JSONDecodeError:
            return secret
            
    except ClientError as e:
        print(f"Error getting secret {secret_arn}: {e}")
        return f"ERROR_FETCHING_SECRET_{secret_arn}"


def resolve_value_from(value_from: str) -> str:

    if value_from.startswith('arn:aws:ssm'):
        parameter_name = value_from.split(':parameter')[-1]
        return get_parameter_value(parameter_name)
    elif value_from.startswith('arn:aws:secretsmanager'):
        return get_secret_value(value_from)
    else:
        print(f"Warning: Unsupported valueFrom reference: {value_from}")
        return f"UNSUPPORTED_VALUE_FROM_{value_from}"


def get_task_definition_envs(task_definition_arn: str, container_name: str) -> List[Dict[str, str]]:

    try:
        ecs_client = boto3.client('ecs')
        
        response = ecs_client.describe_task_definition(
            taskDefinition=task_definition_arn
        )
        
        containers = response['taskDefinition']['containerDefinitions']
        target_container = None
        
        for container in containers:
            if container['name'] == container_name:
                target_container = container
                break
        
        if not target_container:
            print(f"Error: Container '{container_name}' not found in task definition")
            sys.exit(1)
            
        env_vars = []
        
        if 'environment' in target_container:
            env_vars.extend(target_container['environment'])
            
        # Process environment variables with valueFrom
        if 'secrets' in target_container:
            for secret in target_container['secrets']:
                name = secret.get('name', '')
                value_from = secret.get('valueFrom', '')
                if name and value_from:
                    resolved_value = resolve_value_from(value_from)
                    env_vars.append({
                        'name': name,
                        'value': resolved_value
                    })
        
        return env_vars
        
    except ClientError as e:
        print(f"AWS Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def generate_env_file(env_vars: List[Dict[str, str]], output_file: str = '.env'):

    try:
        with open(output_file, 'w') as f:
            for env in env_vars:
                name = env.get('name', '')
                value = env.get('value', '')
                if name and value:
                    # escape the value if it contains special characters
                    if any(c in str(value) for c in [' ', '\n', '#', '"', "'"]):
                        value = f'"{str(value).replace('"', '\\"')}"'
                    f.write(f"{name}={value}\n")
        print(f"Successfully generated {output_file}")
    except Exception as e:
        print(f"Error generating .env file: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Extract environment variables from ECS task definition'
    )
    parser.add_argument(
        '--task-definition',
        required=True,
        help='The ARN of the task definition'
    )
    parser.add_argument(
        '--container-name',
        required=True,
        help='The name of the container'
    )
    parser.add_argument(
        '--output',
        default='.env',
        help='Output file name (default: .env)'
    )
    
    args = parser.parse_args()
    
    env_vars = get_task_definition_envs(args.task_definition, args.container_name)

    generate_env_file(env_vars, args.output)


if __name__ == '__main__':
    main() 