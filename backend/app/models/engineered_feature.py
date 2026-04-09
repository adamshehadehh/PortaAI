from sqlalchemy import Column, Integer, ForeignKey, Date, Numeric, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base


class EngineeredFeature(Base):
    __tablename__ = "engineered_features"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    date = Column(Date, nullable=False)

    return_1d = Column(Numeric(15, 8), nullable=True)
    return_7d = Column(Numeric(15, 8), nullable=True)
    volatility_7d = Column(Numeric(15, 8), nullable=True)
    ma_7 = Column(Numeric(15, 5), nullable=True)
    ma_30 = Column(Numeric(15, 5), nullable=True)
    momentum_7d = Column(Numeric(15, 8), nullable=True)
    rsi_14 = Column(Numeric(15, 5), nullable=True)
    sentiment_aggregate = Column(Numeric(15, 8), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    asset = relationship("Asset")