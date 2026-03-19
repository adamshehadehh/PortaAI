import pandas as pd
from sqlalchemy import text

from ai_engine.data.db_client import SessionLocal
from ai_engine.forecasting.model import load_saved_model


# Load the latest engineered features for one asset
def load_latest_features(db, asset_id: int):
    query = text("""
        SELECT 
            return_1d,
            return_7d,
            volatility_7d,
            ma_7,
            ma_30,
            momentum_7d,
            rsi_14
        FROM engineered_features
        WHERE asset_id = :asset_id
        ORDER BY date DESC
        LIMIT 1
    """)

    return db.execute(query, {"asset_id": asset_id}).fetchone()


# Load the latest close price for an asset
def get_latest_price(db, asset_id: int) -> float:
    row = db.execute(
        text("""
            SELECT close
            FROM price_history
            WHERE asset_id = :asset_id
            ORDER BY date DESC
            LIMIT 1
        """),
        {"asset_id": asset_id}
    ).fetchone()

    return float(row[0]) if row else 0.0


# Load portfolio cash
def get_portfolio_cash(db, portfolio_id: int) -> float:
    row = db.execute(
        text("""
            SELECT current_cash
            FROM portfolios
            WHERE id = :portfolio_id
        """),
        {"portfolio_id": portfolio_id}
    ).fetchone()

    return float(row[0]) if row else 0.0


# Load current position for one asset in one portfolio
def get_current_position(db, portfolio_id: int, asset_id: int):
    row = db.execute(
        text("""
            SELECT id, quantity, average_cost
            FROM portfolio_positions
            WHERE portfolio_id = :portfolio_id AND asset_id = :asset_id
        """),
        {"portfolio_id": portfolio_id, "asset_id": asset_id}
    ).fetchone()

    return row


# Create one portfolio run row
def create_portfolio_run(db, portfolio_id: int, run_type: str = "rebalance", notes: str = None) -> int:
    db.execute(
        text("""
            INSERT INTO portfolio_runs (portfolio_id, run_type, status, notes)
            VALUES (:portfolio_id, :run_type, :status, :notes)
        """),
        {
            "portfolio_id": portfolio_id,
            "run_type": run_type,
            "status": "completed",
            "notes": notes,
        }
    )
    db.commit()

    row = db.execute(
        text("""
            SELECT id
            FROM portfolio_runs
            WHERE portfolio_id = :portfolio_id
            ORDER BY id DESC
            LIMIT 1
        """),
        {"portfolio_id": portfolio_id}
    ).fetchone()

    return row[0]


# Save allocation decision
def save_allocation(
    db,
    portfolio_run_id: int,
    portfolio_id: int,
    asset_id: int,
    target_weight: float,
    current_weight: float,
    reason_summary: str
):
    db.execute(
        text("""
            INSERT INTO allocations (
                portfolio_run_id,
                portfolio_id,
                asset_id,
                target_weight,
                current_weight,
                reason_summary
            )
            VALUES (
                :portfolio_run_id,
                :portfolio_id,
                :asset_id,
                :target_weight,
                :current_weight,
                :reason_summary
            )
        """),
        {
            "portfolio_run_id": portfolio_run_id,
            "portfolio_id": portfolio_id,
            "asset_id": asset_id,
            "target_weight": target_weight,
            "current_weight": current_weight,
            "reason_summary": reason_summary,
        }
    )
    db.commit()


# Save executed trade
def save_trade(
    db,
    portfolio_run_id: int,
    portfolio_id: int,
    asset_id: int,
    action: str,
    quantity: float,
    price: float,
    amount: float
):
    db.execute(
        text("""
            INSERT INTO trades (
                portfolio_run_id,
                portfolio_id,
                asset_id,
                action,
                quantity,
                price,
                amount
            )
            VALUES (
                :portfolio_run_id,
                :portfolio_id,
                :asset_id,
                :action,
                :quantity,
                :price,
                :amount
            )
        """),
        {
            "portfolio_run_id": portfolio_run_id,
            "portfolio_id": portfolio_id,
            "asset_id": asset_id,
            "action": action,
            "quantity": quantity,
            "price": price,
            "amount": amount,
        }
    )
    db.commit()


