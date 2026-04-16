from sqlalchemy import text


def create_portfolio_snapshot(db, portfolio_id: int, total_value: float):
    db.execute(
        text("""
            INSERT INTO portfolio_snapshots (portfolio_id, total_value)
            VALUES (:portfolio_id, :total_value)
        """),
        {
            "portfolio_id": portfolio_id,
            "total_value": round(float(total_value), 2),
        }
    )
    db.commit()
