import os
import joblib
import pandas as pd
from sqlalchemy import text
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

from ai_engine.data.db_client import SessionLocal


MODEL_DIR = "ai_engine/forecasting/saved_models"


def load_dataset(db, asset_id: int) -> pd.DataFrame:
    query = text("""
        SELECT 
            ef.date,
            ef.return_1d,
            ef.return_7d,
            ef.volatility_7d,
            ef.ma_7,
            ef.ma_30,
            ef.momentum_7d,
            ef.rsi_14,
            ph.close
        FROM engineered_features ef
        JOIN price_history ph 
            ON ef.asset_id = ph.asset_id AND ef.date = ph.date
        WHERE ef.asset_id = :asset_id
        ORDER BY ef.date
    """)

    rows = db.execute(query, {"asset_id": asset_id}).fetchall()

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows, columns=[
        "date", "return_1d", "return_7d", "volatility_7d",
        "ma_7", "ma_30", "momentum_7d", "rsi_14", "close"
    ])

    df["date"] = pd.to_datetime(df["date"])

    # Convert DB numeric values into floats for sklearn/pandas
    for col in df.columns:
        if col != "date":
            df[col] = df[col].astype(float)

    return df


def create_target(df: pd.DataFrame) -> pd.DataFrame:
    # Predict next-day return
    df["target"] = df["close"].pct_change().shift(-1)
    df = df.dropna()
    return df


def time_series_split(df: pd.DataFrame):
    n = len(df)

    train_end = int(n * 0.70)
    val_end = int(n * 0.85)

    train = df.iloc[:train_end]
    val = df.iloc[train_end:val_end]
    test = df.iloc[val_end:]

    return train, val, test


def evaluate(y_true, y_pred, name="Set"):
    mse = mean_squared_error(y_true, y_pred)

    # Directional accuracy = did we correctly predict positive vs negative return
    direction_true = (y_true > 0).astype(int)
    direction_pred = (y_pred > 0).astype(int)
    accuracy = (direction_true == direction_pred).mean()

    print(f"{name} MSE: {mse}")
    print(f"{name} Directional Accuracy: {accuracy:.2f}")
    print("-" * 40)

    return {"mse": float(mse), "directional_accuracy": float(accuracy)}


def get_feature_columns():
    return [
        "return_1d",
        "return_7d",
        "volatility_7d",
        "ma_7",
        "ma_30",
        "momentum_7d",
        "rsi_14",
    ]


def train_model(train: pd.DataFrame):
    features = get_feature_columns()

    X_train = train[features]
    y_train = train["target"]

    # Reduced-complexity model to improve generalization
    model = RandomForestRegressor(
        n_estimators=50,
        max_depth=5,
        min_samples_split=10,
        random_state=42
    )

    model.fit(X_train, y_train)
    return model


def build_training_pipeline(db, asset_id: int):
    df = load_dataset(db, asset_id)

    if df.empty:
        raise ValueError(f"No dataset found for asset_id={asset_id}")

    df = create_target(df)
    train, val, test = time_series_split(df)

    model = train_model(train)

    print("\nEvaluation Results:\n")
    train_metrics = evaluate(train["target"], model.predict(train[get_feature_columns()]), "Train")
    val_metrics = evaluate(val["target"], model.predict(val[get_feature_columns()]), "Validation")
    test_metrics = evaluate(test["target"], model.predict(test[get_feature_columns()]), "Test")

    return {
        "model": model,
        "features": get_feature_columns(),
        "metrics": {
            "train": train_metrics,
            "validation": val_metrics,
            "test": test_metrics,
        }
    }


def get_model_path(asset_id: int) -> str:
    os.makedirs(MODEL_DIR, exist_ok=True)
    return os.path.join(MODEL_DIR, f"forecast_model_asset_{asset_id}.joblib")


def save_model(asset_id: int, model, features, metrics):
    payload = {
        "model": model,
        "features": features,
        "metrics": metrics,
        "asset_id": asset_id,
    }
    model_path = get_model_path(asset_id)
    joblib.dump(payload, model_path)
    return model_path


def load_saved_model(asset_id: int):
    model_path = get_model_path(asset_id)

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"No saved model found for asset_id={asset_id}. Train and save the model first."
        )

    return joblib.load(model_path)


def train_and_save_asset_model(asset_id: int):
    db = SessionLocal()

    try:
        training_output = build_training_pipeline(db, asset_id)
        model_path = save_model(
            asset_id=asset_id,
            model=training_output["model"],
            features=training_output["features"],
            metrics=training_output["metrics"],
        )

        print(f"Model saved successfully at: {model_path}")
        return model_path

    finally:
        db.close()


def main():
    db = SessionLocal()
    try:
        rows = db.execute(text("SELECT id, symbol FROM assets ORDER BY id")).fetchall()
    finally:
        db.close()

    for asset_id, symbol in rows:
        print(f"\nTraining model for {symbol}...")
        train_and_save_asset_model(asset_id)

if __name__ == "__main__":
    main()