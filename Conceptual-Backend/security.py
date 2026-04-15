import hmac
import hashlib
import logging

logger = logging.getLogger(__name__)

SECRET = "super_secret"

def generate_signature(payload: str, timestamp: str):
    try:
        logger.debug(f"Generating signature for timestamp={timestamp}")
        message = f"{timestamp}.{payload}".encode()
        signature = hmac.new(SECRET.encode(), message, hashlib.sha256).hexdigest()
        logger.debug(f"Signature generated successfully")
        return signature
    except Exception as e:
        logger.error(f"Error generating signature: {str(e)}", exc_info=True)
        raise

def verify_signature(payload: bytes, signature: str):
    try:
        logger.debug(f"Verifying signature...")
        expected = generate_signature(payload)
        is_valid = hmac.compare_digest(expected, signature)
        if not is_valid:
            logger.warning(f"Signature verification failed - potential security breach detected")
        else:
            logger.debug(f"Signature verified successfully")
        return is_valid
    except Exception as e:
        logger.error(f"Error verifying signature: {str(e)}", exc_info=True)
        raise