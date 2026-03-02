"""
Helper to load HuggingFace token from AWS Secrets Manager.
"""
import os
import json
import boto3
from botocore.exceptions import ClientError

def get_hf_token(secret_name="cc-eval-hf-token", region="us-east-1"):
    """
    Retrieve HuggingFace token from Secrets Manager.
    Falls back to environment variable if secret not found.
    """
    # Check if already set
    if "HF_TOKEN" in os.environ:
        return os.environ["HF_TOKEN"]
    
    # Try Secrets Manager
    try:
        client = boto3.client('secretsmanager', region_name=region)
        response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response['SecretString'])
        token = secret['HF_TOKEN']
        
        # Set in environment for transformers library
        os.environ["HF_TOKEN"] = token
        return token
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"Warning: Secret {secret_name} not found. Set HF_TOKEN manually.")
        else:
            print(f"Error retrieving secret: {e}")
        return None

def setup_hf_auth():
    """
    Setup HuggingFace authentication for model downloads.
    Call this at the start of notebooks/scripts.
    """
    token = get_hf_token()
    if token:
        print("✓ HuggingFace token loaded from Secrets Manager")
        return True
    else:
        print("✗ HuggingFace token not found. Gated models will fail.")
        return False
