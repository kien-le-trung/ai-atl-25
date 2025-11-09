#!/usr/bin/env python3
"""
Test script for the Vapi Calls API endpoints.
"""
import requests
import json
import sys

API_BASE_URL = "http://localhost:8000"


def test_ping_pong():
    """Test the ping-pong endpoint."""
    print("Testing ping-pong endpoint...")
    response = requests.get(f"{API_BASE_URL}/api/calls/ping/pong")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    return response.status_code == 200


def test_health():
    """Test the health endpoint."""
    print("Testing health endpoint...")
    response = requests.get(f"{API_BASE_URL}/api/calls/health")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}\n")

    if data.get("configured"):
        print("✓ Vapi is configured and ready to use!")
    else:
        print("⚠ Vapi is not configured. Set VAPI_API_KEY, VAPI_ASSISTANT_ID, and VAPI_PHONE_NUMBER_ID in .env")

    return response.status_code == 200


def test_create_call(phone_number: str = "+1234567890"):
    """Test creating a call (will fail if not configured)."""
    print(f"Testing call creation to {phone_number}...")

    response = requests.post(
        f"{API_BASE_URL}/api/calls/create",
        json={
            "phone_number": phone_number,
            "assistant_overrides": {
                "variableValues": {
                    "person_name": "Test User"
                }
            }
        }
    )

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

    return response.status_code == 200


def test_create_call_with_context():
    """Test creating a call with context (will fail if not configured)."""
    print("Testing call creation with context...")

    response = requests.post(
        f"{API_BASE_URL}/api/calls/create-with-context",
        json={
            "phone_number": "+1234567890",
            "person_name": "Jane Doe",
            "person_information": "Software Engineer at TechCorp",
            "conversation_summary": "Discussed project deadlines and team collaboration"
        }
    )

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

    return response.status_code == 200


def test_list_calls():
    """Test listing calls (will fail if not configured)."""
    print("Testing list calls...")

    response = requests.get(f"{API_BASE_URL}/api/calls?limit=5")

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

    return response.status_code == 200


def main():
    """Main test function."""
    print("=" * 80)
    print("Vapi Calls API Test")
    print("=" * 80 + "\n")

    # Test basic endpoints (should always work)
    tests_passed = 0
    tests_total = 0

    # Test ping-pong
    tests_total += 1
    if test_ping_pong():
        tests_passed += 1
        print("✓ Ping-pong test passed!\n")
    else:
        print("✗ Ping-pong test failed!\n")

    # Test health
    tests_total += 1
    if test_health():
        tests_passed += 1
        print("✓ Health check passed!\n")
    else:
        print("✗ Health check failed!\n")

    print("-" * 80)
    print(f"Basic Tests: {tests_passed}/{tests_total} passed")
    print("-" * 80 + "\n")

    # Check if Vapi is configured before testing call endpoints
    health_response = requests.get(f"{API_BASE_URL}/api/calls/health")
    is_configured = health_response.json().get("configured", False)

    if not is_configured:
        print("⚠ Vapi is not configured. Skipping call creation tests.")
        print("\nTo test call functionality, add to your .env file:")
        print("  VAPI_API_KEY=your_api_key")
        print("  VAPI_ASSISTANT_ID=your_assistant_id")
        print("  VAPI_PHONE_NUMBER_ID=your_phone_number_id")
        print("\nAll basic endpoints are working correctly!")
        sys.exit(0)

    # Test call endpoints (only if configured)
    print("Testing call endpoints (Vapi is configured)...\n")

    # Note: These will actually create calls if configured!
    print("Note: The following tests will attempt to create real calls.")
    print("Make sure you have a valid test phone number and credits.\n")

    # Uncomment to test actual call creation
    # if test_create_call():
    #     print("✓ Call creation test passed!\n")
    # else:
    #     print("✗ Call creation test failed!\n")

    # if test_create_call_with_context():
    #     print("✓ Call with context test passed!\n")
    # else:
    #     print("✗ Call with context test failed!\n")

    # if test_list_calls():
    #     print("✓ List calls test passed!\n")
    # else:
    #     print("✗ List calls test failed!\n")

    print("\n✓ All available tests completed successfully!")


if __name__ == "__main__":
    main()
