# Condies

A climbing conditions dashboard for crags. It pulls hourly weather forecasts, scores each day's climbability based on temperature, dew point, wind, and precipitation, and serves the result up in a Streamlit dashboard.

## Why

Friction is a huge component in climbing. Cold, dry air sticks to rock; while warm, humid air can feel like climbing on glass. This project takes the daily ritual of checking the forecast for ideal conditions (condies) at various crags and turns it into a single number per window of the day — letting you know, at a glance, whether tomorrow morning at the Buttermilks is going to feel like sandpaper or candle wax.

## How it works

```
Open-Meteo API  →  BigQuery (raw)  →  dbt (staging → intermediate → marts)  →  Streamlit
                          ▲
                       Dagster orchestrates
```

- **Ingestion** — A Python script fetches a 3-day hourly forecast from [Open-Meteo](https://open-meteo.com/) for each crag and writes the raw JSON to BigQuery.
- **Transformation** — dbt unpacks the JSON, aggregates it to daily and time-window summaries (morning / afternoon / evening), and computes a climbability score per window.
- **Orchestration** — Dagster wires ingestion and dbt together as Software-Defined Assets so the whole pipeline can be triggered or backfilled as a unit.
- **Visualization** — A Streamlit app reads the final mart and shows scores per crag and per time of day.

## The scoring model

Each window gets scored on:

| Component       | Max points | What it rewards                                   |
|-----------------|-----------:|---------------------------------------------------|
| Temperature     | 60         | 44–58°F is the sweet spot for friction            |
| Dew point       | 40         | Lower dew point = drier rock = better grip        |
| Wind bonus      | 3          | 5–15 mph helps the rock dry and you stay cool     |
| Precip gate     | ×          | Any rain in the window zeroes the score out       |

The daily score is the average across morning, afternoon, and evening. It's a naive first-pass heuristic — future versions will factor in rock type and aspect (north-facing granite stays wet longer than south-facing sandstone).

## Stack

- **Storage**: BigQuery
- **Transformation**: dbt Core
- **Orchestration**: Dagster (OSS)
- **Ingestion**: Python + Open-Meteo API
- **Dashboard**: Streamlit

## Crags currently tracked

Camp 4 · Buttermilks · Castle Rock SP · Kings Canyon