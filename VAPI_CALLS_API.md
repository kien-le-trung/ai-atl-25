# Vapi Calls API Documentation

The Vapi Calls API provides endpoints for making AI-powered outbound phone calls using Vapi's voice AI assistant.

## Overview

**Service**: Vapi Voice AI Calls
**Base Path**: `/api/calls`
**Capabilities**: Outbound calls, AI assistant, Transcription

## Configuration

Add the following to your `.env` file:

```env
VAPI_API_KEY=your_vapi_api_key
VAPI_ASSISTANT_ID=your_assistant_id
VAPI_PHONE_NUMBER_ID=your_phone_number_id
```

Get your credentials from [Vapi.ai Dashboard](https://vapi.ai)

---

## Endpoints

### 1. Ping-Pong (Test Endpoint)

**GET** `/api/calls/ping/pong`

Simple ping-pong endpoint to verify the API is working.

**Response:**
```json
{
  "ping": "pong",
  "service": "vapi_calls",
  "status": "active"
}
```

**Example:**
```bash
curl http://localhost:8000/api/calls/ping/pong
```

---

### 2. Health Check

**GET** `/api/calls/health`

Check if the Vapi service is configured and ready.

**Response:**
```json
{
  "status": "healthy",
  "service": "vapi_calls",
  "configured": true,
  "capabilities": [
    "outbound_calls",
    "ai_assistant",
    "transcription"
  ]
}
```

**Status Values:**
- `healthy` - Vapi is configured and ready
- `unconfigured` - Missing API credentials

**Example:**
```bash
curl http://localhost:8000/api/calls/health
```

---

### 3. Create Call

**POST** `/api/calls/create`

Create and initiate a new AI voice call.

**Request Body:**
```json
{
  "phone_number": "+1234567890",
  "assistant_overrides": {
    "variableValues": {
      "person_name": "John Doe",
      "custom_variable": "value"
    }
  }
}
```

**Parameters:**
- `phone_number` (required) - Phone number in E.164 format (e.g., +1234567890)
- `assistant_overrides` (optional) - Custom variables for the AI assistant

**Response:**
```json
{
  "success": true,
  "message": "Call initiated successfully",
  "data": {
    "id": "call_abc123def456",
    "status": "initiated",
    "phone_number": "+1234567890",
    "assistant_id": "asst_xyz789"
  }
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/calls/create" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1234567890",
    "assistant_overrides": {
      "variableValues": {
        "person_name": "Alice"
      }
    }
  }'
```

---

### 4. Create Call with Context

**POST** `/api/calls/create-with-context`

Create a call with personalized conversation context.

**Request Body:**
```json
{
  "phone_number": "+1234567890",
  "person_name": "Jane Smith",
  "person_information": "Software Engineer at TechCorp",
  "conversation_summary": "Discussed project timelines and deliverables last week"
}
```

**Parameters:**
- `phone_number` (required) - Phone number in E.164 format
- `person_name` (required) - Name of the person being called
- `person_information` (optional) - Background info about the person
- `conversation_summary` (optional) - Summary of previous conversations

**Response:**
```json
{
  "success": true,
  "message": "Call to Jane Smith initiated successfully",
  "data": {
    "id": "call_abc123def456",
    "status": "initiated",
    "phone_number": "+1234567890",
    "assistant_id": "asst_xyz789"
  }
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/calls/create-with-context" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1234567890",
    "person_name": "Bob Johnson",
    "person_information": "CTO at StartupXYZ",
    "conversation_summary": "Previously discussed scaling infrastructure"
  }'
```

---

### 5. Get Call Details

**GET** `/api/calls/{call_id}`

Retrieve details and transcript of a specific call.

**Path Parameters:**
- `call_id` - The Vapi call ID

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "call_abc123def456",
    "status": "completed",
    "transcript": "Full conversation transcript here...",
    "duration": 120.5,
    "started_at": "2025-11-08T10:30:00Z",
    "ended_at": "2025-11-08T10:32:00Z",
    "cost": 0.25,
    "metadata": { }
  }
}
```

**Call Status Values:**
- `initiated` - Call is being connected
- `ringing` - Phone is ringing
- `in-progress` - Call is active
- `completed` - Call finished successfully
- `failed` - Call failed
- `no-answer` - No one answered
- `busy` - Line was busy

**Example:**
```bash
curl http://localhost:8000/api/calls/call_abc123def456
```

---

### 6. List Calls

**GET** `/api/calls?limit=10`

List recent calls.

**Query Parameters:**
- `limit` (optional) - Number of calls to return (1-100, default: 10)

**Response:**
```json
{
  "success": true,
  "data": {
    "calls": [
      {
        "id": "call_abc123",
        "status": "completed",
        "createdAt": "2025-11-08T10:30:00Z"
      }
    ],
    "count": 1
  }
}
```

**Example:**
```bash
curl "http://localhost:8000/api/calls?limit=20"
```

---

## Integration with Conversation System

You can integrate Vapi calls with the conversation partner system:

### Example: Call a Conversation Partner

```python
import requests

