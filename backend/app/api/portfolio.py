from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user_portfolio_id
from ai_engine.optimization.decision_engine import main as run_decision_engine
from ai_engine.services.portfolio_snapshots import create_portfolio_snapshot
from app.services.portfolio_valuation import compute_current_portfolio_value

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


@router.post("/rebalance")
def rebalance_portfolio(
    portfolio_id: int = Depends(get_current_user_portfolio_id),
):
    """
    Run the AI decision engine for the authenticated user's portfolio.
    """
    try:
        run_decision_engine(portfolio_id=portfolio_id)

        return {
            "message": "Rebalance completed successfully",
            "portfolio_id": portfolio_id,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rebalance failed: {str(e)}")
    
@router.post("/snapshot")
def snapshot_portfolio_value(
    portfolio_id: int = Depends(get_current_user_portfolio_id),
):
    """
    Compute and store the current value snapshot for the authenticated user's portfolio.
    """
    from app.db.session import SessionLocal

    db = SessionLocal()

    try:
        total_value = compute_current_portfolio_value(db, portfolio_id)

        create_portfolio_snapshot(
            db=db,
            portfolio_id=portfolio_id,
            total_value=total_value,
        )

        return {
            "message": "Portfolio snapshot created successfully",
            "portfolio_id": portfolio_id,
            "total_value": total_value,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Snapshot failed: {str(e)}")

    finally:
        db.close()