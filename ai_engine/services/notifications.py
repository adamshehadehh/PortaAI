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


def create_notification(db, user_id: int, portfolio_id: int, title: str, message: str):
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