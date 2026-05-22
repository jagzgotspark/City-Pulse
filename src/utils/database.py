import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")
# Railway uses postgresql:// but SQLAlchemy needs postgresql+psycopg2://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
engine = create_engine(DATABASE_URL)


def init_db():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS cities (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                lat FLOAT NOT NULL,
                lon FLOAT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS weather_snapshots (
                id SERIAL PRIMARY KEY,
                city_id INTEGER REFERENCES cities(id),
                timestamp TIMESTAMPTZ NOT NULL,
                temperature FLOAT,
                feels_like FLOAT,
                humidity INTEGER,
                condition VARCHAR(50),
                wind_speed FLOAT,
                visibility INTEGER,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS air_quality_snapshots (
                id SERIAL PRIMARY KEY,
                city_id INTEGER REFERENCES cities(id),
                timestamp TIMESTAMPTZ NOT NULL,
                aqi INTEGER,
                pm2_5 FLOAT,
                pm10 FLOAT,
                co FLOAT,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS pulse_scores (
                id SERIAL PRIMARY KEY,
                city_id INTEGER REFERENCES cities(id),
                timestamp TIMESTAMPTZ NOT NULL,
                score FLOAT NOT NULL,
                weather_score FLOAT,
                air_score FLOAT,
                summary TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS events_snapshots (
                id SERIAL PRIMARY KEY,
                city_id INTEGER REFERENCES cities(id),
                timestamp TIMESTAMPTZ NOT NULL,
                event_count INTEGER,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """))
        conn.commit()
        print("Database initialised with new schema")

def get_or_create_city(name: str, lat: float, lon: float) -> int:
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id FROM cities WHERE name = :name
        """), {"name": name})
        row = result.fetchone()

        if row:
            return row[0]

        result = conn.execute(text("""
            INSERT INTO cities (name, lat, lon)
            VALUES (:name, :lat, :lon)
            RETURNING id
        """), {"name": name, "lat": lat, "lon": lon})
        conn.commit()
        return result.fetchone()[0]

def save_weather_snapshot(city_id: int, data: dict):
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO weather_snapshots
                (city_id, timestamp, temperature, feels_like,
                 humidity, condition, wind_speed, visibility)
            VALUES
                (:city_id, :timestamp, :temperature, :feels_like,
                 :humidity, :condition, :wind_speed, :visibility)
        """), {**data, "city_id": city_id})
        conn.commit()

def save_air_snapshot(city_id: int, data: dict):
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO air_quality_snapshots
                (city_id, timestamp, aqi, pm2_5, pm10, co)
            VALUES
                (:city_id, :timestamp, :aqi, :pm2_5, :pm10, :co)
        """), {**data, "city_id": city_id})
        conn.commit()

def save_events_snapshot(city_id: int, data: dict):
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO events_snapshots
                (city_id, timestamp, event_count)
            VALUES
                (:city_id, :timestamp, :event_count)
        """), {**data, "city_id": city_id})
        conn.commit()

def get_latest_snapshot(city_name: str) -> dict | None:
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT
                c.name,
                w.temperature,
                w.feels_like,
                w.humidity,
                w.condition,
                w.wind_speed,
                w.visibility,
                a.aqi,
                a.pm2_5,
                w.timestamp
            FROM weather_snapshots w
            JOIN cities c ON w.city_id = c.id
            LEFT JOIN air_quality_snapshots a ON a.city_id = c.id
            WHERE c.name = :city_name
            ORDER BY w.timestamp DESC
            LIMIT 1
        """), {"city_name": city_name})
        row = result.fetchone()
        return dict(row._mapping) if row else None

