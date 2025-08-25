# Authentication API

This document describes the authentication endpoints for generating and validating JWT tokens.

## Endpoints

### Generate JWT Token

**POST** `/dmcp/auth`

Generates a new JWT token with a dynamic payload provided in the request.

#### Request Body

```json
{
  "payload": {
    "user_id": 123,
    "username": "testuser",
    "role": "admin",
    "custom_field": "custom_value"
  }
}
```

The `payload` field can contain any JSON object with the data you want to include in the JWT token.

#### Response

```json
{
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in_minutes": 60
  },
  "success": true,
  "errors": [],
  "warnings": []
}
```

#### Example Usage

```bash
curl -X POST "http://localhost:8000/dmcp/auth" \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "user_id": 123,
      "username": "testuser",
      "role": "admin"
    }
  }'
```

### Validate JWT Token

**POST** `/dmcp/auth/validate`

Validates a JWT token and returns its decoded payload.

#### Headers

- `Authorization`: Bearer token (e.g., `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`)

#### Response

```json
{
  "data": {
    "payload": {
      "user_id": 123,
      "username": "testuser",
      "role": "admin",
      "custom_field": "custom_value",
      "exp": 1640995200,
      "iat": 1640991600
    },
    "valid": true
  },
  "success": true,
  "errors": [],
  "warnings": []
}
```

#### Example Usage

```bash
curl -X POST "http://localhost:8000/dmcp/auth/validate" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json"
```

## Configuration

The JWT token generation uses the following configuration from your environment:

- `JWT_SECRET_KEY`: Secret key for signing tokens
- `JWT_ALGORITHM`: Algorithm used for signing (default: HS256)
- `JWT_EXPIRATION_MINUTES`: Token expiration time in minutes (default: 60)

## Error Responses

### Missing Authorization Header

```json
{
  "data": null,
  "success": false,
  "errors": [
    {
      "msg": "Authorization header is required"
    }
  ],
  "warnings": []
}
```

### Invalid Token

```json
{
  "data": null,
  "success": false,
  "errors": [
    {
      "msg": "Authentication failed: Invalid token"
    }
  ],
  "warnings": []
}
```

### Expired Token

```json
{
  "data": null,
  "success": false,
  "errors": [
    {
      "msg": "Authentication failed: Token has expired"
    }
  ],
  "warnings": []
}
```

## Security Notes

1. **Token Expiration**: Tokens automatically expire after the configured time period
2. **Payload Validation**: The endpoint accepts any JSON payload, so validate your data before sending
3. **Secret Key**: Ensure your `JWT_SECRET_KEY` is secure and unique in production
4. **HTTPS**: Use HTTPS in production to protect token transmission

## Testing

You can test the endpoints using the provided Bruno API files:

- `generate_token.bru`: Test token generation
- `validate_token.bru`: Test token validation

Or use the Python test script:

```bash
python test_auth_endpoint.py
``` 