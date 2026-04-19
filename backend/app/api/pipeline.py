from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_user_id
from ai_engine.data.data_loader import main as run_data_refresh
from ai_engine.features.feature_engineering import main as run_feature_refresh
from ai_engine.forecasting.model import main as run_model_training
from app.api.deps import get_current_user_id, get_current_user_portfolio_id
from app.db.session import SessionLocal
from app.services.portfolio_valuation import compute_current_portfolio_value
from ai_engine.services.portfolio_snapshots import create_portfolio_snapshot
from ai_engine.optimization.decision_engine import main as run_decision_engine
from sqlalchemy import text

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])


@router.post("/data-refresh")
def refresh_market_data(
    user_id: int = Depends(get_current_user_id),
):
    """
    Trigger market data refresh and update price_history.
    Protected endpoint for authenticated use.
    """
    try:
        run_data_refresh()

        return {
            "message": "Market data refresh completed successfully",
            "triggered_by_user_id": user_id,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data refresh failed: {str(e)}")
@router.post("/feature-refresh")
def refresh_engineered_features(
    user_id: int = Depends(get_current_user_id),
):
    """
    Trigger engineered feature refresh from the latest market data.
    Protected endpoint for authenticated use.
    """
    try:
        run_feature_refresh()

        return {
            "message": "Feature refresh completed successfully",
            "triggered_by_user_id": user_id,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feature refresh failed: {str(e)}")
@router.post("/train")
def train_forecasting_model(
    user_id: int = Depends(get_current_user_id),
):
    """
    Trigger forecasting model training using the latest engineered features.
    Protected endpoint for authenticated use.
    """
    try:
        run_model_training()

        return {
            "message": "Model training completed successfully",
            "triggered_by_user_id": user_id,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model training failed: {str(e)}")
@router.post("/daily-run")
def run_daily_pipeline(
    user_id: int = Depends(get_current_user_id),
    portfolio_id: int = Depends(get_current_user_portfolio_id),
):
    """
    Run the full daily pipeline:
    1. refresh market data
    2. refresh engineered features
    3. retrain forecasting model
    4. create a portfolio value snapshot
    """
    db = SessionLocal()

    try:
        run_data_refresh()
        run_feature_refresh()
        run_model_training()

        total_value = compute_current_portfolio_value(db, portfolio_id)
        create_portfolio_snapshot(
            db=db,
            portfolio_id=portfolio_id,
            total_value=total_value,
        )

        return {
            "message": "Daily pipeline completed successfully",
            "triggered_by_user_id": user_id,
            "portfolio_id": portfolio_id,
            "total_value": total_value,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Daily pipeline failed: {str(e)}")

    finally:
        db.close()
        
@router.post("/weekly-run")
def run_weekly_pipeline(
    user_id: int = Depends(get_current_user_id),
    portfolio_id: int = Depends(get_current_user_portfolio_id),
):
    """
    Run the weekly pipeline:
    - rebalance portfolio
    - snapshot handled inside decision engine
    """
    db = SessionLocal()

    try:
        selected_count_row = db.execute(
            text("""
                SELECT COUNT(*)
                FROM portfolio_assets
                WHERE portfolio_id = :portfolio_id
            """),
            {"portfolio_id": portfolio_id}
        ).fetchone()

        selected_count = int(selected_count_row[0]) if selected_count_row else 0

        holdings_count_row = db.execute(
            text("""
                SELECT COUNT(*)
                FROM portfolio_positions
                WHERE portfolio_id = :portfolio_id
                  AND quantity > 0
            """),
            {"portfolio_id": portfolio_id}
        ).fetchone()

        holdings_count = int(holdings_count_row[0]) if holdings_count_row else 0

        if selected_count == 0 and holdings_count == 0:
            return {
                "message": "Weekly pipeline skipped: no assets selected and no holdings to liquidate.",
                "triggered_by_user_id": user_id,
                "portfolio_id": portfolio_id,
            }

        run_decision_engine(portfolio_id=portfolio_id)

        return {
            "message": "Weekly pipeline completed successfully",
            "triggered_by_user_id": user_id,
            "portfolio_id": portfolio_id,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Weekly pipeline failed: {str(e)}"
        )

    finally:
        db.close()