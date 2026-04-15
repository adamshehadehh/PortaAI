from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import text

from app.core.security import SECRET_KEY, ALGORITHM
from app.db.session import SessionLocal

bearer_scheme = HTTPBearer()


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> int:
    """
    Extract and validate the JWT token, then return the authenticated user_id.
    """
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject = payload.get("sub")

        if subject is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token")

        return int(subject)

    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid authentication token")


def get_current_user_portfolio_id(
    user_id: int = Depends(get_current_user_id),
) -> int:
    """
    Find the portfolio that belongs to the authenticated user.
    For now, return the first portfolio for that user.
    """
    db = SessionLocal()

    try:
        row = db.execute(
            text("""
                SELECT id
                FROM portfolios
                WHERE user_id = :user_id
                ORDER BY id ASC
                LIMIT 1
            """),
            {"user_id": user_id}
        ).fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail="No portfolio found for this user")

        return int(row[0])

    finally:
        db.close()