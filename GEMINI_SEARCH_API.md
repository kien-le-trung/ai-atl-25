# Gemini Search API

The Gemini Search API endpoint allows you to perform intelligent web searches using Google's Gemini AI with advanced thinking capabilities.

## Endpoint

```
POST /api/search/gemini
```

## Features

- **Web Search**: Gemini can search the web and gather information from URLs
- **Thinking Mode**: Uses advanced reasoning to analyze and synthesize information
- **Streaming Response**: Results are streamed in real-time for better UX
- **Customizable**: Adjust temperature and thinking budget parameters

## Request Format

```json
{
  "prompt": "Your search query or question",
  "temperature": 0.2,
  "thinking_budget": -1
}
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | - | The search query or question you want answered |
| `temperature` | float | No | 0.2 | Controls randomness (0.0-1.0). Lower = more focused |
| `thinking_budget` | integer | No | -1 | Thinking budget (-1 for unlimited) |

## Response

The endpoint returns a **streaming text response**. Content is streamed as it's generated.

**Content-Type**: `text/plain`

## Example Usage

### Using cURL

```bash
curl -X POST "http://localhost:8000/api/search/gemini" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Find contact information from these URLs: https://example.com/profile",
    "temperature": 0.2
  }'
```

### Using Python (requests)

```python
import requests

response = requests.post(
    "http://localhost:8000/api/search/gemini",
    json={
        "prompt": "What are the latest developments in AI?",
        "temperature": 0.2,
        "thinking_budget": -1
    },
    stream=True
)

for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
    if chunk:
        print(chunk, end='', flush=True)
```

### Using JavaScript (fetch)

```javascript
const response = await fetch('http://localhost:8000/api/search/gemini', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    prompt: 'Summarize the latest tech news',
    temperature: 0.2,
    thinking_budget: -1
  })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const chunk = decoder.decode(value);
  console.log(chunk);
}
```

## Health Check

Check if the search service is available:

```
GET /api/search/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "gemini_search",
  "capabilities": ["web_search", "thinking", "streaming"]
}
```

## Model Information

The API uses **Gemini 2.0 Flash Thinking Experimental** model, which provides:
- Fast response times
- Advanced reasoning capabilities
- Web search integration
- Thinking mode for complex queries

## Configuration

Ensure your `.env` file contains:
```
GOOGLE_API_KEY=your_api_key_here
# Or optionally:
GEMINI_API_KEY=your_api_key_here
```

The service will use `GEMINI_API_KEY` if available, otherwise falls back to `GOOGLE_API_KEY`.

## Error Handling

If an error occurs, it will be included in the streaming response:

```
Error: [Error message here]
```

Common errors:
- `Gemini client not initialized`: API key not configured
- `Search failed`: Issue with the Gemini API or network
- `404 NOT_FOUND`: Model not available

## Use Cases

1. **Information Gathering**: Find contact info, research topics, gather data
2. **URL Analysis**: Analyze and extract information from multiple URLs
3. **Fact Checking**: Verify information across multiple sources
4. **Research**: Get comprehensive answers with citations
5. **Summarization**: Summarize content from web pages

## Notes

- The API uses streaming to provide real-time responses
- Responses are generated as the model thinks through the problem
- Temperature of 0.2 is recommended for factual queries
- Higher temperatures (0.7-1.0) are better for creative tasks
