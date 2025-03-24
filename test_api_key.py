#!/usr/bin/env python3
"""Test script to verify API key implementation."""

import json
import os
import time

import requests
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Get the API key from environment
API_KEY = os.getenv("GRAPHQNA_API_KEY")
print(f"API Key: {API_KEY[:5]}..." if API_KEY else "API Key not found")

# Test API endpoints
BASE_URL = "http://localhost:8000"


def test_health_endpoint():
    """Test the health endpoint (should be accessible without API key)."""
    url = f"{BASE_URL}/api/health"
    response = requests.get(url)
    print(f"Health endpoint status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_info_endpoint_without_key():
    """Test the info endpoint without API key (should fail)."""
    url = f"{BASE_URL}/api/info"
    response = requests.get(url)
    print(f"Info endpoint without key status: {response.status_code}")
    print(f"Response: {response.text}")


def test_info_endpoint_with_key():
    """Test the info endpoint with API key (should succeed)."""
    url = f"{BASE_URL}/api/info"
    headers = {"x-api-key": API_KEY}
    response = requests.get(url, headers=headers)
    print(f"Info endpoint with key status: {response.status_code}")
    print(
        f"Response: {json.dumps(response.json(), indent=2) if response.status_code == 200 else response.text}"
    )


def test_info_endpoint_uppercase_header():
    """Test case-insensitive header handling with uppercase API key value."""
    url = f"{BASE_URL}/api/info"
    headers = {"x-api-key": API_KEY.upper() if API_KEY else "INVALID_KEY"}
    response = requests.get(url, headers=headers)
    print(f"Info endpoint with uppercase key value status: {response.status_code}")
    print(
        f"Response: {json.dumps(response.json(), indent=2) if response.status_code == 200 else response.text}"
    )


def test_query_endpoint_with_key():
    """Test the query endpoint with API key."""
    url = f"{BASE_URL}/api/query"
    headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
    data = {"query": "What is Hero by Vivun?", "retrieval_method": "graphrag"}
    response = requests.post(url, headers=headers, json=data)
    print(f"Query endpoint with key status: {response.status_code}")
    if response.status_code == 200:
        print(f"Answer: {response.json().get('answer', 'No answer')}")
    else:
        print(f"Response: {response.text}")


def test_rate_limiting():
    """Test rate limiting by making many requests quickly."""
    url = f"{BASE_URL}/api/info"
    headers = {"x-api-key": API_KEY}

    print("Testing rate limiting (sending 70 requests quickly)...")
    responses = []

    for i in range(70):  # Default limit is 60 per minute
        response = requests.get(url, headers=headers)
        responses.append(response.status_code)
        time.sleep(0.05)  # Small delay to avoid overwhelming the server

    # Count response codes
    success_count = responses.count(200)
    rate_limited_count = responses.count(429)

    print(f"Successful responses: {success_count}")
    print(f"Rate limited responses: {rate_limited_count}")

    if rate_limited_count > 0:
        print("✅ Rate limiting is working")
    else:
        print("❌ Rate limiting did not trigger as expected")


if __name__ == "__main__":
    print("Testing API Key Authentication")
    print("-" * 50)
    test_health_endpoint()
    print("-" * 50)
    test_info_endpoint_without_key()
    print("-" * 50)
    test_info_endpoint_with_key()
    print("-" * 50)
    test_info_endpoint_uppercase_header()
    print("-" * 50)
    test_query_endpoint_with_key()
    print("-" * 50)

    # Rate limiting test is optional and may cause temporary rate limiting for your IP
    run_rate_limit_test = input("Run rate limiting test? (y/n): ").lower() == "y"
    if run_rate_limit_test:
        print("-" * 50)
        test_rate_limiting()
