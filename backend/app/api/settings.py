from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text

from app.api.deps import get_current_user_id
from app.db.session import SessionLocal

router = APIRouter(prefix="/api/settings", tags=["settings"])


class SettingsUpdateRequest(BaseModel):
    in_app_notifications_enabled: bool
    email_notifications_enabled: bool
    trade_notifications_enabled: bool
    rebalance_notifications_enabled: bool
    rebalance_frequency: str


@router.get("")
def get_user_settings(
    user_id: int = Depends(get_current_user_id),
):
    db = SessionLocal()

    try:
        row = db.execute(
            text("""
                SELECT
                    in_app_notifications_enabled,
                    email_notifications_enabled,
                    trade_notifications_enabled,
                    rebalance_notifications_enabled,
                    rebalance_frequency
                FROM user_settings
                WHERE user_id = :user_id
            """),
            {"user_id": user_id}
        ).fetchone()

        if row is None:
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
            db.commit()

            row = db.execute(
                text("""
                    SELECT
                        in_app_notifications_enabled,
                        email_notifications_enabled,
                        trade_notifications_enabled,
                        rebalance_notifications_enabled,
                        rebalance_frequency
                    FROM user_settings
                    WHERE user_id = :user_id
                """),
                {"user_id": user_id}
            ).fetchone()

        return {
            "in_app_notifications_enabled": bool(row[0]),
            "email_notifications_enabled": bool(row[1]),
            "trade_notifications_enabled": bool(row[2]),
            "rebalance_notifications_enabled": bool(row[3]),
            "rebalance_frequency": row[4],
        }

    finally:
        db.close()


@router.put("")
def update_user_settings(
    payload: SettingsUpdateRequest,
    user_id: int = Depends(get_current_user_id),
):
    db = SessionLocal()

    try:
        existing = db.execute(
            text("""
                SELECT id
                FROM user_settings
                WHERE user_id = :user_id
            """),
            {"user_id": user_id}
        ).fetchone()

        if existing is None:
            db.execute(
                text("""
                    INSERT INTO user_settings (
                        user_id,
                        in_app_notifications_enabled,
                        email_notifications_enabled,
                        trade_notifications_enabled,
                        rebalance_notifications_enabled,
                        rebalance_frequency,
                        updated_at
                    )
                    VALUES (
                        :user_id,
                        :in_app_notifications_enabled,
                        :email_notifications_enabled,
                        :trade_notifications_enabled,
                        :rebalance_notifications_enabled,
                        :rebalance_frequency,
                        NOW()
                    )
                """),
                {
                    "user_id": user_id,
                    "in_app_notifications_enabled": payload.in_app_notifications_enabled,
                    "email_notifications_enabled": payload.email_notifications_enabled,
                    "trade_notifications_enabled": payload.trade_notifications_enabled,
                    "rebalance_notifications_enabled": payload.rebalance_notifications_enabled,
                    "rebalance_frequency": payload.rebalance_frequency,
                }
            )
        else:
            db.execute(
                text("""
                    UPDATE user_settings
                    SET
                        in_app_notifications_enabled = :in_app_notifications_enabled,
                        email_notifications_enabled = :email_notifications_enabled,
                        trade_notifications_enabled = :trade_notifications_enabled,
                        rebalance_notifications_enabled = :rebalance_notifications_enabled,
                        rebalance_frequency = :rebalance_frequency,
                        updated_at = NOW()
                    WHERE user_id = :user_id
                """),
                {
                    "user_id": user_id,
                    "in_app_notifications_enabled": payload.in_app_notifications_enabled,
                    "email_notifications_enabled": payload.email_notifications_enabled,
                    "trade_notifications_enabled": payload.trade_notifications_enabled,
                    "rebalance_notifications_enabled": payload.rebalance_notifications_enabled,
                    "rebalance_frequency": payload.rebalance_frequency,
                }
            )

        db.commit()

        return {"message": "Settings updated successfully"}

    finally:
        db.close()