from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text

from app.db.session import SessionLocal
from app.core.security import create_access_token, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
def login(payload: LoginRequest):
    """
    Authenticate a user with email + password and return a JWT token.
    """
    db = SessionLocal()

    try:
        row = db.execute(
            text("""
                SELECT id, email, hashed_password
                FROM users
                WHERE email = :email
            """),
            {"email": payload.email}
        ).fetchone()

        if row is None:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        user_id, email, hashed_password = row

        if not verify_password(payload.password, hashed_password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        access_token = create_access_token(subject=str(user_id))

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "email": email,
            },
        }

    finally:
        db.close()