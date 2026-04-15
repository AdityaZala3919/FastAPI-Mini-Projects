import hmac
import hashlib
import logging
import bcrypt
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_session
from models import User

logger = logging.getLogger(__name__)

SECRET = "super_secret"
JWT_SECRET_KEY = "super_secret"
ALGORITHM = "HS256"

security = HTTPBearer()

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
    
def hash_password(password: str) -> str:
    try:
        logger.debug(f"Hashing password")
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        logger.debug(f"Password hashed successfully")
        return hashed
    except Exception as e:
        logger.error(f"Error hashing password: {str(e)}", exc_info=True)
        raise

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        logger.debug(f"Verifying password")
        is_valid = bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
        if is_valid:
            logger.debug(f"Password verification successful")
        else:
            logger.warning(f"Password verification failed")
        return is_valid
    except Exception as e:
        logger.error(f"Error verifying password: {str(e)}", exc_info=True)
        raise

async def create_access_token(user_id: str):
    try:
        logger.debug(f"Creating access token for user_id={user_id}")
        payload = {
            "sub": user_id,
            "exp": datetime.now() + timedelta(hours=2)
        }
        token = jwt.encode(payload=payload, key=JWT_SECRET_KEY, algorithm=ALGORITHM)
        logger.info(f"Access token created successfully for user_id={user_id}")
        return token
    except Exception as e:
        logger.error(f"Error creating access token for user_id={user_id}: {str(e)}", exc_info=True)
        raise

async def decode_token(token: str):
    try:
        logger.debug(f"Decoding JWT token")
        decoded = jwt.decode(token, key=JWT_SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug(f"Token decoded successfully")
        return decoded
    except jwt.ExpiredSignatureError:
        logger.warning(f"Token has expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token provided: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Error decoding token: {str(e)}", exc_info=True)
        raise

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
):
    try:
        logger.debug(f"Extracting user from credentials")
        token = credentials.credentials
        
        payload = await decode_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            logger.warning(f"Invalid token payload - missing 'sub' claim")
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        logger.debug(f"Fetching user from database: user_id={user_id}")
        user = await session.scalar(select(User).where(User.id == user_id))
        
        if not user:
            logger.warning(f"User not found in database: user_id={user_id}")
            raise HTTPException(status_code=401, detail="User not found")
        
        logger.debug(f"User authenticated successfully: user_id={user_id}, username={user.username}")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}", exc_info=True)
        raise HTTPException(status_code=401, detail="Authentication failed")
    