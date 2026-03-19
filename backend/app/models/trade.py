from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_run_id = Column(Integer, ForeignKey("portfolio_runs.id"), nullable=False)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    action = Column(String, nullable=False)  # buy / sell / hold
    quantity = Column(Numeric(20, 8), nullable=False)
    price = Column(Numeric(20, 8), nullable=False)
    amount = Column(Numeric(20, 8), nullable=False)
    executed_at = Column(DateTime(timezone=True), server_default=func.now())

    portfolio_run = relationship("PortfolioRun")
    portfolio = relationship("Portfolio")
    asset = relationship("Asset")