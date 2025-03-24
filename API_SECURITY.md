# GraphQnA API Security

This document explains the security measures implemented for the GraphQnA API.

## API Key Authentication

The GraphQnA API uses API key authentication to protect the endpoints. This helps to:

1. Prevent unauthorized access to your knowledge base
2. Avoid abuse of your OpenAI API credits
3. Restrict access to sensitive company information

### How It Works

All API endpoints (except for the `/api/health` endpoint) require an API key to be included in the request headers:

```
x-api-key: your-api-key-here
```

### Configuration

The API key is configured in the `.env` file:

```
GRAPHQNA_API_KEY=your-api-key-here
```

### Case-Insensitive Comparison

The API performs case-insensitive comparison of API keys, so both the header name and the API key value itself are not case-sensitive:

- The header can be provided in any case (e.g., `x-api-key`, `X-API-Key`, etc.)
- The API key value will be compared case-insensitively, so `AbC123` and `abc123` are treated as the same key

This makes the API more robust and less prone to integration issues.

### Log Rotation

Security events are logged with automatic rotation:

- Security logs are stored in `logs/security.log`
- API logs are stored in `logs/api.log`
- Logs are rotated daily with 30-day retention for security logs and 14-day retention for API logs
- Each log entry includes timestamp, level, and detailed message

### Rate Limiting

The API includes basic rate limiting to prevent abuse:

- Default: 60 requests per minute per IP address
- Exceeding this limit returns a 429 (Too Many Requests) response
- This can be configured in the `server.py` file by adjusting the `requests_per_minute` parameter

### Security Logging

Security-related events are logged for monitoring purposes:

- Failed authentication attempts (with limited key information)
- Rate limiting events
- Missing API key configuration warnings
- Client IP addresses for traceability

### For Development

If you're running the API locally for development, you can:

1. Set the API key in your `.env` file
2. Include the API key in your requests using the `x-api-key` header
3. For testing, you can use the provided `test_api_key.py` script

### For Production

In a production environment, we recommend:

1. Using a strong, randomly generated API key (e.g., 32+ characters)
2. Rotating the API key periodically
3. Using HTTPS for all API communication
4. Considering additional security measures like IP restrictions
5. Setting up monitoring for failed authentication attempts
6. Ensuring log directories are properly secured and monitored

## Implementation Details

The API key authentication is implemented as a FastAPI dependency that checks the request headers for a valid API key. If the API key is missing or invalid, the request is rejected with a 403 Forbidden error.

The Slack bot automatically includes the API key in all requests to the API, so it works seamlessly with the security measures.

## Testing

You can test the API key authentication using the provided `test_api_key.py` script:

```bash
python test_api_key.py
```

This script will test:

- The health endpoint (no API key required)
- The info endpoint without an API key (should fail)
- The info endpoint with an API key (should succeed)
- Case-insensitive API key comparison
- The query endpoint with an API key (should return an answer)
- Optional rate limiting test
