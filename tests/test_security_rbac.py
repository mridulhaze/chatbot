import pytest
from backend.core.security import hash_password, verify_password, create_jwt_token, decode_jwt_token

def test_password_hashing():
    pwd = "secret_password_2026"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrong_password", hashed) is False

def test_jwt_token_flow():
    payload = {"user_id": 101, "username": "student1", "role": "USER"}
    token = create_jwt_token(payload, expires_in_minutes=60)
    assert isinstance(token, str)
    assert len(token.split(".")) == 3

    decoded = decode_jwt_token(token)
    assert decoded is not None
    assert decoded["username"] == "student1"
    assert decoded["role"] == "USER"
