# Climbing Conditions Dashboard
*Analytics Engineering Portfolio Project*

## Goal
Build an end-to-end data pipeline that surfaces climbing conditions (temperature, wind, precipitation, air quality) for specific crags, targeting climbers as end users. Showcase a modern Analytics Engineering stack for job interviews.

## Stack
| Layer | Tool |
|-------|------|
| Ingestion | Python |
| Orchestration | Dagster (open source, with native dbt integration) |
| Storage | Snowflake (trial active ~$380 credits — BigQuery free tier as fallback) |
| Transformation | dbt (centerpiece of project) |
| IaC | Terraform |
| Visualization | Metabase or Streamlit |
| Version Control | GitHub (public, portfolio-facing) |

## Data Sources
- **Open-Meteo** — free, no auth, historical + forecast weather by lat/long
- **Mountain Project API** — route data (grade, location, type, popularity)
- **OpenAQ** — air quality / wildfire smoke data
- **dbt seed CSV** — hand-curated list of climbing areas with lat/long, rock type, aspect (sun/shade)

## Target Climbing Areas
- Yosemite Valley
- Buttermilks (Bishop)
- Tuolumne Meadows
- Lake Tahoe area

## dbt Model Structure
```
staging/
  stg_weather.sql          -- Open-Meteo source
  stg_routes.sql           -- Mountain Project source
  stg_air_quality.sql      -- OpenAQ source

intermediate/
  int_routes_enriched.sql  -- Routes joined to nearest weather station + air quality

marts/
  fct_conditions.sql       -- Daily climbability score per area (weighted formula)
  fct_historical.sql       -- Best months per crag historically
  dim_areas.sql            -- Climbing area dimension from seed data
```

## Key Design Decisions (to be made during build)
- Climbability score formula — weighted factors: temperature range, wind speed threshold, precipitation, AQI
- Granularity — daily or hourly
- How to match Mountain Project routes to Open-Meteo lat/long coordinates

## Interview Narrative
> "I climb V8-V9 and built a real-time conditions tool for climbers using dbt, Snowflake, Dagster, and Open-Meteo. The core of the project is a dbt mart model that calculates a daily climbability score per climbing area based on weighted weather and air quality factors."

## Current Status
- Snowflake trial active
- dbt Fundamentals certification complete
- Dagster selected for orchestration (native dbt integration)
- Project not yet started — architecture phase

## Constraints
- 3-4 hours available on non-climbing weekends
- Target completion: 6-8 weeks
- Must be public on GitHub as a portfolio piece
