from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import text

from app.db.session import SessionLocal
from app.core.security import create_access_token, verify_password,hash_password

router = APIRouter(prefix="/api/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

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

@router.post("/register")
def register_user(payload: RegisterRequest):
    db = SessionLocal()

    try:
        existing_user = db.execute(
            text("""
                SELECT id
                FROM users
                WHERE email = :email
            """),
            {"email": payload.email}
        ).fetchone()

        if existing_user is not None:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = hash_password(payload.password)

        user_row = db.execute(
            text("""
                INSERT INTO users (email, hashed_password)
                VALUES (:email, :hashed_password)
                RETURNING id, email
            """),
            {
                "email": payload.email,
                "hashed_password": hashed_password,
            }
        ).fetchone()

        user_id = int(user_row[0])
        user_email = user_row[1]

        portfolio_row = db.execute(
            text("""
                INSERT INTO portfolios (
                    user_id,
                    name,
                    initial_cash,
                    current_cash,
                    base_currency
                )
                VALUES (
                    :user_id,
                    :name,
                    :initial_cash,
                    :current_cash,
                    :base_currency
                )
                RETURNING id
            """),
            {
                "user_id": user_id,
                "name": "Main Portfolio",
                "initial_cash": 100000.0,
                "current_cash": 100000.0,
                "base_currency": "USD",
            }
        ).fetchone()

        portfolio_id = int(portfolio_row[0])

        db.execute(
            text("""
                INSERT INTO user_settings (
                    user_id,
                    in_app_notifications_enabled,
                    email_notifications_enabled,
                    trade_notifications_enabled,
                    rebalance_notifications_enabled,
                    rebalance_frequency
                )
                VALUES (
                    :user_id,
                    TRUE,
                    FALSE,
                    TRUE,
                    TRUE,
                    'weekly'
                )
            """),
            {"user_id": user_id}
        )
        default_symbols = ["AAPL", "MSFT", "NVDA", "BTC-USD", "ETH-USD", "GLD"]

        for symbol in default_symbols:
            asset_row = db.execute(
                text("""
                    SELECT id
                    FROM assets
                    WHERE symbol = :symbol
                """),
                {"symbol": symbol}
            ).fetchone()

            if asset_row is not None:
                asset_id = int(asset_row[0])

                existing_row = db.execute(
                    text("""
                        SELECT id
                        FROM portfolio_assets
                        WHERE portfolio_id = :portfolio_id
                        AND asset_id = :asset_id
                    """),
                    {
                        "portfolio_id": portfolio_id,
                        "asset_id": asset_id,
                    }
                ).fetchone()

                if existing_row is None:
                    db.execute(
                        text("""
                            INSERT INTO portfolio_assets (portfolio_id, asset_id, added_at)
                            VALUES (:portfolio_id, :asset_id, NOW())
                        """),
                        {
                            "portfolio_id": portfolio_id,
                            "asset_id": asset_id,
                        }
                    )
        db.commit()

        access_token = create_access_token(subject=str(user_id))

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "email": user_email,
            },
            "portfolio": {
                "id": portfolio_id,
                "name": "Main Portfolio",
            },
        }

    finally:
        db.close()