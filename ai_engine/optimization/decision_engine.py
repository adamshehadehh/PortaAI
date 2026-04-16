import pandas as pd
from sqlalchemy import text
import shap
from ai_engine.data.db_client import SessionLocal
from ai_engine.forecasting.model import load_saved_model
from ai_engine.services.notifications import create_notification, get_portfolio_user_id
from ai_engine.services.portfolio_snapshots import create_portfolio_snapshot

# ============================================
# DATA LOADING
# ============================================

def load_latest_features(db, asset_id: int):
    """
    Load the most recent engineered features for one asset.
    These are used as inputs to the trained forecasting model.
    """
    query = text("""
    SELECT 
        return_1d,
        return_7d,
        volatility_7d,
        ma_7,
        ma_30,
        momentum_7d,
        rsi_14,
        sentiment_aggregate
    FROM engineered_features
    WHERE asset_id = :asset_id
    ORDER BY date DESC
    LIMIT 1
    """)
    return db.execute(query, {"asset_id": asset_id}).fetchone()


def get_latest_price(db, asset_id: int) -> float:
    """
    Load the latest available close price for an asset.
    """
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


def get_allowed_assets_for_portfolio(db, portfolio_id: int):
    """
    Load the asset universe selected by the user for this portfolio.
    """
    rows = db.execute(
        text("""
            SELECT pa.asset_id, a.symbol
            FROM portfolio_assets pa
            JOIN assets a ON pa.asset_id = a.id
            WHERE pa.portfolio_id = :portfolio_id
            ORDER BY pa.asset_id
        """),
        {"portfolio_id": portfolio_id}
    ).fetchall()

    return rows
def get_recent_average_sentiment(db, asset_id: int, limit: int = 10) -> float:
    """
    Compute the average sentiment score from the most recent news items
    for a given asset.

    We use only the latest N sentiment rows so the signal reflects
    recent market/news mood instead of very old headlines.
    """
    row = db.execute(
        text("""
            SELECT AVG(sentiment_score)
            FROM (
                SELECT sentiment_score
                FROM sentiment_scores
                WHERE asset_id = :asset_id
                ORDER BY created_at DESC
                LIMIT :limit
            ) recent_scores
        """),
        {
            "asset_id": asset_id,
            "limit": limit,
        }
    ).fetchone()

    return float(row[0]) if row and row[0] is not None else 0.0

# ============================================
# PORTFOLIO STATE
# ============================================

def get_portfolio_cash(db, portfolio_id: int) -> float:
    """
    Get current available cash in the portfolio.
    """
    row = db.execute(
        text("""
            SELECT current_cash
            FROM portfolios
            WHERE id = :portfolio_id
        """),
        {"portfolio_id": portfolio_id}
    ).fetchone()

    return float(row[0]) if row else 0.0


def update_portfolio_cash(db, portfolio_id: int, new_cash: float):
    """
    Update the current cash balance after trades are executed.
    """
    db.execute(
        text("""
            UPDATE portfolios
            SET current_cash = :new_cash
            WHERE id = :portfolio_id
        """),
        {"new_cash": new_cash, "portfolio_id": portfolio_id}
    )
    db.commit()


def get_current_position(db, portfolio_id: int, asset_id: int):
    """
    Get current quantity and average cost for one asset in a portfolio.
    """
    row = db.execute(
        text("""
            SELECT id, quantity, average_cost
            FROM portfolio_positions
            WHERE portfolio_id = :portfolio_id AND asset_id = :asset_id
        """),
        {"portfolio_id": portfolio_id, "asset_id": asset_id}
    ).fetchone()

    return row


def get_all_positions(db, portfolio_id: int):
    """
    Get all current positions in the portfolio.
    """
    rows = db.execute(
        text("""
            SELECT asset_id, quantity
            FROM portfolio_positions
            WHERE portfolio_id = :portfolio_id
        """),
        {"portfolio_id": portfolio_id}
    ).fetchall()

    return rows


