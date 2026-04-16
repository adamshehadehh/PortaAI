from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from fastapi import Depends
from app.api.deps import get_current_user_portfolio_id
import pandas as pd
import shap
from app.db.session import SessionLocal
from ai_engine.optimization.decision_engine import (
    compute_final_asset_score,
    get_recent_average_sentiment,
    get_allowed_assets_for_portfolio,
    predict_next_return,
)
from ai_engine.forecasting.model import load_saved_model
from ai_engine.optimization.decision_engine import load_latest_features

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

def get_top_shap_explanations(db, asset_id: int, top_n: int = 3):
    """
    Return the latest prediction explanation for one asset using SHAP.
    """
    saved = load_saved_model(asset_id)
    model = saved["model"]
    features = saved["features"]

    latest_row = load_latest_features(db, asset_id)
    if latest_row is None:
        return None

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

    prediction = float(model.predict(X_latest)[0])

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_latest)

    contributions = []
    for i, feature_name in enumerate(features):
        feature_value = float(X_latest.iloc[0][feature_name])
        feature_shap = float(shap_values[0][i])

        if feature_shap > 0:
            direction = "UP"
        elif feature_shap < 0:
            direction = "DOWN"
        else:
            direction = "NEUTRAL"

        contributions.append({
            "feature": feature_name,
            "value": round(feature_value, 6),
            "shap": round(feature_shap, 6),
            "direction": direction,
        })

    contributions.sort(key=lambda x: abs(x["shap"]), reverse=True)

    return {
        "predicted_return": round(prediction, 6),
        "reasons": contributions[:top_n],
    }