# Update portfolio cash balance
def update_portfolio_cash(db, portfolio_id: int, new_cash: float):
    db.execute(
        text("""
            UPDATE portfolios
            SET current_cash = :new_cash
            WHERE id = :portfolio_id
        """),
        {
            "new_cash": new_cash,
            "portfolio_id": portfolio_id,
        }
    )
    db.commit()


# Create or update asset position after trade
def update_position(db, portfolio_id: int, asset_id: int, action: str, quantity: float, price: float):
    existing = get_current_position(db, portfolio_id, asset_id)

    if existing is None:
        # No position exists yet
        if action == "buy":
            db.execute(
                text("""
                    INSERT INTO portfolio_positions (
                        portfolio_id,
                        asset_id,
                        quantity,
                        average_cost
                    )
                    VALUES (
                        :portfolio_id,
                        :asset_id,
                        :quantity,
                        :average_cost
                    )
                """),
                {
                    "portfolio_id": portfolio_id,
                    "asset_id": asset_id,
                    "quantity": quantity,
                    "average_cost": price,
                }
            )
            db.commit()
        return

    position_id, current_qty, current_avg_cost = existing
    current_qty = float(current_qty)
    current_avg_cost = float(current_avg_cost)

    if action == "buy":
        new_qty = current_qty + quantity
        new_avg_cost = ((current_qty * current_avg_cost) + (quantity * price)) / new_qty

        db.execute(
            text("""
                UPDATE portfolio_positions
                SET quantity = :quantity,
                    average_cost = :average_cost
                WHERE id = :position_id
            """),
            {
                "quantity": new_qty,
                "average_cost": new_avg_cost,
                "position_id": position_id,
            }
        )
        db.commit()

    elif action == "sell":
        new_qty = current_qty - quantity

        if new_qty <= 0:
            # Fully closed position
            db.execute(
                text("""
                    DELETE FROM portfolio_positions
                    WHERE id = :position_id
                """),
                {"position_id": position_id}
            )
            db.commit()
        else:
            db.execute(
                text("""
                    UPDATE portfolio_positions
                    SET quantity = :quantity
                    WHERE id = :position_id
                """),
                {
                    "quantity": new_qty,
                    "position_id": position_id,
                }
            )
            db.commit()


# Load trained forecasting model and predict next return
def predict_next_return(db, asset_id: int) -> float:
    saved = load_saved_model(asset_id)
    model = saved["model"]
    features = saved["features"]

    latest_row = load_latest_features(db, asset_id)

    if latest_row is None:
        return 0.0

    # Build one-row dataframe using latest features
    X_latest = pd.DataFrame([{
        "return_1d": float(latest_row[0]) if latest_row[0] is not None else 0.0,
        "return_7d": float(latest_row[1]) if latest_row[1] is not None else 0.0,
        "volatility_7d": float(latest_row[2]) if latest_row[2] is not None else 0.0,
        "ma_7": float(latest_row[3]) if latest_row[3] is not None else 0.0,
        "ma_30": float(latest_row[4]) if latest_row[4] is not None else 0.0,
        "momentum_7d": float(latest_row[5]) if latest_row[5] is not None else 0.0,
        "rsi_14": float(latest_row[6]) if latest_row[6] is not None else 0.0,
    }])

    prediction = model.predict(X_latest[features])[0]
    return float(prediction)


# Basic rule-based decision logic for Phase 1
def decide_action(predicted_return: float):
    if predicted_return > 0.01:
        return "buy", 0.30   # invest 30% of available cash
    elif predicted_return < -0.01:
        return "sell", 1.00  # fully exit current position
    else:
        return "hold", 0.0


# Compute current portfolio weight of one asset
def compute_current_weight(db, portfolio_id: int, asset_id: int, latest_price: float, cash: float) -> float:
    position = get_current_position(db, portfolio_id, asset_id)

    asset_value = 0.0
    if position:
        _, qty, _ = position
        asset_value = float(qty) * latest_price

    total_value = cash + asset_value
    if total_value == 0:
        return 0.0

    return asset_value / total_value


