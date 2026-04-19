from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text

from app.api.deps import get_current_user_id
from app.db.session import SessionLocal

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me")
def get_current_user_info(
    user_id: int = Depends(get_current_user_id),
):
    db = SessionLocal()

    try:
        user = db.execute(
            text("""
                SELECT email
                FROM users
                WHERE id = :user_id
            """),
            {"user_id": user_id}
        ).fetchone()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "id": user_id,
            "email": user[0],
        }

    finally:
        db.close()