@router.get("/summary")
def get_dashboard_summary(
    portfolio_id: int = Depends(get_current_user_portfolio_id),
):
    """
    Return high-level dashboard numbers for one portfolio:
    - total portfolio value
    - current cash
    - invested percentage
    """
    db = SessionLocal()

    try:
        # 1) Load current cash
        portfolio_row = db.execute(
            text("""
                SELECT current_cash
                FROM portfolios
                WHERE id = :portfolio_id
            """),
            {"portfolio_id": portfolio_id}
        ).fetchone()

        if portfolio_row is None:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        current_cash = float(portfolio_row[0])

        # 2) Compute current market value of all positions
        positions = db.execute(
            text("""
                SELECT pp.asset_id, pp.quantity, ph.close
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
        for asset_id, quantity, latest_close in positions:
            invested_value += float(quantity) * float(latest_close)

        total_value = current_cash + invested_value
        invested_percent = (invested_value / total_value * 100.0) if total_value > 0 else 0.0

        return {
            "portfolio_id": portfolio_id,
            "total_value": round(total_value, 2),
            "cash": round(current_cash, 2),
            "invested_percent": round(invested_percent, 2),
        }

    finally:
        db.close()
@router.get("/positions")
def get_portfolio_positions(
    portfolio_id: int = Depends(get_current_user_portfolio_id),
):
    """
    Return the current portfolio positions with:
    - asset symbol
    - quantity
    - average cost
    - current portfolio weight
    - status
    """
    db = SessionLocal()

    try:
        # Load current cash
        portfolio_row = db.execute(
            text("""
                SELECT current_cash
                FROM portfolios
                WHERE id = :portfolio_id
            """),
            {"portfolio_id": portfolio_id}
        ).fetchone()

        if portfolio_row is None:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        current_cash = float(portfolio_row[0])

        # Load positions with latest prices
        rows = db.execute(
            text("""
                SELECT 
                    a.symbol,
                    pp.quantity,
                    pp.average_cost,
                    ph.close
                FROM portfolio_positions pp
                JOIN assets a ON pp.asset_id = a.id
                JOIN LATERAL (
                    SELECT close
                    FROM price_history
                    WHERE asset_id = pp.asset_id
                    ORDER BY date DESC
                    LIMIT 1
                ) ph ON TRUE
                WHERE pp.portfolio_id = :portfolio_id
                ORDER BY a.symbol
            """),
            {"portfolio_id": portfolio_id}
        ).fetchall()

        # Compute total portfolio value
        invested_value = 0.0
        for symbol, quantity, average_cost, latest_close in rows:
            invested_value += float(quantity) * float(latest_close)

        total_value = current_cash + invested_value

        positions = []
        for symbol, quantity, average_cost, latest_close in rows:
            market_value = float(quantity) * float(latest_close)
            current_weight = (market_value / total_value * 100.0) if total_value > 0 else 0.0

            positions.append({
                "symbol": symbol,
                "quantity": round(float(quantity), 4),
                "avg_cost": round(float(average_cost), 2),
                "current_weight": round(current_weight, 2),
                "status": "Active",
            })

        return {
            "portfolio_id": portfolio_id,
            "positions": positions,
        }

    finally:
        db.close()

@router.get("/predictions")
def get_portfolio_predictions(
    portfolio_id: int = Depends(get_current_user_portfolio_id),
):
    """
    Return latest predictions for the assets allowed in the portfolio.
    Includes:
    - predicted return
    - recent sentiment
    - final score
    - suggested action
    """
    db = SessionLocal()

    try:
        allowed_assets = get_allowed_assets_for_portfolio(db, portfolio_id)

        predictions = []

        for asset_id, symbol in allowed_assets:
            predicted_return = predict_next_return(db, asset_id)
            avg_sentiment = get_recent_average_sentiment(db, asset_id, limit=10)
            final_score = compute_final_asset_score(
                predicted_return=predicted_return,
                avg_sentiment=avg_sentiment,
                sentiment_weight=0.002,
            )

            if final_score > 0:
                action = "BUY"
            elif final_score < 0:
                action = "SELL"
            else:
                action = "HOLD"

            predictions.append({
                "symbol": symbol,
                "predicted_return": round(float(predicted_return), 6),
                "sentiment": round(float(avg_sentiment), 4),
                "final_score": round(float(final_score), 6),
                "action": action,
            })

        return {
            "portfolio_id": portfolio_id,
            "predictions": predictions,
        }

    finally:
        db.close()
@router.get("/trades")
def get_portfolio_trades(
    portfolio_id: int = Depends(get_current_user_portfolio_id),
):
    """
    Return recent simulated trades for one portfolio.
    """
    db = SessionLocal()

    try:
        rows = db.execute(
            text("""
                SELECT
                    a.symbol,
                    t.action,
                    t.amount,
                    t.executed_at
                FROM trades t
                JOIN assets a ON t.asset_id = a.id
                WHERE t.portfolio_id = :portfolio_id
                ORDER BY t.executed_at DESC
                LIMIT 20
            """),
            {"portfolio_id": portfolio_id}
        ).fetchall()

        trades = []
        for symbol, action, amount, executed_at in rows:
            trades.append({
                "asset": symbol,
                "action": action.upper(),
                "amount": round(float(amount), 2),
                "time": executed_at.strftime("%Y-%m-%d %H:%M") if executed_at else "",
                "status": "Executed",
            })

        return {
            "portfolio_id": portfolio_id,
            "trades": trades,
        }

    finally:
        db.close()
@router.get("/explainability")
def get_portfolio_explainability(
    portfolio_id: int = Depends(get_current_user_portfolio_id),
):
    """
    Return SHAP explanations for current portfolio-relevant assets.
    For now, we explain all assets allowed in the portfolio.
    """
    db = SessionLocal()

    try:
        allowed_assets = db.execute(
            text("""
                SELECT a.id, a.symbol
                FROM portfolio_assets pa
                JOIN assets a ON pa.asset_id = a.id
                WHERE pa.portfolio_id = :portfolio_id
                ORDER BY a.symbol
            """),
            {"portfolio_id": portfolio_id}
        ).fetchall()

        explanations = []

        for asset_id, symbol in allowed_assets:
            explanation = get_top_shap_explanations(db, asset_id, top_n=3)

            if explanation is None:
                continue

            predicted_return = explanation["predicted_return"]
            reasons = explanation["reasons"]

            summary = (
                f"{symbol} prediction is driven mainly by "
                f"{', '.join([reason['feature'] for reason in reasons[:3]])}."
            )

            explanations.append({
                "symbol": symbol,
                "predicted_return": predicted_return,
                "reasons": reasons,
                "summary": summary,
            })

        return {
            "portfolio_id": portfolio_id,
            "explanations": explanations,
        }

    finally:
        db.close()
@router.get("/allocation")
def get_portfolio_allocation(
    portfolio_id: int = Depends(get_current_user_portfolio_id),
):
    """
    Return current portfolio allocation breakdown including cash.
    """
    db = SessionLocal()

    try:
        portfolio_row = db.execute(
            text("""
                SELECT current_cash
                FROM portfolios
                WHERE id = :portfolio_id
            """),
            {"portfolio_id": portfolio_id}
        ).fetchone()

        if portfolio_row is None:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        current_cash = float(portfolio_row[0])

        rows = db.execute(
            text("""
                SELECT 
                    a.symbol,
                    pp.quantity,
                    ph.close
                FROM portfolio_positions pp
                JOIN assets a ON pp.asset_id = a.id
                JOIN LATERAL (
                    SELECT close
                    FROM price_history
                    WHERE asset_id = pp.asset_id
                    ORDER BY date DESC
                    LIMIT 1
                ) ph ON TRUE
                WHERE pp.portfolio_id = :portfolio_id
                ORDER BY a.symbol
            """),
            {"portfolio_id": portfolio_id}
        ).fetchall()

        invested_value = 0.0
        asset_values = []

        for symbol, quantity, latest_close in rows:
            market_value = float(quantity) * float(latest_close)
            invested_value += market_value
            asset_values.append((symbol, market_value))

        total_value = current_cash + invested_value

        allocation = []

        cash_percent = (current_cash / total_value * 100.0) if total_value > 0 else 0.0
        allocation.append({
            "name": "Cash",
            "value": round(cash_percent, 2),
        })

        for symbol, market_value in asset_values:
            weight = (market_value / total_value * 100.0) if total_value > 0 else 0.0
            allocation.append({
                "name": symbol,
                "value": round(weight, 2),
            })

        return {
            "portfolio_id": portfolio_id,
            "allocation": allocation,
        }

    finally:
        db.close()
@router.get("/history")
def get_portfolio_history(
    portfolio_id: int = Depends(get_current_user_portfolio_id),
):
    """
    Return real portfolio history from stored portfolio snapshots.
    """
    db = SessionLocal()

    try:
        rows = db.execute(
            text("""
                SELECT created_at, total_value
                FROM portfolio_snapshots
                WHERE portfolio_id = :portfolio_id
                ORDER BY created_at ASC
                LIMIT 50
            """),
            {"portfolio_id": portfolio_id}
        ).fetchall()

        history = [
            {
                "label": created_at.strftime("%b %d %H:%M"),
                "value": float(total_value),
            }
            for created_at, total_value in rows
        ]

        return {
            "portfolio_id": portfolio_id,
            "history": history,
        }

    finally:
        db.close()