# tests/test_security.py
import pytest
from App.fastapi_app.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from datetime import timedelta

def test_hash_password():
    password = "mysecretpassword"
    hashed = hash_password(password)
    
    assert hashed != password
    assert isinstance(hashed, str)
    assert len(hashed) > 0
    # Should be different due to salt
    assert hash_password(password) != hash_password(password)

def test_verify_password():
    password = "mysecretpassword"
    wrong_password = "wrongpassword"
    hashed = hash_password(password)
    
    assert verify_password(password, hashed) is True
    assert verify_password(wrong_password, hashed) is False

def test_create_access_token():
    data = {"sub": "testuser"}
    token = create_access_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token.split(".")) == 3 # JWT format: header.payload.signature

def test_decode_token_valid():
    data = {"sub": "testuser"}
    token = create_access_token(data)
    
    payload = decode_token(token)
    assert payload is not None
    assert payload.get("sub") == "testuser"
    assert "exp" in payload

def test_decode_token_invalid():
    invalid_token = "invalid.token.string"
    payload = decode_token(invalid_token)
    
    assert payload is None

def test_decode_token_expired():
    data = {"sub": "testuser"}
    # Create token that expired 1 minute ago
    token = create_access_token(data, expires_delta=timedelta(minutes=-1))
    
    payload = decode_token(token)
    # python-jose returns None for expired tokens if caught in our standard except JWTError block
    assert payload is None
