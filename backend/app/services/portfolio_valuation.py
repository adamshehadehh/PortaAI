from sqlalchemy import text


def compute_current_portfolio_value(db, portfolio_id: int) -> float:
    """
    Compute current portfolio value as:
    cash + sum(position quantity * latest price).
    """
    portfolio_row = db.execute(
        text("""
            SELECT current_cash
            FROM portfolios
            WHERE id = :portfolio_id
        """),
        {"portfolio_id": portfolio_id}
    ).fetchone()

    if portfolio_row is None:
        raise ValueError("Portfolio not found")

    current_cash = float(portfolio_row[0])

    positions = db.execute(
        text("""
            SELECT
                pp.asset_id,
                pp.quantity,
                ph.close
            FROM portfolio_positions pp
            JOIN LATERAL (
                SELECT close
                FROM price_history
                WHERE asset_id = pp.asset_id
                ORDER BY date DESC
                LIMIT 1
            ) ph ON TRUE
            WHERE pp.portfolio_id = :portfolio_id
        """),
        {"portfolio_id": portfolio_id}
    ).fetchall()

    invested_value = 0.0
    for _, quantity, latest_close in positions:
        invested_value += float(quantity) * float(latest_close)

    return round(current_cash + invested_value, 2)