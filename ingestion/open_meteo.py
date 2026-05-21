import json
import os
import time
from datetime import date, datetime, timezone

import requests
from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

from config import CRAGS

BASE_URL   = "https://api.open-meteo.com/v1/forecast"
HOURLY_VARS = "temperature_2m,precipitation,windspeed_10m,wind_direction_10m,weathercode,dewpoint_2m"
DAILY_VARS  = "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max"

TABLE_ID = "{project}.raw.open_meteo_weather".format(
    project=os.environ.get("GCP_PROJECT_ID", "condies-497005")
)

SCHEMA = [
    bigquery.SchemaField("loaded_at",  "TIMESTAMP"),
    bigquery.SchemaField("fetch_date", "DATE"),
    bigquery.SchemaField("crag_name",  "STRING"),
    bigquery.SchemaField("latitude",   "FLOAT64"),
    bigquery.SchemaField("longitude",  "FLOAT64"),
    bigquery.SchemaField("raw_json",   "STRING"),
]


def get_client() -> bigquery.Client:
    return bigquery.Client.from_service_account_json(
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
    )


def ensure_table(client: bigquery.Client):
    table = bigquery.Table(TABLE_ID, schema=SCHEMA)
    client.create_table(table, exists_ok=True)


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


def insert_row(client: bigquery.Client, name: str, lat: float, lon: float, payload: dict):
    row = {
        "loaded_at":  datetime.now(timezone.utc).isoformat(),
        "fetch_date": date.today().isoformat(),
        "crag_name":  name,
        "latitude":   lat,
        "longitude":  lon,
        "raw_json":   json.dumps(payload),
    }
    errors = client.insert_rows_json(TABLE_ID, [row])
    if errors:
        raise RuntimeError(f"BigQuery insert errors for {name}: {errors}")


def main():
    client = get_client()
    ensure_table(client)

    for name, coords in CRAGS.items():
        print(f"Fetching {name}...")
        params = {
            "latitude":      coords["lat"],
            "longitude":     coords["lon"],
            "hourly":        HOURLY_VARS,
            "daily":         DAILY_VARS,
            "timezone":      "auto",
            "forecast_days": 3,
        }
        payload = fetch_with_backoff(params)
        insert_row(client, name, coords["lat"], coords["lon"], payload)
        print(f"  Inserted row for {name}")

    print("Done.")


if __name__ == "__main__":
    main()
