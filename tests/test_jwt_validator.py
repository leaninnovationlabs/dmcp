"""Tests for JWT validator functionality."""

import pytest
from datetime import datetime, timedelta, timezone
from app.core.jwt_validator import JWTValidator, jwt_validator
from app.core.exceptions import AuthenticationError


class TestJWTValidator:
    """Test cases for JWT validator."""
    
    def test_create_token(self):
        """Test JWT token creation."""
        validator = JWTValidator()
        payload = {"user_id": 123, "username": "testuser"}
        
        token = validator.create_token(payload)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verify token can be decoded
        decoded = validator.validate_token(token)
        assert decoded["user_id"] == 123
        assert decoded["username"] == "testuser"
        assert "exp" in decoded
        assert "iat" in decoded
    
    def test_validate_valid_token(self):
        """Test validation of a valid token."""
        validator = JWTValidator()
        payload = {"user_id": 456, "role": "admin"}
        
        token = validator.create_token(payload)
        decoded = validator.validate_token(token)
        
        assert decoded["user_id"] == 456
        assert decoded["role"] == "admin"
    
    def test_validate_token_with_bearer_prefix(self):
        """Test validation of token with Bearer prefix."""
        validator = JWTValidator()
        payload = {"user_id": 789}
        
        token = validator.create_token(payload)
        bearer_token = f"Bearer {token}"
        
        decoded = validator.validate_token(bearer_token)
        assert decoded["user_id"] == 789
    
    def test_validate_invalid_token(self):
        """Test validation of invalid token."""
        validator = JWTValidator()
        
        with pytest.raises(AuthenticationError, match="Invalid token"):
            validator.validate_token("invalid.token.here")
    
    def test_validate_malformed_token(self):
        """Test validation of malformed token."""
        validator = JWTValidator()
        
        with pytest.raises(AuthenticationError, match="Invalid token"):
            validator.validate_token("not-a-jwt-token")
    
    def test_is_token_valid_with_valid_token(self):
        """Test is_token_valid with valid token."""
        validator = JWTValidator()
        payload = {"user_id": 123}
        
        token = validator.create_token(payload)
        
        assert validator.is_token_valid(token) is True
    
    def test_is_token_valid_with_invalid_token(self):
        """Test is_token_valid with invalid token."""
        validator = JWTValidator()
        
        assert validator.is_token_valid("invalid.token") is False
    
    def test_get_token_payload(self):
        """Test getting token payload without validation."""
        validator = JWTValidator()
        payload = {"user_id": 999, "data": "test"}
        
        token = validator.create_token(payload)
        retrieved_payload = validator.get_token_payload(token)
        
        assert retrieved_payload is not None
        assert retrieved_payload["user_id"] == 999
        assert retrieved_payload["data"] == "test"
    
    def test_get_token_payload_with_bearer_prefix(self):
        """Test getting token payload with Bearer prefix."""
        validator = JWTValidator()
        payload = {"user_id": 888}
        
        token = validator.create_token(payload)
        bearer_token = f"Bearer {token}"
        retrieved_payload = validator.get_token_payload(bearer_token)
        
        assert retrieved_payload is not None
        assert retrieved_payload["user_id"] == 888
    
    def test_get_token_payload_invalid_token(self):
        """Test getting payload from invalid token."""
        validator = JWTValidator()
        
        payload = validator.get_token_payload("invalid.token")
        assert payload is None
    
    def test_global_jwt_validator_instance(self):
        """Test that global JWT validator instance works."""
        payload = {"test": "global_instance"}
        
        token = jwt_validator.create_token(payload)
        decoded = jwt_validator.validate_token(token)
        
        assert decoded["test"] == "global_instance" 