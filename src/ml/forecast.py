import pandas as pd
from prophet import Prophet
from sqlalchemy import text
from src.utils.database import engine
import logging

logger = logging.getLogger(__name__)

def get_training_data(city_name: str) -> pd.DataFrame:
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT
                p.timestamp as ds,
                p.score as y
            FROM pulse_scores p
            JOIN cities c ON p.city_id = c.id
            WHERE c.name = :city_name
            ORDER BY p.timestamp ASC
        """), {"city_name": city_name})
        rows = result.fetchall()

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows, columns=["ds", "y"])
    df["ds"] = pd.to_datetime(df["ds"]).dt.tz_localize(None)
    return df

def forecast_city(city_name: str, hours_ahead: int = 24) -> dict | None:
    try:
        df = get_training_data(city_name)

        if len(df) < 10:
            logger.warning(f"Not enough data for {city_name}: {len(df)} points")
            return None

        model = Prophet(
            changepoint_prior_scale=0.05,
            seasonality_prior_scale=10,
            daily_seasonality=True,
            weekly_seasonality=False,
            yearly_seasonality=False,
            interval_width=0.80
        )

        model.fit(df)

        future = model.make_future_dataframe(
            periods=hours_ahead,
            freq="h"
        )
        forecast = model.predict(future)

        last_actual = df["ds"].max()
        future_only = forecast[forecast["ds"] > last_actual].head(hours_ahead)

        next_24h = future_only[["ds", "yhat", "yhat_lower", "yhat_upper"]].to_dict("records")

        next_score = float(next_24h[0]["yhat"]) if next_24h else None
        next_score = max(0, min(100, next_score)) if next_score else None

        trend = "improving" if next_score and next_score > df["y"].iloc[-1] else "declining"

        return {
            "city": city_name,
            "current_score": float(df["y"].iloc[-1]),
            "predicted_next": round(next_score, 1) if next_score else None,
            "trend": trend,
            "data_points_used": len(df),
            "forecast_24h": [
                {
                    "timestamp": str(row["ds"]),
                    "predicted": round(max(0, min(100, row["yhat"])), 1),
                    "lower": round(max(0, row["yhat_lower"]), 1),
                    "upper": round(min(100, row["yhat_upper"]), 1)
                }
                for row in next_24h[:24]
            ]
        }
    except Exception as e:
        logger.error(f"Forecast failed for {city_name}: {e}")
        return None