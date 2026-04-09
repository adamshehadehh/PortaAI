import pandas as pd
from sqlalchemy import text

from ai_engine.data.db_client import SessionLocal


# Load all price history for one asset from the database
def load_price_history_for_asset(db, asset_id: int) -> pd.DataFrame:
    query = text("""
        SELECT date, open, high, low, close, volume
        FROM price_history
        WHERE asset_id = :asset_id
        ORDER BY date
    """)

    rows = db.execute(query, {"asset_id": asset_id}).fetchall()

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows, columns=["date", "open", "high", "low", "close", "volume"])
    df["date"] = pd.to_datetime(df["date"])

    # Convert numeric values from Decimal to float for pandas calculations
    numeric_cols = ["open", "high", "low", "close", "volume"]
    for col in numeric_cols:
        df[col] = df[col].astype(float)

    return df

def get_average_sentiment_until_date(db, asset_id: int, feature_date, limit: int = 10) -> float:
    """
    Compute average sentiment for an asset using only sentiment rows
    available on or before the given feature date.

    This makes sentiment time-dependent instead of static.
    """
    row = db.execute(
        text("""
            SELECT AVG(sentiment_score)
            FROM (
                SELECT s.sentiment_score
                FROM sentiment_scores s
                JOIN news n ON s.news_id = n.id
                WHERE s.asset_id = :asset_id
                  AND n.published_at::date <= :feature_date
                ORDER BY n.published_at DESC
                LIMIT :limit
            ) recent_scores
        """),
        {
            "asset_id": asset_id,
            "feature_date": feature_date,
            "limit": limit,
        }
    ).fetchone()

    return float(row[0]) if row and row[0] is not None else 0.0

# Compute technical and statistical features from raw price data
def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    feature_df = df.copy()

    # Daily return
    feature_df["return_1d"] = feature_df["close"].pct_change()

    # 7-day return
    feature_df["return_7d"] = feature_df["close"].pct_change(periods=7)

    # 7-day rolling volatility of daily returns
    feature_df["volatility_7d"] = feature_df["return_1d"].rolling(window=7).std()

    # Moving averages
    feature_df["ma_7"] = feature_df["close"].rolling(window=7).mean()
    feature_df["ma_30"] = feature_df["close"].rolling(window=30).mean()

    # 7-day momentum
    feature_df["momentum_7d"] = feature_df["close"] - feature_df["close"].shift(7)

    # RSI(14)
    delta = feature_df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()

    rs = avg_gain / avg_loss
    feature_df["rsi_14"] = 100 - (100 / (1 + rs))
    # We will fill this later using date-aware sentiment lookup
    feature_df["sentiment_aggregate"] = 0.0
    return feature_df

def attach_time_dependent_sentiment(db, asset_id: int, feature_df: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    """
    For each feature row date, attach the average sentiment available
    up to that date.
    """
    if feature_df.empty:
        return feature_df

    sentiment_values = []

    for _, row in feature_df.iterrows():
        feature_date = row["date"].date()

        avg_sentiment = get_average_sentiment_until_date(
            db=db,
            asset_id=asset_id,
            feature_date=feature_date,
            limit=limit
        )

        sentiment_values.append(avg_sentiment)

    feature_df["sentiment_aggregate"] = sentiment_values
    return feature_df

# Insert computed features into DB, skipping duplicates
def insert_engineered_features(db, asset_id: int, df: pd.DataFrame) -> int:
    inserted = 0

    for _, row in df.iterrows():
        existing = db.execute(
            text("""
                SELECT id
                FROM engineered_features
                WHERE asset_id = :asset_id AND date = :date
            """),
            {
                "asset_id": asset_id,
                "date": row["date"].date(),
            }
        ).fetchone()

        if existing:
            continue

        db.execute(
            text("""
                INSERT INTO engineered_features (
                    asset_id, date, return_1d, return_7d, volatility_7d,
                    ma_7, ma_30, momentum_7d, rsi_14, sentiment_aggregate
                )
                VALUES (
                    :asset_id, :date, :return_1d, :return_7d, :volatility_7d,
                    :ma_7, :ma_30, :momentum_7d, :rsi_14, :sentiment_aggregate
                )
            """),
            {
                "asset_id": asset_id,
                "date": row["date"].date(),
                "return_1d": None if pd.isna(row["return_1d"]) else float(row["return_1d"]),
                "return_7d": None if pd.isna(row["return_7d"]) else float(row["return_7d"]),
                "volatility_7d": None if pd.isna(row["volatility_7d"]) else float(row["volatility_7d"]),
                "ma_7": None if pd.isna(row["ma_7"]) else float(row["ma_7"]),
                "ma_30": None if pd.isna(row["ma_30"]) else float(row["ma_30"]),
                "momentum_7d": None if pd.isna(row["momentum_7d"]) else float(row["momentum_7d"]),
                "rsi_14": None if pd.isna(row["rsi_14"]) else float(row["rsi_14"]),
                "sentiment_aggregate": None if pd.isna(row["sentiment_aggregate"]) else float(row["sentiment_aggregate"]),
            }
        )
        inserted += 1

    db.commit()
    return inserted


# Get all assets currently stored in the DB
def get_all_assets(db):
    rows = db.execute(
        text("SELECT id, symbol FROM assets ORDER BY id")
    ).fetchall()
    return rows


def main():
    db = SessionLocal()

    try:
        total_inserted = 0
        assets = get_all_assets(db)

        for asset_id, symbol in assets:
            print(f"Engineering features for {symbol}...")

            price_df = load_price_history_for_asset(db, asset_id)

            if price_df.empty:
                print(f"No price history found for {symbol}")
                continue

            # Compute technical features first
            feature_df = compute_features(price_df)

            # Attach date-aware sentiment feature
            feature_df = attach_time_dependent_sentiment(db, asset_id, feature_df, limit=10)

            # Optional preview print of latest sentiment value
            latest_sentiment = feature_df["sentiment_aggregate"].iloc[-1] if not feature_df.empty else 0.0
            print(f"Latest time-dependent sentiment for {symbol}: {latest_sentiment:.4f}")
            
            inserted = insert_engineered_features(db, asset_id, feature_df)

            total_inserted += inserted
            print(f"Inserted {inserted} feature rows for {symbol}")

        print(f"\nDone. Total engineered feature rows inserted: {total_inserted}")

    finally:
        db.close()


if __name__ == "__main__":
    main()