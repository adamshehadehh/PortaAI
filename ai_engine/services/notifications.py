from sqlalchemy import text


def get_portfolio_user_id(db, portfolio_id: int):
    row = db.execute(
        text("""
            SELECT user_id
            FROM portfolios
            WHERE id = :portfolio_id
        """),
        {"portfolio_id": portfolio_id}
    ).fetchone()

    return int(row[0]) if row else None


def get_user_notification_settings(db, user_id: int):
    row = db.execute(
        text("""
            SELECT
                in_app_notifications_enabled,
                trade_notifications_enabled,
                rebalance_notifications_enabled
            FROM user_settings
            WHERE user_id = :user_id
        """),
        {"user_id": user_id}
    ).fetchone()

    if row is None:
        return {
            "in_app_notifications_enabled": True,
            "trade_notifications_enabled": True,
            "rebalance_notifications_enabled": True,
        }

    return {
        "in_app_notifications_enabled": bool(row[0]),
        "trade_notifications_enabled": bool(row[1]),
        "rebalance_notifications_enabled": bool(row[2]),
    }


def create_notification(
    db,
    user_id: int,
    portfolio_id: int,
    title: str,
    message: str,
    notification_type: str = "general",
):
    """
    Create an in-app notification only if user settings allow it.
    notification_type: trade | rebalance | general
    """
    settings = get_user_notification_settings(db, user_id)

    if not settings["in_app_notifications_enabled"]:
        return

    if notification_type == "trade" and not settings["trade_notifications_enabled"]:
        return

    if notification_type == "rebalance" and not settings["rebalance_notifications_enabled"]:
        return

    db.execute(
        text("""
            INSERT INTO notifications (user_id, portfolio_id, title, message, is_read)
            VALUES (:user_id, :portfolio_id, :title, :message, FALSE)
        """),
        {
            "user_id": user_id,
            "portfolio_id": portfolio_id,
            "title": title,
            "message": message,
        }
    )