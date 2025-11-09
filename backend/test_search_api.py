#!/usr/bin/env python3
"""
Test script for the Gemini search API endpoint.
"""
import requests
import json
import sys

API_BASE_URL = "http://localhost:8000"


def test_search_health():
    """Test the search health endpoint."""
    print("Testing search health endpoint...")
    response = requests.get(f"{API_BASE_URL}/api/search/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    return response.status_code == 200


def test_gemini_search(prompt: str):
    """Test the Gemini search endpoint with streaming."""
    print(f"Testing Gemini search with prompt: '{prompt[:100]}...'\n")
    print("Streaming response:")
    print("-" * 80)

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/search/gemini",
            json={
                "prompt": prompt,
                "temperature": 0.2,
                "thinking_budget": -1
            },
            stream=True,
            timeout=60
        )

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.text)
            return False

        # Stream the response
        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
            if chunk:
                print(chunk, end='', flush=True)

        print("\n" + "-" * 80)
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Main test function."""
    print("=" * 80)
    print("Gemini Search API Test")
    print("=" * 80 + "\n")

    # Test health endpoint
    if not test_search_health():
        print("Health check failed!")
        sys.exit(1)

    # Test search with a simple prompt
    prompt = """
    Try to find the contact information of this person from these URLs:
    https://robertsonscholars.org/profiles/harjyot-singh-sahni/
    https://ousf.duke.edu/profile/harjyot-singh-sahni/
    https://www.linkedin.com/in/harjyotsahni
    """

    if test_gemini_search(prompt):
        print("\n✓ Search test completed successfully!")
    else:
        print("\n✗ Search test failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
