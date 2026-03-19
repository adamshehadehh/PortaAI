from sqlalchemy import Column, Integer, String, Boolean

from app.db.base import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    asset_type = Column(String, nullable=False)  # stock, crypto, etf, metal
    market = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)