import pandas as pd
import shap
from sqlalchemy import text

from ai_engine.data.db_client import SessionLocal
from ai_engine.forecasting.model import load_saved_model


# Load latest engineered features for one asset.
# These are the same inputs used by the forecasting model at inference time.
def load_latest_features(db, asset_id: int):
    row = db.execute(
        text("""
            SELECT 
                return_1d,
                return_7d,
                volatility_7d,
                ma_7,
                ma_30,
                momentum_7d,
                rsi_14,
                sentiment_aggregate
            FROM engineered_features
            WHERE asset_id = :asset_id
            ORDER BY date DESC
            LIMIT 1
        """),
        {"asset_id": asset_id}
    ).fetchone()

    return row


# Get symbol for nicer printed output.
def get_asset_symbol(db, asset_id: int) -> str:
    row = db.execute(
        text("""
            SELECT symbol
            FROM assets
            WHERE id = :asset_id
        """),
        {"asset_id": asset_id}
    ).fetchone()

    return row[0] if row else f"asset_{asset_id}"


# Build a one-row dataframe using the exact feature names expected by the model.
def build_latest_feature_frame(latest_row):
    return pd.DataFrame([{
        "return_1d": float(latest_row[0]) if latest_row[0] is not None else 0.0,
        "return_7d": float(latest_row[1]) if latest_row[1] is not None else 0.0,
        "volatility_7d": float(latest_row[2]) if latest_row[2] is not None else 0.0,
        "ma_7": float(latest_row[3]) if latest_row[3] is not None else 0.0,
        "ma_30": float(latest_row[4]) if latest_row[4] is not None else 0.0,
        "momentum_7d": float(latest_row[5]) if latest_row[5] is not None else 0.0,
        "rsi_14": float(latest_row[6]) if latest_row[6] is not None else 0.0,
        "sentiment_aggregate": float(latest_row[7]) if latest_row[7] is not None else 0.0,
    }])


# Explain one asset's latest prediction using SHAP.
def explain_latest_prediction(asset_id: int):
    db = SessionLocal()

    try:
        symbol = get_asset_symbol(db, asset_id)
        saved = load_saved_model(asset_id)

        model = saved["model"]
        features = saved["features"]

        latest_row = load_latest_features(db, asset_id)
        if latest_row is None:
            print(f"No latest features found for {symbol}")
            return

        X_latest = build_latest_feature_frame(latest_row)
        X_latest = X_latest[features]

        # Predict latest next-day return.
        prediction = float(model.predict(X_latest)[0])

        # TreeExplainer works well for XGBoost tree-based models.
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_latest)

        # Expected/base value is the average model output before feature contributions.
        base_value = explainer.expected_value
        if isinstance(base_value, (list, tuple)):
            base_value = base_value[0]

        print(f"\nSHAP explanation for {symbol}")
        print(f"Predicted next return: {prediction:.6f}")
        print(f"Base value: {float(base_value):.6f}\n")

        # Build a readable table of feature contributions.
        contributions = []
        for i, feature_name in enumerate(features):
            feature_value = float(X_latest.iloc[0][feature_name])
            feature_shap = float(shap_values[0][i])
            contributions.append((feature_name, feature_value, feature_shap))

        # Sort by absolute contribution so the most important features appear first.
        contributions.sort(key=lambda x: abs(x[2]), reverse=True)

        # 🔥 Top 3 most important features (clean explanation)
        print("\nTop 3 most important features:")
        for feature_name, feature_value, feature_shap in contributions[:3]:
            if feature_shap > 0:
                direction = "pushes UP"
            elif feature_shap < 0:
                direction = "pushes DOWN"
            else:
                direction = "has NO EFFECT"
            print(
                f"- {feature_name}: value={feature_value:.6f}, "
                f"shap={feature_shap:.6f} -> {direction}"
            )

        # 🔍 Full breakdown (for debugging / detailed analysis)
        print("\nAll feature contributions:")
        for feature_name, feature_value, feature_shap in contributions:
            if feature_shap > 0:
                direction = "pushes UP"
            elif feature_shap < 0:
                direction = "pushes DOWN"
            else:
                direction = "has NO EFFECT"
            print(
                f"- {feature_name}: value={feature_value:.6f}, "
                f"shap={feature_shap:.6f} -> {direction}"
            )
    finally:
        db.close()


def main():
    db = SessionLocal()
    try:
        rows = db.execute(text("SELECT id FROM assets")).fetchall()
        for row in rows:
            asset_id = row[0]
            explain_latest_prediction(asset_id)
    finally:
        db.close()

if __name__ == "__main__":
    main()