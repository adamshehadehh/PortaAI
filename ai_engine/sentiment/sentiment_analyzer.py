from sqlalchemy import text
from transformers import pipeline

from ai_engine.data.db_client import SessionLocal


# Load a finance-oriented sentiment model
# If this model fails in your environment, we can switch to another one.
sentiment_pipeline = pipeline(
    "text-classification",
    model="C:/Users/adams/PortaAI/finbert_model"
)


def get_unscored_news(db):
    """
    Load news items that do not yet have a sentiment score.
    """
    rows = db.execute(
        text("""
            SELECT n.id, n.asset_id, n.headline
            FROM news n
            LEFT JOIN sentiment_scores s ON n.id = s.news_id
            WHERE s.id IS NULL
            ORDER BY n.id
        """)
    ).fetchall()

    return rows


def normalize_label(label: str):
    """
    Normalize transformer label names into positive / neutral / negative.
    """
    label = label.lower()

    if "positive" in label:
        return "positive"
    if "negative" in label:
        return "negative"
    return "neutral"


def signed_score(label: str, score: float):
    """
    Convert model output into a signed numeric sentiment score.
    Positive -> +score
    Negative -> -score
    Neutral  -> 0
    """
    if label == "positive":
        return score
    if label == "negative":
        return -score
    return 0.0


def save_sentiment_score(db, news_id: int, asset_id: int, sentiment_label: str, sentiment_score: float):
    """
    Save sentiment result into sentiment_scores table.
    """
    db.execute(
        text("""
            INSERT INTO sentiment_scores (
                news_id, asset_id, sentiment_label, sentiment_score, model_version
            )
            VALUES (
                :news_id, :asset_id, :sentiment_label, :sentiment_score, :model_version
            )
        """),
        {
            "news_id": news_id,
            "asset_id": asset_id,
            "sentiment_label": sentiment_label,
            "sentiment_score": sentiment_score,
            "model_version": "ProsusAI/finbert",
        }
    )
    db.commit()


def main():
    db = SessionLocal()

    try:
        rows = get_unscored_news(db)

        if not rows:
            print("No unscored news found.")
            return

        total_scored = 0

        for news_id, asset_id, headline in rows:
            result = sentiment_pipeline(headline)[0]

            raw_label = result["label"]
            raw_score = float(result["score"])

            label = normalize_label(raw_label)
            score = signed_score(label, raw_score)

            save_sentiment_score(
                db=db,
                news_id=news_id,
                asset_id=asset_id,
                sentiment_label=label,
                sentiment_score=score,
            )

            total_scored += 1
            print(f"Scored news_id={news_id} | label={label} | score={score:.4f}")

        print(f"\nDone. Total sentiment rows inserted: {total_scored}")

    finally:
        db.close()


if __name__ == "__main__":
    main()