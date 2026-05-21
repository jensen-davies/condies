# Snowflake → BigQuery Migration

## 1. GCP Setup
- [x] Create a GCP project
- [x] Enable the BigQuery API
- [x] Create a service account and download the JSON key
- [x] Create datasets: `raw`, `staging`, `intermediate`, `marts`

## 2. Dependencies
Swap packages in `requirements.txt`:
- [x] Remove `snowflake-connector-python`, add `google-cloud-bigquery`
- [x] Remove `dbt-snowflake`, add `dbt-bigquery`
- [ ] Remove `dagster-snowflake`, add `dagster-gcp`

## 3. dbt Profile
- [x] Rewrite the `condies` profile in `~/.dbt/profiles.yml` with BigQuery connection (project ID, dataset, service account key path)

## 4. SQL Rewrites

### stg_weather.sql *(medium)*
- [x] Replace `LATERAL FLATTEN` + Snowflake JSON extraction syntax (`raw_json:hourly.temp[f.index]::float`) with BigQuery `UNNEST()` + `JSON_EXTRACT_SCALAR`

### int_weather_daily.sql *(low)*
- [x] No changes needed — pure standard SQL

### int_weather_windows.sql *(low)*
- [x] Replace `hour()` with `extract(hour from ...)`

### fct_conditions.sql *(low)*
- [x] No changes needed — pure standard SQL

## 5. Ingestion
- [x] In `dagster_condies/assets/weather_ingest.py`, swap the Snowflake write operation for a BigQuery client write

## 6. Dagster Resources
- [x] No Snowflake resource was wired into definitions.py — nothing to change

## 7. Streamlit
- [x] In `streamlit_app/data.py`, swap the Snowflake connector query for a BigQuery client query

## 8. Validation
- [x] Run `dbt debug` to confirm BigQuery connection
- [x] Run `dbt run` and verify all models build clean
- [ ] Run `dbt test` and verify all tests pass
- [ ] Confirm Streamlit app loads data correctly
