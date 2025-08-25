# Auth API Examples

## Generate JWT Token

### Basic Example

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

### Complex Payload Example

```bash
curl -X POST "http://localhost:8000/dmcp/auth" \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "user_id": 456,
      "username": "john_doe",
      "email": "john@example.com",
      "role": "user",
      "permissions": ["read", "write"],
      "metadata": {
        "department": "engineering",
        "location": "remote",
        "preferences": {
          "theme": "dark",
          "language": "en"
        }
      },
      "created_at": "2024-01-15T10:30:00Z"
    }
  }'
```

### Minimal Payload Example

```bash
curl -X POST "http://localhost:8000/dmcp/auth" \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "session_id": "abc123def456"
    }
  }'
```

## Validate JWT Token

### Valid Token Example

```bash
# First, generate a token
TOKEN=$(curl -s -X POST "http://localhost:8000/dmcp/auth" \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "user_id": 123,
      "username": "testuser"
    }
  }' | jq -r '.data.token')

# Then validate it
curl -X POST "http://localhost:8000/dmcp/auth/validate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### Invalid Token Example

```bash
curl -X POST "http://localhost:8000/dmcp/auth/validate" \
  -H "Authorization: Bearer invalid_token_here" \
  -H "Content-Type: application/json"
```

### Missing Authorization Header

```bash
curl -X POST "http://localhost:8000/dmcp/auth/validate" \
  -H "Content-Type: application/json"
```

## Complete Workflow Example

```bash
#!/bin/bash

# Step 1: Generate a token
echo "Generating JWT token..."
RESPONSE=$(curl -s -X POST "http://localhost:8000/dmcp/auth" \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "user_id": 789,
      "username": "alice",
      "role": "manager",
      "department": "sales"
    }
  }')

echo "Response: $RESPONSE"

# Extract token from response
TOKEN=$(echo $RESPONSE | jq -r '.data.token')
echo "Generated token: ${TOKEN:0:50}..."

# Step 2: Validate the token
echo -e "\nValidating token..."
VALIDATION_RESPONSE=$(curl -s -X POST "http://localhost:8000/dmcp/auth/validate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

echo "Validation response: $VALIDATION_RESPONSE"

# Step 3: Use token for authenticated request
echo -e "\nUsing token for authenticated request..."
AUTH_RESPONSE=$(curl -s -X GET "http://localhost:8000/dmcp/health" \
  -H "Authorization: Bearer $TOKEN")

echo "Authenticated request response: $AUTH_RESPONSE"
```

## Python Example

```python
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000/dmcp"

# Generate token
def generate_token(payload):
    response = requests.post(
        f"{BASE_URL}/auth",
        json={"payload": payload},
        headers={"Content-Type": "application/json"}
    )
    return response.json()

# Validate token
def validate_token(token):
    response = requests.post(
        f"{BASE_URL}/auth/validate",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    return response.json()

# Example usage
if __name__ == "__main__":
    # Generate token
    payload = {
        "user_id": 123,
        "username": "testuser",
        "role": "admin"
    }
    
    result = generate_token(payload)
    print("Token generation result:", json.dumps(result, indent=2))
    
    if result.get("success"):
        token = result["data"]["token"]
        
        # Validate token
        validation = validate_token(token)
        print("Token validation result:", json.dumps(validation, indent=2))
```

## JavaScript Example

```javascript
// Base URL
const BASE_URL = 'http://localhost:8000/dmcp';

// Generate token
async function generateToken(payload) {
    const response = await fetch(`${BASE_URL}/auth`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ payload })
    });
    return await response.json();
}

// Validate token
async function validateToken(token) {
    const response = await fetch(`${BASE_URL}/auth/validate`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        }
    });
    return await response.json();
}

// Example usage
async function main() {
    const payload = {
        user_id: 123,
        username: 'testuser',
        role: 'admin'
    };
    
    // Generate token
    const result = await generateToken(payload);
    console.log('Token generation result:', result);
    
    if (result.success) {
        const token = result.data.token;
        
        // Validate token
        const validation = await validateToken(token);
        console.log('Token validation result:', validation);
    }
}

main().catch(console.error);
``` 