from sqlalchemy import text


def get_user_email_and_email_setting(db, user_id: int):
    row = db.execute(
        text("""
            SELECT
                u.email,
                COALESCE(us.email_notifications_enabled, FALSE)
            FROM users u
            LEFT JOIN user_settings us ON us.user_id = u.id
            WHERE u.id = :user_id
        """),
        {"user_id": user_id}
    ).fetchone()

    if row is None:
        return None, False

    return row[0], bool(row[1])