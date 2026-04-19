from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user_portfolio_id
from ai_engine.optimization.decision_engine import main as run_decision_engine
from ai_engine.services.portfolio_snapshots import create_portfolio_snapshot
from app.services.portfolio_valuation import compute_current_portfolio_value
from app.db.session import SessionLocal
from sqlalchemy import text

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


@router.post("/rebalance")
def rebalance_portfolio(
    portfolio_id: int = Depends(get_current_user_portfolio_id),
):
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
            raise HTTPException(
                status_code=400,
                detail="No assets selected and no holdings to liquidate. Please add assets in Settings before rebalancing."
            )

        run_decision_engine(portfolio_id=portfolio_id)

        return {
            "message": "Rebalance completed successfully",
            "portfolio_id": portfolio_id,
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rebalance failed: {str(e)}")

    finally:
        db.close()
        
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