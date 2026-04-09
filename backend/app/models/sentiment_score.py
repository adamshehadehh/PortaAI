from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base


class SentimentScore(Base):
    __tablename__ = "sentiment_scores"

    id = Column(Integer, primary_key=True, index=True)
    news_id = Column(Integer, ForeignKey("news.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    sentiment_label = Column(String, nullable=False)   # positive / neutral / negative
    sentiment_score = Column(Numeric(10, 6), nullable=False)
    model_version = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    news = relationship("News")
    asset = relationship("Asset")