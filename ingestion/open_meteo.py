import json
import os
import time
from datetime import date

import requests
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

from config import CRAGS

BASE_URL = "https://api.open-meteo.com/v1/forecast"
HOURLY_VARS = "temperature_2m,precipitation,windspeed_10m,wind_direction_10m,weathercode,dewpoint_2m"
DAILY_VARS  = "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max"


def fetch_with_backoff(params: dict, max_retries: int = 3) -> dict:
    for attempt in range(max_retries):
        response = requests.get(BASE_URL, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        if response.status_code == 429:
            wait = 2 ** attempt
            print(f"  Rate limited — retrying in {wait}s")
            time.sleep(wait)
        else:
            response.raise_for_status()
    raise RuntimeError(f"Failed after {max_retries} retries")


def get_connection():
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        schema="RAW",
    )


def ensure_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS RAW.OPEN_METEO_WEATHER (
            LOADED_AT   TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            FETCH_DATE  DATE,
            CRAG_NAME   VARCHAR,
            LATITUDE    FLOAT,
            LONGITUDE   FLOAT,
            RAW_JSON    VARIANT
        )
    """)


def insert_row(cursor, name: str, lat: float, lon: float, payload: dict):
    cursor.execute(
        """
        INSERT INTO RAW.OPEN_METEO_WEATHER (FETCH_DATE, CRAG_NAME, LATITUDE, LONGITUDE, RAW_JSON)
        SELECT %s, %s, %s, %s, PARSE_JSON(%s)
        """,
        (
            date.today().isoformat(),
            name,
            lat,
            lon,
            json.dumps(payload),
        ),
    )


def main():
    conn = get_connection()
    cur = conn.cursor()
    ensure_table(cur)

    for name, coords in CRAGS.items():
        print(f"Fetching {name}...")
        params = {
            "latitude":  coords["lat"],
            "longitude": coords["lon"],
            "hourly":    HOURLY_VARS,
            "daily":     DAILY_VARS,
            "timezone":  "auto",
            "forecast_days": 3,
        }
        payload = fetch_with_backoff(params)
        insert_row(cur, name, coords["lat"], coords["lon"], payload)
        print(f"  Inserted row for {name}")

    conn.commit()
    cur.close()
    conn.close()
    print("Done.")


if __name__ == "__main__":
    main()