def compute_total_portfolio_value(db, portfolio_id: int, cash: float) -> float:
    """
    Compute total portfolio value = cash + market value of all positions.
    """
    positions = get_all_positions(db, portfolio_id)
    total_value = cash

    for asset_id, quantity in positions:
        latest_price = get_latest_price(db, asset_id)
        total_value += float(quantity) * latest_price

    return total_value


def compute_current_weight(db, portfolio_id: int, asset_id: int, total_portfolio_value: float) -> float:
    """
    Compute current portfolio weight of one asset.
    """
    if total_portfolio_value <= 0:
        return 0.0

    position = get_current_position(db, portfolio_id, asset_id)

    if position is None:
        return 0.0

    _, quantity, _ = position
    latest_price = get_latest_price(db, asset_id)
    asset_value = float(quantity) * latest_price

    return asset_value / total_portfolio_value


# ============================================
# LOGGING TABLES
# ============================================

def create_portfolio_run(db, portfolio_id: int, run_type: str = "rebalance", notes: str = None) -> int:
    """
    Log one portfolio rebalance/execution cycle.
    """
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


def save_allocation(db, portfolio_run_id, portfolio_id, asset_id, target_weight, current_weight, reason_summary):
    """
    Store AI target allocation for an asset.
    """
    db.execute(
        text("""
            INSERT INTO allocations (
                portfolio_run_id, portfolio_id, asset_id,
                target_weight, current_weight, reason_summary
            )
            VALUES (
                :portfolio_run_id, :portfolio_id, :asset_id,
                :target_weight, :current_weight, :reason_summary
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


def save_trade(db, portfolio_run_id, portfolio_id, asset_id, action, quantity, price, amount):
    """
    Store executed trade in the trades table.
    """
    db.execute(
        text("""
            INSERT INTO trades (
                portfolio_run_id, portfolio_id, asset_id,
                action, quantity, price, amount
            )
            VALUES (
                :portfolio_run_id, :portfolio_id, :asset_id,
                :action, :quantity, :price, :amount
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


# ============================================
# POSITION UPDATE
# ============================================

def update_position(db, portfolio_id: int, asset_id: int, action: str, quantity: float, price: float):
    """
    Update portfolio_positions after a BUY or SELL.
    """
    existing = get_current_position(db, portfolio_id, asset_id)

    if existing is None:
        # No position exists yet
        if action == "buy" and quantity > 0:
            db.execute(
                text("""
                    INSERT INTO portfolio_positions (portfolio_id, asset_id, quantity, average_cost)
                    VALUES (:portfolio_id, :asset_id, :quantity, :average_cost)
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

    if action == "buy" and quantity > 0:
        # Recompute weighted average cost after buying more
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

    elif action == "sell" and quantity > 0:
        # Reduce or fully close the position
        new_qty = current_qty - quantity

        if new_qty <= 0:
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


# ============================================
# FORECASTING / SCORING
# ============================================

def predict_next_return(db, asset_id: int) -> float:
    """
    Load the trained model for one asset and predict the next return.
    """
    saved = load_saved_model(asset_id)
    model = saved["model"]
    features = saved["features"]

    latest_row = load_latest_features(db, asset_id)

    if latest_row is None:
        return 0.0

    X_latest = pd.DataFrame([{
    "return_1d": float(latest_row[0]) if latest_row[0] is not None else 0.0,
    "return_7d": float(latest_row[1]) if latest_row[1] is not None else 0.0,
    "volatility_7d": float(latest_row[2]) if latest_row[2] is not None else 0.0,
    "ma_7": float(latest_row[3]) if latest_row[3] is not None else 0.0,
    "ma_30": float(latest_row[4]) if latest_row[4] is not None else 0.0,
    "momentum_7d": float(latest_row[5]) if latest_row[5] is not None else 0.0,
    "rsi_14": float(latest_row[6]) if latest_row[6] is not None else 0.0,
    "sentiment_aggregate": float(latest_row[7]) if latest_row[7] is not None else 0.0,
    }])

    prediction = model.predict(X_latest[features])[0]
    return float(prediction)

def get_top_shap_reasons(db, asset_id: int, top_n: int = 3):
    """
    Explain the latest model prediction for one asset using SHAP.

    Returns the top N most important feature contributions sorted by absolute impact.
    """
    saved = load_saved_model(asset_id)
    model = saved["model"]
    features = saved["features"]

    latest_row = load_latest_features(db, asset_id)
    if latest_row is None:
        return []

    # Build latest feature frame using the same structure used at inference time
    X_latest = pd.DataFrame([{
        "return_1d": float(latest_row[0]) if latest_row[0] is not None else 0.0,
        "return_7d": float(latest_row[1]) if latest_row[1] is not None else 0.0,
        "volatility_7d": float(latest_row[2]) if latest_row[2] is not None else 0.0,
        "ma_7": float(latest_row[3]) if latest_row[3] is not None else 0.0,
        "ma_30": float(latest_row[4]) if latest_row[4] is not None else 0.0,
        "momentum_7d": float(latest_row[5]) if latest_row[5] is not None else 0.0,
        "rsi_14": float(latest_row[6]) if latest_row[6] is not None else 0.0,
        "sentiment_aggregate": float(latest_row[7]) if latest_row[7] is not None else 0.0,
    }])

    X_latest = X_latest[features]

    # Use TreeExplainer for XGBoost
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_latest)

    contributions = []
    for i, feature_name in enumerate(features):
        feature_value = float(X_latest.iloc[0][feature_name])
        feature_shap = float(shap_values[0][i])

        if feature_shap > 0:
            direction = "pushes UP"
        elif feature_shap < 0:
            direction = "pushes DOWN"
        else:
            direction = "has NO EFFECT"

        contributions.append({
            "feature": feature_name,
            "value": feature_value,
            "shap": feature_shap,
            "direction": direction,
        })

    # Sort by absolute importance
    contributions.sort(key=lambda x: abs(x["shap"]), reverse=True)

    return contributions[:top_n]
    
def compute_final_asset_score(predicted_return: float, avg_sentiment: float, sentiment_weight: float = 0.002) -> float:
    """
    Combine quantitative forecast with sentiment signal.

    The sentiment weight is kept small so sentiment influences the score
    without overpowering the forecasting model.
    """
    return predicted_return + (sentiment_weight * avg_sentiment)
# ============================================
# 🔹 CONFIDENCE → CASH ALLOCATION
# ============================================

def compute_invest_fraction(predictions):
    """
    Compute how much of the portfolio to invest based on confidence.

    We now use final_score (prediction + sentiment) instead of only
    predicted_return.
    """
    positive = [p["final_score"] for p in predictions if p["final_score"] > 0]

    if not positive:
        return 0.2

    avg_confidence = sum(positive) / len(positive)

    scale = 100
    invest_fraction = avg_confidence * scale

    # Keep portfolio exposure between 20% and 80%
    invest_fraction = max(0.2, min(0.8, invest_fraction))

    print(f"\nConfidence (from final scores): {avg_confidence:.6f}")
    print(f"Dynamic invest fraction: {invest_fraction:.2f}")

    return invest_fraction

# ============================================
# TARGET WEIGHT LOGIC
# ============================================

def compute_target_weights(predictions, invest_fraction):
    """
    Convert positive final scores into target portfolio weights.

    We now use final_score instead of raw predicted_return so that
    both forecasting and sentiment influence allocation.
    """
    positive_assets = [p for p in predictions if p["final_score"] > 0]

    if not positive_assets:
        return {}

    total_positive_score = sum(p["final_score"] for p in positive_assets)

    if total_positive_score <= 0:
        return {}

    target_weights = {}

    for p in positive_assets:
        normalized_score = p["final_score"] / total_positive_score
        target_weights[p["asset_id"]] = normalized_score * invest_fraction

    return target_weights


# ============================================
# MAIN MULTI-ASSET REBALANCER
# ============================================

def main(portfolio_id: int):
    db = SessionLocal()

    try:
        user_id = get_portfolio_user_id(db, portfolio_id)
        current_cash = get_portfolio_cash(db, portfolio_id)
        total_portfolio_value = compute_total_portfolio_value(db, portfolio_id, current_cash)
        allowed_assets = get_allowed_assets_for_portfolio(db, portfolio_id)

        if not allowed_assets:
            print("No allowed assets found in portfolio_assets.")
            return

        predictions = []

       # Predict all allowed assets and combine with recent sentiment
        for asset_id, symbol in allowed_assets:
            try:
                predicted_return = predict_next_return(db, asset_id)
                latest_price = get_latest_price(db, asset_id)

                # Load recent average sentiment for this asset
                avg_sentiment = get_recent_average_sentiment(db, asset_id, limit=10)

                # Combine quantitative prediction with sentiment
                final_score = compute_final_asset_score(
                    predicted_return=predicted_return,
                    avg_sentiment=avg_sentiment,
                    sentiment_weight=0.002
                )

                predictions.append({
                    "asset_id": asset_id,
                    "symbol": symbol,
                    "predicted_return": predicted_return,
                    "avg_sentiment": avg_sentiment,
                    "final_score": final_score,
                    "price": latest_price,
                })
            except Exception as e:
                print(f"Skipping {symbol}: {e}")
        if not predictions:
            print("No predictions generated.")
            return

        # Compute dynamic investment fraction
        invest_fraction = compute_invest_fraction(predictions)

        # Compute target weights using dynamic allocation
        target_weights = compute_target_weights(predictions, invest_fraction=invest_fraction)
        
        # Create one portfolio run for this rebalance
        portfolio_run_id = create_portfolio_run(
            db=db,
            portfolio_id=portfolio_id,
            run_type="rebalance",
            notes="Full multi-asset buy/sell/hold rebalance"
        )

        print("\nPredictions + Sentiment:")
        for p in predictions:
            print(
                f"{p['symbol']}: "
                f"pred={p['predicted_return']:.6f}, "
                f"sent={p['avg_sentiment']:.4f}, "
                f"final={p['final_score']:.6f}"
            )
                
        # Small threshold to avoid tiny unnecessary trades
        rebalance_threshold = 0.01

        # Loop through all assets and compare current vs target
        for p in predictions:
            asset_id = p["asset_id"]
            symbol = p["symbol"]
            predicted_return = p["predicted_return"]
            latest_price = p["price"]
            top_reasons = get_top_shap_reasons(db, asset_id, top_n=3)
            current_weight = compute_current_weight(
                db=db,
                portfolio_id=portfolio_id,
                asset_id=asset_id,
                total_portfolio_value=total_portfolio_value
            )

            target_weight = target_weights.get(asset_id, 0.0)
            weight_diff = target_weight - current_weight

            # Save the allocation row no matter what
            avg_sentiment = p["avg_sentiment"]
            final_score = p["final_score"]

            reason = (
                f"predicted_return={predicted_return:.4f}, "
                f"avg_sentiment={avg_sentiment:.4f}, "
                f"final_score={final_score:.4f}, "
                f"target_weight={target_weight:.4f}"
            )
            save_allocation(
                db=db,
                portfolio_run_id=portfolio_run_id,
                portfolio_id=portfolio_id,
                asset_id=asset_id,
                target_weight=target_weight,
                current_weight=current_weight,
                reason_summary=reason,
            )

            # HOLD if target and current are already close
            if abs(weight_diff) < rebalance_threshold:
                print(f"HOLD {symbol} | current={current_weight:.4f}, target={target_weight:.4f}")
                print("Top reasons:")
                for reason_item in top_reasons:
                    print(
                        f"  - {reason_item['feature']}: "
                        f"value={reason_item['value']:.6f}, "
                        f"shap={reason_item['shap']:.6f} -> {reason_item['direction']}"
                    )
                continue

            # BUY if target > current
            if weight_diff > 0:
                amount_to_invest = weight_diff * total_portfolio_value

                # Never buy more than available cash
                amount_to_invest = min(amount_to_invest, current_cash)

                if amount_to_invest <= 0 or latest_price <= 0:
                    print(f"HOLD {symbol} | insufficient cash or invalid price")
                    continue

                quantity = amount_to_invest / latest_price

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

                update_position(
                    db=db,
                    portfolio_id=portfolio_id,
                    asset_id=asset_id,
                    action="buy",
                    quantity=quantity,
                    price=latest_price,
                )

                current_cash -= amount_to_invest
                if user_id is not None:
                    create_notification(
                        db=db,
                        user_id=user_id,
                        portfolio_id=portfolio_id,
                        title="Buy Signal Executed",
                        message=f"A BUY trade was executed for {symbol} worth ${amount_to_invest:.2f}.",
                    )
                    db.commit()
                print(f"BUY {symbol} | amount=${amount_to_invest:.2f} | current={current_weight:.4f} -> target={target_weight:.4f}")
                print("Top reasons:")
                for reason_item in top_reasons:
                    print(
                        f"  - {reason_item['feature']}: "
                        f"value={reason_item['value']:.6f}, "
                        f"shap={reason_item['shap']:.6f} -> {reason_item['direction']}"
                    )
            # SELL if target < current
            elif weight_diff < 0:
                position = get_current_position(db, portfolio_id, asset_id)

                if position is None:
                    print(f"HOLD {symbol} | no existing position to sell")
                    continue

                _, current_qty, _ = position
                current_qty = float(current_qty)

                current_asset_value = current_weight * total_portfolio_value
                target_asset_value = target_weight * total_portfolio_value
                amount_to_sell = current_asset_value - target_asset_value

                if amount_to_sell <= 0 or latest_price <= 0:
                    print(f"HOLD {symbol} | nothing to sell")
                    continue

                quantity_to_sell = amount_to_sell / latest_price
                quantity_to_sell = min(quantity_to_sell, current_qty)

                if quantity_to_sell <= 0:
                    print(f"HOLD {symbol} | quantity to sell too small")
                    continue

                actual_amount = quantity_to_sell * latest_price

                save_trade(
                    db=db,
                    portfolio_run_id=portfolio_run_id,
                    portfolio_id=portfolio_id,
                    asset_id=asset_id,
                    action="sell",
                    quantity=quantity_to_sell,
                    price=latest_price,
                    amount=actual_amount,
                )

                update_position(
                    db=db,
                    portfolio_id=portfolio_id,
                    asset_id=asset_id,
                    action="sell",
                    quantity=quantity_to_sell,
                    price=latest_price,
                )

                current_cash += actual_amount
                if user_id is not None:
                    create_notification(
                        db=db,
                        user_id=user_id,
                        portfolio_id=portfolio_id,
                        title="Sell Signal Executed",
                        message=f"A SELL trade was executed for {symbol} worth ${actual_amount:.2f}.",
                    )
                    db.commit()
                print(f"SELL {symbol} | amount=${actual_amount:.2f} | current={current_weight:.4f} -> target={target_weight:.4f}")
                print("Top reasons:")
                for reason_item in top_reasons:
                    print(
                        f"  - {reason_item['feature']}: "
                        f"value={reason_item['value']:.6f}, "
                        f"shap={reason_item['shap']:.6f} -> {reason_item['direction']}"
                    )
        # Save final cash balance
        update_portfolio_cash(db, portfolio_id, current_cash)
        
        final_total_portfolio_value = compute_total_portfolio_value(
            db, portfolio_id, current_cash
        )

        create_portfolio_snapshot(
            db=db,
            portfolio_id=portfolio_id,
            total_value=final_total_portfolio_value,
        )
        if user_id is not None:
            create_notification(
                db=db,
                user_id=user_id,
                portfolio_id=portfolio_id,
                title="Portfolio Rebalanced",
                message="PortaAI completed a rebalance cycle successfully.",
            )
            db.commit()
        print(f"\nFinal remaining cash: ${current_cash:.2f}")

    finally:
        db.close()


if __name__ == "__main__":
    main(portfolio_id=1)