# 1. Get partner information
partner = requests.get("http://localhost:8000/api/partners/1").json()

# 2. Get recent conversation summary
conversations = requests.get(
    f"http://localhost:8000/api/conversations?partner_id={partner['id']}"
).json()

# 3. Create call with context
call_response = requests.post(
    "http://localhost:8000/api/calls/create-with-context",
    json={
        "phone_number": partner["phone"],
        "person_name": partner["name"],
        "person_information": partner.get("notes", ""),
        "conversation_summary": conversations[0].get("summary", "") if conversations else ""
    }
)

# 4. Get call ID
call_id = call_response.json()["data"]["id"]

# 5. Wait for call to complete, then get transcript
import time
time.sleep(60)  # Wait for call

transcript_response = requests.get(f"http://localhost:8000/api/calls/{call_id}")
transcript = transcript_response.json()["data"]["transcript"]

print(f"Call transcript: {transcript}")
```

---

## Error Handling

### Common Errors

**400 Bad Request**
```json
{
  "detail": "Phone number must be in E.164 format (e.g., +1234567890)"
}
```

**500 Internal Server Error**
```json
{
  "detail": "Failed to create call: Vapi is not configured. Please set VAPI_API_KEY..."
}
```

### Error Codes

| Status Code | Meaning |
|------------|---------|
| 200 | Success |
| 400 | Bad request (invalid phone number, etc.) |
| 500 | Server error (not configured, API error, etc.) |

---

## Phone Number Format

All phone numbers must be in **E.164 format**:

✅ **Correct:**
- `+1234567890` (US)
- `+447911123456` (UK)
- `+33612345678` (France)

❌ **Incorrect:**
- `1234567890` (missing +)
- `(123) 456-7890` (formatting)
- `001234567890` (wrong prefix)

---

## Assistant Variables

You can pass custom variables to your Vapi assistant:

```json
{
  "assistant_overrides": {
    "variableValues": {
      "person_name": "John Doe",
      "person_information": "Software Engineer at InnoTech",
      "conversation_summary": "Discussed scalability challenges",
      "custom_field": "any value"
    }
  }
}
```

These variables are available in your Vapi assistant prompt template.

---

## Rate Limiting

Vapi has rate limits based on your plan:
- Free tier: ~10 calls/day
- Paid plans: Higher limits

Check your Vapi dashboard for current limits.

---

## Cost Considerations

**Call Costs:**
- Typically $0.10-0.30 per minute
- Varies by destination country
- Check Vapi pricing for current rates

**Best Practices:**
- Test with short calls first
- Monitor usage in Vapi dashboard
- Set up billing alerts

---

## Testing

Run the test script:
```bash
cd backend
python3 test_calls_api.py
```

**Test Results:**
- ✓ Ping-pong endpoint
- ✓ Health check endpoint
- ⚠ Call creation (requires configuration)

---

## Webhook Integration (Future)

Vapi supports webhooks for call events. You can configure webhooks in your Vapi dashboard to:
- Receive call status updates
- Get transcripts in real-time
- Track call completion

---

## Service Architecture

```
┌─────────────┐
│  API Client │
└──────┬──────┘
       │ POST /api/calls/create
       ▼
┌──────────────────┐
│  calls.py        │ (FastAPI Router)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ vapi_service.py  │ (Business Logic)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Vapi Python SDK │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Vapi.ai API    │ (External Service)
└──────────────────┘
```

---

## Environment Variables Summary

```env
# Required for Vapi functionality
VAPI_API_KEY=your_api_key_here
VAPI_ASSISTANT_ID=your_assistant_id_here
VAPI_PHONE_NUMBER_ID=your_phone_number_id_here
```

---

## Quick Start

1. **Get Vapi Credentials**
   - Sign up at [vapi.ai](https://vapi.ai)
   - Create an assistant
   - Get your API key, assistant ID, and phone number ID

2. **Configure Environment**
   ```bash
   echo "VAPI_API_KEY=your_key" >> .env
   echo "VAPI_ASSISTANT_ID=your_id" >> .env
   echo "VAPI_PHONE_NUMBER_ID=your_phone_id" >> .env
   ```

3. **Test the API**
   ```bash
   curl http://localhost:8000/api/calls/health
   ```

4. **Make Your First Call**
   ```bash
   curl -X POST http://localhost:8000/api/calls/create \
     -H "Content-Type: application/json" \
     -d '{"phone_number": "+1234567890"}'
   ```

---

## Support

- **Vapi Documentation**: [docs.vapi.ai](https://docs.vapi.ai)
- **Vapi Dashboard**: [dashboard.vapi.ai](https://dashboard.vapi.ai)
- **API Issues**: Check server logs for detailed error messages

---

## Security Notes

- Never commit `.env` file with real credentials
- Use environment variables for all secrets
- Validate phone numbers before making calls
- Monitor usage to prevent abuse
- Consider implementing rate limiting for production
