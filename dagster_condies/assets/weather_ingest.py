from dagster import asset, MaterializeResult, MetadataValue

from ingestion.open_meteo import (
    get_connection,
    ensure_table,
    fetch_with_backoff,
    insert_row,
    CRAGS,
    HOURLY_VARS,
    DAILY_VARS,
)


@asset
def raw_weather() -> MaterializeResult:
    conn = get_connection()
    cur = conn.cursor()
    ensure_table(cur)

    for crag in CRAGS:
        params = {
            "latitude":     crag["latitude"],
            "longitude":    crag["longitude"],
            "hourly":       HOURLY_VARS,
            "daily":        DAILY_VARS,
            "timezone":     "auto",
            "forecast_days": 3,
        }
        payload = fetch_with_backoff(params)
        insert_row(cur, crag, payload)

    conn.commit()
    cur.close()
    conn.close()

    return MaterializeResult(
        metadata={
            "rows_inserted": MetadataValue.int(len(CRAGS)),
            "crags":         MetadataValue.text(", ".join(c["name"] for c in CRAGS)),
        }
    )
