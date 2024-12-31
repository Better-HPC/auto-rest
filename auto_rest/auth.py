import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

import jwt
from fastapi import HTTPException
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncEngine

# Generate a random secret key for encoding and decoding JWT tokens
SECRET_KEY = os.urandom(32).hex()
ALGORITHM = "HS256"
TOKEN_TIMEOUT = timedelta(hours=1)

# In-memory storage for tokens
TOKEN_STORE: Dict[str, Engine | AsyncEngine] = {}


def now() -> datetime:
    """Get the current UTC datetime."""

    return datetime.now(tz=timezone.utc)


def create_session(conn: Engine | AsyncEngine) -> str:
    """Create a new session token and map it to an open database connection.

    Args:
        conn: The database connection object (Engine or AsyncEngine).

    Returns:
        The encoded JWT token.
    """

    payload = {
        "username": conn.url.username,
        "created_at": now().isoformat()
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    TOKEN_STORE[token] = conn
    return token


def fetch_session(token: str) -> Optional[Engine | AsyncEngine]:
    """Fetch the database connection associated with a token.

    Args:
        token: The JWT token.

    Returns:
        The database connection if valid, else None.

    Raises:
        HTTPException: If the token is invalid or expired.
    """

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        created_at = datetime.fromisoformat(payload["created_at"])
        connection = TOKEN_STORE[token]

        # Clear out expired tokens
        if now() - created_at > TOKEN_TIMEOUT:
            del TOKEN_STORE[token]

        return TOKEN_STORE[token]

    except (jwt.ExpiredSignatureError, jwt.DecodeError, KeyError):
        raise HTTPException(status_code=403, detail="Permission denied.")
