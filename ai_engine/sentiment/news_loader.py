import yfinance as yf
from datetime import datetime, timezone
from sqlalchemy import text

from ai_engine.data.db_client import SessionLocal


def get_assets(db):
    """
    Load all assets from the database.
    """
    rows = db.execute(
        text("""
            SELECT id, symbol
            FROM assets
            ORDER BY id
        """)
    ).fetchall()

    return rows


def insert_news_item(db, asset_id: int, headline: str, source: str, published_at, url: str):
    """
    Insert a news item if the same headline for the same asset does not already exist.
    """
    existing = db.execute(
        text("""
            SELECT id
            FROM news
            WHERE asset_id = :asset_id AND headline = :headline
        """),
        {
            "asset_id": asset_id,
            "headline": headline,
        }
    ).fetchone()

    if existing:
        return None

    db.execute(
        text("""
            INSERT INTO news (asset_id, headline, source, published_at, url)
            VALUES (:asset_id, :headline, :source, :published_at, :url)
        """),
        {
            "asset_id": asset_id,
            "headline": headline,
            "source": source,
            "published_at": published_at,
            "url": url,
        }
    )
    db.commit()

    row = db.execute(
        text("""
            SELECT id
            FROM news
            WHERE asset_id = :asset_id AND headline = :headline
            ORDER BY id DESC
            LIMIT 1
        """),
        {
            "asset_id": asset_id,
            "headline": headline,
        }
    ).fetchone()

    return row[0]


def fetch_yfinance_news(symbol: str):
    """
    Fetch news from yfinance ticker feed.
    Returns a list of dictionaries.
    """
    ticker = yf.Ticker(symbol)

    try:
        news_items = ticker.news
    except Exception:
        news_items = []

    return news_items or []


def normalize_published_time(raw_item):
    """
    Convert yfinance published time into a timezone-aware datetime.
    """
    # yfinance often uses providerPublishTime (unix timestamp)
    ts = raw_item.get("providerPublishTime")

    if ts is not None:
        return datetime.fromtimestamp(ts, tz=timezone.utc)

    # fallback to now if unavailable
    return datetime.now(timezone.utc)


def main():
    db = SessionLocal()

    try:
        assets = get_assets(db)
        total_inserted = 0

        for asset_id, symbol in assets:
            print(f"Fetching news for {symbol}...")

            items = fetch_yfinance_news(symbol)
            inserted_for_asset = 0

            for item in items:
                content = item.get("content", {})

                headline = content.get("title")
                if not headline:
                    continue

                source = content.get("provider", {}).get("displayName", "Unknown")

                url = content.get("canonicalUrl", {}).get("url")

                # Fix published date
                pub_date_str = content.get("pubDate")

                from datetime import datetime, timezone

                if pub_date_str:
                    try:
                        published_at = datetime.fromisoformat(pub_date_str.replace("Z", "+00:00"))
                    except Exception:
                        published_at = datetime.now(timezone.utc)
                else:
                    published_at = datetime.now(timezone.utc)
                    
                news_id = insert_news_item(
                    db=db,
                    asset_id=asset_id,
                    headline=headline,
                    source=source,
                    published_at=published_at,
                    url=url,
                )

                if news_id is not None:
                    inserted_for_asset += 1
                    total_inserted += 1

            print(f"Inserted {inserted_for_asset} news rows for {symbol}")

        print(f"\nDone. Total new news rows inserted: {total_inserted}")

    finally:
        db.close()


if __name__ == "__main__":
    main()