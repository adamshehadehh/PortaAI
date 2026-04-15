from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text

from app.api.deps import get_current_user_id, get_current_user_portfolio_id
from app.db.session import SessionLocal

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("")
def get_notifications(
    user_id: int = Depends(get_current_user_id),
    portfolio_id: int = Depends(get_current_user_portfolio_id),
):
    """
    Return notifications for the authenticated user and portfolio.
    """
    db = SessionLocal()

    try:
        rows = db.execute(
            text("""
                SELECT id, title, message, is_read, created_at
                FROM notifications
                WHERE user_id = :user_id
                  AND portfolio_id = :portfolio_id
                ORDER BY created_at DESC
                LIMIT 20
            """),
            {
                "user_id": user_id,
                "portfolio_id": portfolio_id,
            }
        ).fetchall()

        notifications = []
        for notif_id, title, message, is_read, created_at in rows:
            notifications.append({
                "id": notif_id,
                "title": title,
                "message": message,
                "is_read": bool(is_read),
                "created_at": created_at.strftime("%Y-%m-%d %H:%M") if created_at else "",
            })

        return {
            "notifications": notifications
        }

    finally:
        db.close()


@router.post("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    user_id: int = Depends(get_current_user_id),
    portfolio_id: int = Depends(get_current_user_portfolio_id),
):
    """
    Mark one notification as read.
    """
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                UPDATE notifications
                SET is_read = TRUE
                WHERE id = :notification_id
                  AND user_id = :user_id
                  AND portfolio_id = :portfolio_id
            """),
            {
                "notification_id": notification_id,
                "user_id": user_id,
                "portfolio_id": portfolio_id,
            }
        )
        db.commit()

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Notification not found")

        return {"message": "Notification marked as read"}

    finally:
        db.close()
@router.post("/read-all")
def mark_all_notifications_as_read(
    user_id: int = Depends(get_current_user_id),
    portfolio_id: int = Depends(get_current_user_portfolio_id),
):
    """
    Mark all notifications as read for the authenticated user and portfolio.
    """
    db = SessionLocal()

    try:
        db.execute(
            text("""
                UPDATE notifications
                SET is_read = TRUE
                WHERE user_id = :user_id
                  AND portfolio_id = :portfolio_id
                  AND is_read = FALSE
            """),
            {
                "user_id": user_id,
                "portfolio_id": portfolio_id,
            }
        )
        db.commit()

        return {"message": "All notifications marked as read"}

    finally:
        db.close()


@router.delete("/clear-read")
def clear_read_notifications(
    user_id: int = Depends(get_current_user_id),
    portfolio_id: int = Depends(get_current_user_portfolio_id),
):
    """
    Delete all read notifications for the authenticated user and portfolio.
    """
    db = SessionLocal()

    try:
        db.execute(
            text("""
                DELETE FROM notifications
                WHERE user_id = :user_id
                  AND portfolio_id = :portfolio_id
                  AND is_read = TRUE
            """),
            {
                "user_id": user_id,
                "portfolio_id": portfolio_id,
            }
        )
        db.commit()

        return {"message": "Read notifications cleared"}

    finally:
        db.close()