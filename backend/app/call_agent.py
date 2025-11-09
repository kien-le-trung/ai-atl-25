from vapi import Vapi
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def invoke_call_agent(assistant_overrides):
  client = Vapi(token=os.environ["VAPI_API_KEY"])

  # Data you want the agent to use (whatever your prompt expects)
  # assistant_overrides = {
  #     "variableValues": {
  #         "person_name": "Ben",
  #         "person_information": "Software Engineer at InnoTech Solutions",
  #         "conversation_summary": "discussed scalability challenges with state channels in decentralized finance, sensor fusion optimization in autonomous vehicles, and migrating core ML pipelines from Python to Rust.",
  #     }
  # }

  resp = client.calls.create(
      assistant_id=os.environ["VAPI_ASSISTANT_ID"],
      phone_number_id=os.environ["VAPI_PHONE_NUMBER_ID"],
      customer={"number": "+19842910760"},
      assistant_overrides=assistant_overrides,
  )

  r = requests.get(
      f"https://api.vapi.ai/call/{resp.id}",
      headers={"Authorization": f"Bearer {os.environ["VAPI_API_KEY"]}"}, timeout=20
  )
  r.raise_for_status()
  call = r.json()
  print("Transcript:", call.get("transcript", ""))
  return call.get("transcript", "")