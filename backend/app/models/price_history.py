from sqlalchemy import Column, Integer, ForeignKey, Date, Numeric
from sqlalchemy.orm import relationship

from app.db.base import Base


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    date = Column(Date, nullable=False)

    open = Column(Numeric(15, 5), nullable=False)
    high = Column(Numeric(15, 5), nullable=False)
    low = Column(Numeric(15, 5), nullable=False)
    close = Column(Numeric(15, 5), nullable=False)
    volume = Column(Numeric(20, 2), nullable=True)

    asset = relationship("Asset")