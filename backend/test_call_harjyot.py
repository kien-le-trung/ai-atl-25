#!/usr/bin/env python3
"""
Test script to make a call to +14436367028
"""
import requests
import json
import time

API_BASE_URL = "http://localhost:8000"
PHONE_NUMBER = "+14436367028"

def test_call():
    """Make a test call."""
    print("=" * 80)
    print(f"Making test call to {PHONE_NUMBER}")
    print("=" * 80 + "\n")

    # Create call with context
    print("Creating call with context...")
    response = requests.post(
        f"{API_BASE_URL}/api/calls/create-with-context",
        json={
            "phone_number": PHONE_NUMBER,
            "person_name": "Harjyot",
            "person_information": "Developer testing the Vapi integration",
            "conversation_summary": "Testing the AI conversation assistant with voice calls"
        }
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}\n")

    if response.status_code == 200:
        call_data = response.json()
        if call_data.get("success"):
            call_id = call_data["data"]["id"]
            print(f"✓ Call created successfully!")
            print(f"Call ID: {call_id}\n")

            # Wait a bit for the call to connect
            print("Waiting 10 seconds for call to connect...")
            time.sleep(10)

            # Get call status
            print("Retrieving call details...")
            status_response = requests.get(f"{API_BASE_URL}/api/calls/{call_id}")
            print(f"Call Status:\n{json.dumps(status_response.json(), indent=2)}\n")

            print("✓ Test complete!")
            print(f"\nYou can check the full transcript later by running:")
            print(f"curl http://localhost:8000/api/calls/{call_id}")
        else:
            print("✗ Call creation failed")
    else:
        print("✗ Request failed")

if __name__ == "__main__":
    test_call()