def main():
    db = SessionLocal()

    try:
        portfolio_id = 1
        asset_id = 1  # AAPL for Phase 1

        predicted_return = predict_next_return(db, asset_id)
        latest_price = get_latest_price(db, asset_id)
        current_cash = get_portfolio_cash(db, portfolio_id)
        current_position = get_current_position(db, portfolio_id, asset_id)

        if latest_price <= 0:
            print("Latest price not found.")
            return

        action, fraction = decide_action(predicted_return)

        current_weight = compute_current_weight(
            db=db,
            portfolio_id=portfolio_id,
            asset_id=asset_id,
            latest_price=latest_price,
            cash=current_cash,
        )

        # Create a portfolio run
        portfolio_run_id = create_portfolio_run(
            db=db,
            portfolio_id=portfolio_id,
            run_type="rebalance",
            notes=f"Predicted return={predicted_return:.6f}, decision={action}"
        )

        print(f"Predicted next return: {predicted_return:.6f}")
        print(f"Latest price: {latest_price:.2f}")
        print(f"Current cash: {current_cash:.2f}")
        print(f"Decision: {action.upper()}")

        if action == "buy":
            amount_to_invest = current_cash * fraction
            quantity = amount_to_invest / latest_price if latest_price > 0 else 0.0
            new_cash = current_cash - amount_to_invest

            reason = f"Predicted return {predicted_return:.4f} > 0.01"

            # Save allocation
            save_allocation(
                db=db,
                portfolio_run_id=portfolio_run_id,
                portfolio_id=portfolio_id,
                asset_id=asset_id,
                target_weight=fraction,
                current_weight=current_weight,
                reason_summary=reason,
            )

            # Save trade
            save_trade(
                db=db,
                portfolio_run_id=portfolio_run_id,
                portfolio_id=portfolio_id,
                asset_id=asset_id,
                action="buy",
                quantity=quantity,
                price=latest_price,
                amount=amount_to_invest,
            )

            # Update position
            update_position(
                db=db,
                portfolio_id=portfolio_id,
                asset_id=asset_id,
                action="buy",
                quantity=quantity,
                price=latest_price,
            )

            # Update cash
            update_portfolio_cash(db, portfolio_id, new_cash)

            print(f"BUY executed: ${amount_to_invest:.2f} -> {quantity:.6f} units")

        elif action == "sell":
            if current_position is None:
                print("No position to sell. Holding instead.")

                save_allocation(
                    db=db,
                    portfolio_run_id=portfolio_run_id,
                    portfolio_id=portfolio_id,
                    asset_id=asset_id,
                    target_weight=0.0,
                    current_weight=current_weight,
                    reason_summary="Negative signal, but no existing position to sell",
                )
                return

            _, current_qty, _ = current_position
            current_qty = float(current_qty)

            quantity = current_qty * fraction
            amount_received = quantity * latest_price
            new_cash = current_cash + amount_received

            reason = f"Predicted return {predicted_return:.4f} < -0.01"

            save_allocation(
                db=db,
                portfolio_run_id=portfolio_run_id,
                portfolio_id=portfolio_id,
                asset_id=asset_id,
                target_weight=0.0,
                current_weight=current_weight,
                reason_summary=reason,
            )

            save_trade(
                db=db,
                portfolio_run_id=portfolio_run_id,
                portfolio_id=portfolio_id,
                asset_id=asset_id,
                action="sell",
                quantity=quantity,
                price=latest_price,
                amount=amount_received,
            )

            update_position(
                db=db,
                portfolio_id=portfolio_id,
                asset_id=asset_id,
                action="sell",
                quantity=quantity,
                price=latest_price,
            )

            update_portfolio_cash(db, portfolio_id, new_cash)

            print(f"SELL executed: {quantity:.6f} units -> ${amount_received:.2f}")

        else:
            reason = f"Predicted return {predicted_return:.4f} within hold band"

            save_allocation(
                db=db,
                portfolio_run_id=portfolio_run_id,
                portfolio_id=portfolio_id,
                asset_id=asset_id,
                target_weight=current_weight,
                current_weight=current_weight,
                reason_summary=reason,
            )

            print("HOLD executed: no trade, portfolio unchanged")

    finally:
        db.close()


if __name__ == "__main__":
    main()