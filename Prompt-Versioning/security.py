import hmac
import hashlib

SECRET = "super_secret"

def generate_signature(payload: str, timestamp: str):
    message = f"{timestamp}.{payload}".encode()
    return hmac.new(SECRET.encode(), message, hashlib.sha256).hexdigest()

def verify_signature(payload: bytes, signature: str):
    expected = generate_signature(payload)
    return hmac.compare_digest(expected, signature)