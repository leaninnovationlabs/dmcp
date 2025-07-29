from app.core.jwt_validator import jwt_validator

# Create a token
payload = {"user_id": 123, "username": "john_doe"}
token = jwt_validator.create_token(payload)
print(f"Token: {token}")