from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base


class PortfolioRun(Base):
    __tablename__ = "portfolio_runs"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    run_type = Column(String, nullable=False)  # rebalance / backtest
    status = Column(String, nullable=False, default="completed")
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(String, nullable=True)

    portfolio = relationship("Portfolio")