#!/usr/bin/env python3
"""
Generate a JWT bearer token for API authentication.
This script creates a token using the current JWT secret key configuration.
"""

from app.core.jwt_validator import jwt_validator
from datetime import datetime

# Create a token payload
payload = {
    "user_id": "deployment_user", 
    "username": "deployment_service",
    "purpose": "deployment_auth",
    "generated_at": datetime.now().isoformat()
}

# Generate the token
token = jwt_validator.create_token(payload)

print("="*80)
print("JWT BEARER TOKEN GENERATED")
print("="*80)
print(f"Bearer {token}")
print("="*80)
print("This token is valid for {} minutes".format(jwt_validator.expiration_minutes))
print("Save this token securely - it will be used for API authentication.")
print("="*80)