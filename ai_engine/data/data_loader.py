import pandas as pd
import yfinance as yf
from sqlalchemy import text

from ai_engine.data.db_client import SessionLocal


# List of assets we want to load into the system
ASSETS_TO_LOAD = [
    {"symbol": "AAPL", "name": "Apple Inc.", "asset_type": "stock", "market": "NASDAQ"},
    {"symbol": "MSFT", "name": "Microsoft Corporation", "asset_type": "stock", "market": "NASDAQ"},
    {"symbol": "NVDA", "name": "NVIDIA Corporation", "asset_type": "stock", "market": "NASDAQ"},
    {"symbol": "BTC-USD", "name": "Bitcoin", "asset_type": "crypto", "market": "CRYPTO"},
    {"symbol": "ETH-USD", "name": "Ethereum", "asset_type": "crypto", "market": "CRYPTO"},
    {"symbol": "GLD", "name": "SPDR Gold Shares", "asset_type": "etf", "market": "NYSEARCA"},
]


# Insert asset into DB if it does not exist, otherwise return existing ID
def upsert_asset(db, symbol: str, name: str, asset_type: str, market: str) -> int:
    # Check if asset already exists
    existing = db.execute(
        text("SELECT id FROM assets WHERE symbol = :symbol"),
        {"symbol": symbol}
    ).fetchone()

    if existing:
        return existing[0]

    # Insert new asset
    db.execute(
        text("""
            INSERT INTO assets (symbol, name, asset_type, market, is_active)
            VALUES (:symbol, :name, :asset_type, :market, true)
        """),
        {
            "symbol": symbol,
            "name": name,
            "asset_type": asset_type,
            "market": market,
        }
    )
    db.commit()

    # Retrieve inserted asset ID
    created = db.execute(
        text("SELECT id FROM assets WHERE symbol = :symbol"),
        {"symbol": symbol}
    ).fetchone()

    return created[0]


# Fetch historical market data using yfinance
def fetch_market_data(symbol: str, period: str = "5y", interval: str = "1d") -> pd.DataFrame:
    # Download OHLCV data
    df = yf.download(symbol, period=period, interval=interval, auto_adjust=False, progress=False)

    if df.empty:
        return df

    df = df.reset_index()

    # Handle multi-index columns if returned by yfinance
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

    # Standardize column names
    rename_map = {
        "Date": "date",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
    }
    df = df.rename(columns=rename_map)

    # Keep only required columns
    df = df[["date", "open", "high", "low", "close", "volume"]].copy()

    # Convert date format
    df["date"] = pd.to_datetime(df["date"]).dt.date

    # Remove rows with missing critical values
    df = df.dropna(subset=["date", "open", "high", "low", "close"])

    return df


# Insert price data into database while avoiding duplicates
def insert_price_history(db, asset_id: int, df: pd.DataFrame) -> int:
    inserted = 0

    for _, row in df.iterrows():
        # Check if this date already exists for the asset
        existing = db.execute(
            text("""
                SELECT id
                FROM price_history
                WHERE asset_id = :asset_id AND date = :date
            """),
            {
                "asset_id": asset_id,
                "date": row["date"],
            }
        ).fetchone()

        # Skip duplicate entries
        if existing:
            continue

        # Insert new price row
        db.execute(
            text("""
                INSERT INTO price_history (asset_id, date, open, high, low, close, volume)
                VALUES (:asset_id, :date, :open, :high, :low, :close, :volume)
            """),
            {
                "asset_id": asset_id,
                "date": row["date"],
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row["volume"]) if pd.notna(row["volume"]) else None,
            }
        )
        inserted += 1

    db.commit()
    return inserted


# Main pipeline execution
def main():
    db = SessionLocal()

    try:
        total_inserted = 0

        for asset in ASSETS_TO_LOAD:
            print(f"Loading {asset['symbol']}...")

            # Ensure asset exists in DB
            asset_id = upsert_asset(
                db=db,
                symbol=asset["symbol"],
                name=asset["name"],
                asset_type=asset["asset_type"],
                market=asset["market"],
            )

            # Fetch historical data
            df = fetch_market_data(asset["symbol"])

            if df.empty:
                print(f"No data returned for {asset['symbol']}")
                continue

            # Insert data into DB
            inserted = insert_price_history(db, asset_id, df)
            total_inserted += inserted

            print(f"Inserted {inserted} rows for {asset['symbol']}")

        print(f"\nDone. Total new price rows inserted: {total_inserted}")

    finally:
        db.close()


# Run script
if __name__ == "__main__":
    main()