def get_history(city_name: str, hours: int = 24) -> list:
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT
                w.timestamp,
                w.temperature,
                w.humidity,
                w.condition,
                a.aqi
            FROM weather_snapshots w
            JOIN cities c ON w.city_id = c.id
            LEFT JOIN air_quality_snapshots a ON a.city_id = c.id
            WHERE c.name = :city_name
            AND w.timestamp > NOW() - INTERVAL ':hours hours'
            ORDER BY w.timestamp ASC
        """), {"city_name": city_name, "hours": hours})
        return [dict(row._mapping) for row in result]


def get_all_cities() -> list:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT name, lat, lon FROM cities"))
        return [dict(row._mapping) for row in result]

def get_or_create_city(name: str, lat: float, lon: float) -> int:
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id FROM cities WHERE name = :name
        """), {"name": name})
        row = result.fetchone()

        if row:
            return row[0]

        result = conn.execute(text("""
            INSERT INTO cities (name, lat, lon)
            VALUES (:name, :lat, :lon)
            RETURNING id
        """), {"name": name, "lat": lat, "lon": lon})
        conn.commit()
        return result.fetchone()[0]

def save_weather_snapshot(city_id: int, data: dict):
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO weather_snapshots
                (city_id, timestamp, temperature, feels_like,
                 humidity, condition, wind_speed, visibility)
            VALUES
                (:city_id, :timestamp, :temperature, :feels_like,
                 :humidity, :condition, :wind_speed, :visibility)
        """), {**data, "city_id": city_id})
        conn.commit()

def save_air_snapshot(city_id: int, data: dict):
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO air_quality_snapshots
                (city_id, timestamp, aqi, pm2_5, pm10, co)
            VALUES
                (:city_id, :timestamp, :aqi, :pm2_5, :pm10, :co)
        """), {**data, "city_id": city_id})
        conn.commit()
       
def save_pulse_score(city_id: int, data: dict):
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO pulse_scores
                (city_id, timestamp, score, weather_score, air_score, summary)
            VALUES
                (:city_id, :timestamp, :score, :weather_score, :air_score, :summary)
        """), {**data, "city_id": city_id})
        conn.commit()  

def get_latest_pulse(city_name: str) -> dict | None:
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT p.score, p.weather_score, p.air_score, p.timestamp
            FROM pulse_scores p
            JOIN cities c ON p.city_id = c.id
            WHERE c.name = :city_name
            ORDER BY p.timestamp DESC
            LIMIT 1
        """), {"city_name": city_name})
        row = result.fetchone()
        return dict(row._mapping) if row else None   

def get_pulse_trend(city_name: str, days: int = 7) -> list:
    with engine.connect() as conn:
        result = conn.execute(text(f"""
            SELECT
                DATE_TRUNC('hour', p.timestamp) as hour,
                AVG(p.score) as avg_score,
                AVG(p.weather_score) as avg_weather,
                AVG(p.air_score) as avg_air
            FROM pulse_scores p
            JOIN cities c ON p.city_id = c.id
            WHERE c.name = :city_name
            AND p.timestamp > NOW() - INTERVAL '{days} days'
            GROUP BY hour
            ORDER BY hour ASC
        """), {"city_name": city_name})
        return [dict(row._mapping) for row in result]

def get_daily_summary(city_name: str, days: int = 30) -> list:
    with engine.connect() as conn:
        result = conn.execute(text(f"""
            SELECT
                DATE_TRUNC('day', p.timestamp) as day,
                AVG(p.score) as avg_score,
                MAX(p.score) as max_score,
                MIN(p.score) as min_score
            FROM pulse_scores p
            JOIN cities c ON p.city_id = c.id
            WHERE c.name = :city_name
            AND p.timestamp > NOW() - INTERVAL '{days} days'
            GROUP BY day
            ORDER BY day ASC
        """), {"city_name": city_name})
        return [dict(row._mapping) for row in result]

def get_city_comparison(days: int = 7) -> list:
    with engine.connect() as conn:
        result = conn.execute(text(f"""
            SELECT
                c.name,
                AVG(p.score) as avg_score,
                MAX(p.score) as best_score,
                MIN(p.score) as worst_score,
                COUNT(p.id) as data_points
            FROM pulse_scores p
            JOIN cities c ON p.city_id = c.id
            WHERE p.timestamp > NOW() - INTERVAL '{days} days'
            GROUP BY c.name
            ORDER BY avg_score DESC
        """))
        return [dict(row._mapping) for row in result]   