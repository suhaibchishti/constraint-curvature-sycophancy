#!/usr/bin/env python3
"""
Phase 4: Delete TGI endpoints and clean up.

Usage:
    python scripts/phase4_cleanup.py           # deletes both endpoints
    python scripts/phase4_cleanup.py --model llama
    python scripts/phase4_cleanup.py --model qwen
"""
import argparse, boto3

REGION = "us-east-1"
ENDPOINTS = {
    "llama": "phase4-llama-70b",
    "qwen":  "phase4-qwen-72b",
}


def delete_endpoint(sm_client, endpoint_name):
    try:
        sm_client.delete_endpoint(EndpointName=endpoint_name)
        print(f"✅ Deleted endpoint: {endpoint_name}")
    except sm_client.exceptions.ClientError as e:
        if "Could not find endpoint" in str(e):
            print(f"  {endpoint_name} — not found (already deleted)")
        else:
            raise

    # Also delete endpoint config
    try:
        sm_client.delete_endpoint_config(EndpointConfigName=endpoint_name)
        print(f"✅ Deleted endpoint config: {endpoint_name}")
    except Exception:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=["llama", "qwen"], help="Delete specific model only")
    args = parser.parse_args()

    sm = boto3.client("sagemaker", region_name=REGION)
    targets = [args.model] if args.model else list(ENDPOINTS.keys())

    for key in targets:
        delete_endpoint(sm, ENDPOINTS[key])

    print("\nDone. No more endpoint charges.")
