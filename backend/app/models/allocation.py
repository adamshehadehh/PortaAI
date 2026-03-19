from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Allocation(Base):
    __tablename__ = "allocations"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_run_id = Column(Integer, ForeignKey("portfolio_runs.id"), nullable=False)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)
    target_weight = Column(Numeric(10, 6), nullable=False)
    current_weight = Column(Numeric(10, 6), nullable=True)
    reason_summary = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    portfolio_run = relationship("PortfolioRun")
    portfolio = relationship("Portfolio")
    asset = relationship("Asset")