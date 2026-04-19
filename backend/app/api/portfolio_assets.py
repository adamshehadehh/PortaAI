from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text

from app.api.deps import get_current_user_portfolio_id
from app.db.session import SessionLocal

router = APIRouter(prefix="/api/portfolio/assets", tags=["portfolio-assets"])


class PortfolioAssetsUpdateRequest(BaseModel):
    asset_ids: list[int]


@router.get("")
def get_portfolio_assets(
    portfolio_id: int = Depends(get_current_user_portfolio_id),
):
    db = SessionLocal()

    try:
        selected_rows = db.execute(
            text("""
                SELECT a.id, a.symbol
                FROM portfolio_assets pa
                JOIN assets a ON pa.asset_id = a.id
                WHERE pa.portfolio_id = :portfolio_id
                ORDER BY a.symbol ASC
            """),
            {"portfolio_id": portfolio_id}
        ).fetchall()

        all_rows = db.execute(
            text("""
                SELECT id, symbol
                FROM assets
                ORDER BY symbol ASC
            """)
        ).fetchall()

        return {
            "portfolio_id": portfolio_id,
            "selected_asset_ids": [int(row[0]) for row in selected_rows],
            "selected_assets": [
                {"id": int(row[0]), "symbol": row[1]} for row in selected_rows
            ],
            "all_assets": [
                {"id": int(row[0]), "symbol": row[1]} for row in all_rows
            ],
        }

    finally:
        db.close()


@router.put("")
def update_portfolio_assets(
    payload: PortfolioAssetsUpdateRequest,
    portfolio_id: int = Depends(get_current_user_portfolio_id),
):
    db = SessionLocal()

    try:
        db.execute(
            text("""
                DELETE FROM portfolio_assets
                WHERE portfolio_id = :portfolio_id
            """),
            {"portfolio_id": portfolio_id}
        )

        for asset_id in payload.asset_ids:
            db.execute(
                text("""
                    INSERT INTO portfolio_assets (portfolio_id, asset_id, added_at)
                    VALUES (:portfolio_id, :asset_id, NOW())
                """),
                {
                    "portfolio_id": portfolio_id,
                    "asset_id": asset_id,
                }
            )

        db.commit()

        return {
            "message": "Portfolio assets updated successfully",
            "portfolio_id": portfolio_id,
            "asset_ids": payload.asset_ids,
        }

    finally:
        db.close()