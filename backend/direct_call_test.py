#!/usr/bin/env python3
"""
Direct test of Vapi call (bypassing FastAPI server)
"""
import os
from dotenv import load_dotenv
from vapi_python import Vapi
import requests
import time

load_dotenv()

PHONE_NUMBER = "+14436367028"

def make_call():
    """Make a direct call using Vapi."""
    print("=" * 80)
    print(f"Making direct call to {PHONE_NUMBER}")
    print("=" * 80 + "\n")

    # Get credentials
    api_key = os.environ.get("VAPI_API_KEY")
    assistant_id = os.environ.get("VAPI_ASSISTANT_ID")
    phone_number_id = os.environ.get("VAPI_PHONE_NUMBER_ID")

    if not all([api_key, assistant_id, phone_number_id]):
        print("✗ Missing Vapi credentials in .env file")
        print(f"  VAPI_API_KEY: {'✓' if api_key else '✗'}")
        print(f"  VAPI_ASSISTANT_ID: {'✓' if assistant_id else '✗'}")
        print(f"  VAPI_PHONE_NUMBER_ID: {'✓' if phone_number_id else '✗'}")
        return

    print("✓ All credentials found")
    print(f"  API Key: {api_key[:20]}...")
    print(f"  Assistant ID: {assistant_id}")
    print(f"  Phone Number ID: {phone_number_id}\n")

    # Initialize Vapi client
    client = Vapi(token=api_key)

    # Create call with context
    assistant_overrides = {
        "variableValues": {
            "person_name": "Harjyot",
            "person_information": "Developer testing the Vapi integration",
            "conversation_summary": "Testing the AI conversation assistant with voice calls"
        }
    }

    print("Creating call...")
    try:
        resp = client.calls.create(
            assistant_id=assistant_id,
            phone_number_id=phone_number_id,
            customer={"number": PHONE_NUMBER},
            assistant_overrides=assistant_overrides
        )

        print(f"✓ Call created successfully!")
        print(f"Call ID: {resp.id}\n")

        # Wait for call to connect
        print("Waiting 15 seconds for call to connect...")
        time.sleep(15)

        # Get call details
        print("Retrieving call details...")
        r = requests.get(
            f"https://api.vapi.ai/call/{resp.id}",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=20
        )
        r.raise_for_status()
        call = r.json()

        print(f"\nCall Status: {call.get('status', 'unknown')}")
        print(f"Duration: {call.get('duration', 0)} seconds")

        transcript = call.get('transcript', '')
        if transcript:
            print(f"\nTranscript:\n{transcript}")
        else:
            print("\nTranscript: (not available yet - call may still be in progress)")

        print(f"\n✓ Test complete!")
        print(f"\nCall ID for reference: {resp.id}")
        print(f"You can check this call later in your Vapi dashboard")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    make_call()
