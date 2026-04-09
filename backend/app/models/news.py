from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)
    headline = Column(String, nullable=False)
    source = Column(String, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=False)
    url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    asset = relationship("Asset")