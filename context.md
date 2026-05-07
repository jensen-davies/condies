# Condies — Session Log
*Append-only. Never edit past entries. One entry per completed step.*

---

## 2026-04-19 — Project architecture defined
**Completed:** Reviewed project spec and wrote `CLAUDE.md` with full development rules.

**Decisions made:**
- Dagster Software-Defined Assets API (not Jobs/Ops)
- Snowflake DB structure: `CONDIES_DB` → `RAW`, `STAGING`, `INTERMEDIATE`, `MARTS`
- Open-Meteo first (no auth), Terraform last
- X-SMALL warehouse with 1-min auto-suspend to protect trial credits

**Current state:**
- `CLAUDE.md` exists with full dev rules
- No GitHub repo, no code, no tools installed
- Snowflake trial active

**Remaining steps:**
1. Create GitHub repo (public)
2. Create Snowflake DB, schemas, warehouse
3. Add Python to PATH, install dbt-snowflake
4. Configure `~/.dbt/profiles.yml` and run `dbt debug`

---

## 2026-04-19 — GitHub repo created
**Completed:** Created public GitHub repo `condies`.

**Current state:**
- GitHub repo `condies` exists (public)
- Snowflake not yet set up
- No tools installed

**Remaining steps:**
1. Create Snowflake DB, schemas, warehouse
2. Add Python to PATH, install dbt-snowflake
3. Configure `~/.dbt/profiles.yml` and run `dbt debug`

---

## 2026-04-19 — Snowflake infrastructure created
**Completed:** Created `COMPUTE_WH`, `CONDIES_DB`, and all 4 schemas via Snowflake SQL Worksheet.

**Decisions made:**
- `COMPUTE_WH`: X-SMALL, auto-suspend 60s, auto-resume true, initially suspended

**Current state:**
- GitHub repo `condies` exists (public)
- Snowflake: `CONDIES_DB` with schemas `RAW`, `STAGING`, `INTERMEDIATE`, `MARTS` and `COMPUTE_WH` all created
- Python 3.9 at `/Users/jensen/Library/Python/3.9/bin` — NOT yet on PATH
- `dbt-snowflake` NOT installed
- `~/.dbt/profiles.yml` NOT configured

**Remaining steps:**
1. Install dbt-snowflake: `pip3 install dbt-snowflake`
2. Configure `~/.dbt/profiles.yml`
3. `dbt init dbt_condies` and run `dbt debug`

---

## 2026-04-19 — Python PATH fixed
**Completed:** Added `/Users/jensen/Library/Python/3.9/bin` to PATH in `~/.zshrc`.

**Current state:**
- GitHub repo `condies` exists (public)
- Snowflake: `CONDIES_DB` with all 4 schemas and `COMPUTE_WH` created
- Python 3.9 on PATH
- `dbt-snowflake` NOT installed
- `~/.dbt/profiles.yml` NOT configured

**Remaining steps:**
1. Install dbt-snowflake: `pip3 install dbt-snowflake`
2. Configure `~/.dbt/profiles.yml`
3. `dbt init dbt_condies` and run `dbt debug`

---

## 2026-04-19 — dbt-snowflake installed in Python 3.12 venv
**Completed:** Created `.venv` with Python 3.12, installed dbt-snowflake, resolved PATH cache issue with `hash -r`. dbt --version confirms up-to-date versions.

**Decisions made:**
- Python 3.12 chosen (newest version dbt supports) over reusing system Python 3.9
- venv at `.venv/` (already in .gitignore)
- Must run `source .venv/bin/activate` at the start of each session

**Current state:**
- GitHub repo `condies` exists (public)
- Snowflake: `CONDIES_DB` with all 4 schemas and `COMPUTE_WH` created
- `.venv` (Python 3.12) activated with dbt-snowflake installed and up to date
- `~/.dbt/profiles.yml` NOT configured
- dbt project NOT initialized

**Remaining steps:**
1. Configure `~/.dbt/profiles.yml` with Snowflake credentials
2. `dbt init dbt_condies`
3. Run `dbt debug` to confirm connection

---

## 2026-04-19 — dbt connected to Snowflake, dbt debug passed
**Completed:** Configured `~/.dbt/profiles.yml`, ran `dbt init dbt_condies`, fixed profile name mismatch (`dbt_condies` → `condies` in `dbt_project.yml`). All checks passed.

**Decisions made:**
- Profile named `condies` in `~/.dbt/profiles.yml` (not `dbt_condies` — dbt init appended a duplicate which was deleted)
- `dbt_project.yml` updated to reference `profile: 'condies'`

**Current state:**
- GitHub repo `condies` exists (public)
- Snowflake: `CONDIES_DB` with all 4 schemas and `COMPUTE_WH` created
- `.venv` (Python 3.12) with dbt-snowflake installed — activate with `source .venv/bin/activate`
- `~/.dbt/profiles.yml` configured, `dbt debug` passing
- `dbt_condies/` project initialized with boilerplate example models (not yet cleaned up)

**Remaining steps:**
1. Delete boilerplate (`dbt_condies/models/example/`)
2. Set up `dbt_project.yml` model schema configs (staging → STAGING, intermediate → INTERMEDIATE, marts → MARTS)
3. Create `sources.yml` and first staging model `stg_weather.sql`

---

## 2026-04-22 — dbt project configured, boilerplate removed
**Completed:** Deleted example models, updated `dbt_project.yml` model schema configs, created `generate_schema_name` macro for clean schema routing.

**Decisions made:**
- staging/intermediate → `view`, marts → `table` (views are cheap pass-throughs; tables serve BI tools)
- `generate_schema_name` macro overrides dbt default to prevent `STAGING_STAGING`-style names

**Current state:**
- GitHub repo `condies` exists (public)
- Snowflake: `CONDIES_DB` with all 4 schemas and `COMPUTE_WH` created
- `.venv` (Python 3.12) with dbt-snowflake — activate with `source .venv/bin/activate`
- `~/.dbt/profiles.yml` configured, `dbt debug` passing
- `dbt_condies/` project clean: schema routing configured, no boilerplate
- No models written yet

**Remaining steps:**
1. Build Open-Meteo ingestion script (writes raw JSON to Snowflake RAW schema)
2. Create `sources.yml` defining the raw weather table
3. Write first staging model `stg_weather.sql`

---

## 2026-04-22 — Open-Meteo ingestion script working, 3 rows in Snowflake
**Completed:** Wrote `ingestion/open_meteo.py`, ran it, verified 3 rows in `CONDIES_DB.RAW.OPEN_METEO_WEATHER`.

**Decisions made:**
- Raw layer is append-only — each run inserts new rows, staging handles deduplication by FETCH_DATE
- Storing full API response as VARIANT — staging models unpack specific fields
- Crags: Camp 4 (37.74172, -119.60354), Buttermilks (37.32817, -118.57477), Castle Rock SP (37.22954, -122.09658)

**Current state:**
- GitHub repo `condies` exists (public)
- Snowflake: `CONDIES_DB.RAW.OPEN_METEO_WEATHER` has live data (3 crags)
- `.venv` (Python 3.12) with dbt-snowflake — activate with `source .venv/bin/activate`
- `~/.dbt/profiles.yml` configured, `dbt debug` passing
- `dbt_condies/` project configured, no models written yet

**Remaining steps:**
1. Create `dbt_condies/models/staging/sources.yml` defining the raw weather table
2. Write `dbt_condies/models/staging/stg_weather.sql`
3. Run `dbt run` and verify staging model builds in Snowflake

---

## 2026-04-22 — stg_weather built successfully in Snowflake
**Completed:** Created `sources.yml`, wrote `stg_weather.sql` using LATERAL FLATTEN to unpack hourly JSON arrays. `dbt run` passed cleanly.

**Decisions made:**
- Staging model flattens hourly JSON arrays into one row per crag per hour (72 rows per source row)
- LATERAL FLATTEN on `hourly.time` array; `f.index` used to pull matching values from parallel arrays

**Current state:**
- `CONDIES_DB.STAGING.STG_WEATHER` view exists and is populated
- Warning about unused config paths for `intermediate` and `marts` — expected, folders exist but no models yet
- No `schema.yml` for `stg_weather` yet (descriptions + tests)

**Remaining steps:**
1. Write `schema.yml` for `stg_weather` (descriptions + not_null tests)
2. Run `dbt test` to verify
3. Plan intermediate model (`int_weather_daily.sql` or similar)

---

## 2026-04-24 — stg_weather schema.yml complete, all 4 tests passing
**Completed:** Wrote `schema.yml` for `stg_weather` with column descriptions, `not_null` tests on `crag_name`, `fetch_date`, `hour_at`, and a `dbt_utils.unique_combination_of_columns` test on `crag_name + hour_at + fetch_date`. All 4 tests pass.

**Decisions made:**
- Installed `dbt-labs/dbt_utils` via `packages.yml` for composite key testing
- Composite key chosen over surrogate key — keeps staging model simple

**Current state:**
- `CONDIES_DB.STAGING.STG_WEATHER` view exists, populated, fully tested
- `dbt test` passing 4/4
- No intermediate or mart models yet

**Remaining steps:**
1. Write `int_weather_daily.sql` — aggregate hourly rows to daily summaries per crag
2. Write `schema.yml` entry for the intermediate model
3. Plan `fct_conditions.sql` mart with climbability score

---

## 2026-04-28 — int_weather_daily built and verified
**Completed:** Wrote `int_weather_daily.sql`, aggregating hourly rows to one row per crag per day. Verified view in Snowflake.

**Decisions made:**
- All units converted to imperial: °F, inches, mph
- All numeric values rounded to 2 decimal places
- Columns: `crag_name`, `fetch_date`, `day`, `temp_min_f`, `temp_max_f`, `precip_total_in`, `windspeed_avg_mph`, `windspeed_max_mph`

**Current state:**
- `CONDIES_DB.STAGING.STG_WEATHER` view — tested, passing
- `CONDIES_DB.INTERMEDIATE.INT_WEATHER_DAILY` view — built, verified
- No `schema.yml` for intermediate model yet
- No mart models yet

**Remaining steps:**
1. Write `schema.yml` for `int_weather_daily`
2. Write `fct_conditions.sql` with climbability score formula
3. Write `schema.yml` for `fct_conditions`

---

## 2026-04-28 — int_weather_daily schema.yml complete, all tests passing
**Completed:** Wrote `schema.yml` for `int_weather_daily` with column descriptions, not_null tests on key columns, composite unique test. All tests pass.

**Current state:**
- `CONDIES_DB.STAGING.STG_WEATHER` — tested, passing
- `CONDIES_DB.INTERMEDIATE.INT_WEATHER_DAILY` — tested, passing
- No mart models yet

**Remaining steps:**
1. Design and write `fct_conditions.sql` with climbability score formula
2. Write `schema.yml` for `fct_conditions`
3. Commit everything to GitHub

---

## 2026-04-28 — dewpoint_2m added across all layers
**Completed:** Added `dewpoint_2m` to ingestion script, `dewpoint_c` to `stg_weather`, `dewpoint_avg_f`/`dewpoint_max_f` to `int_weather_daily`. Re-ran ingestion, all tests passing, dew point values confirmed present.

**Current state:**
- `CONDIES_DB.STAGING.STG_WEATHER` — includes `dewpoint_c`, tested, passing
- `CONDIES_DB.INTERMEDIATE.INT_WEATHER_DAILY` — includes `dewpoint_avg_f`, `dewpoint_max_f`, tested, passing
- No mart models yet

**Remaining steps:**
1. Design and write `fct_conditions.sql` with climbability score formula
2. Write `schema.yml` for `fct_conditions`
3. Commit everything to GitHub

---

## 2026-04-29 — fct_conditions.sql written with climbability score
**Completed:** Wrote `fct_conditions.sql` and `marts/schema.yml`. Climbability score formula agreed and implemented.

**Decisions made:**
- Score is 100 pts base (temp 60 + dewpoint 40) + wind bonus up to +3 = max 103
- Temperature scored on `temp_max_f` (conservative day-level estimate)
- Dew point scored on `dewpoint_max_f` (worst-case humidity of the day)
- Precipitation acts as a multiplier (0 or 1) — any rain zeros the entire score
- Wind (5–15 mph avg) gives +3 bonus; no penalty for high wind in v1
- This is a **first-pass scoring model** — future iterations will add rock type and aspect, which affect how a crag responds to temperature and humidity
- Component scores (`temp_score`, `dewpoint_score`, `wind_bonus`, `precip_multiplier`) are exposed as columns for transparency and future debugging

**Current state:**
- `CONDIES_DB.STAGING.STG_WEATHER` — tested, passing
- `CONDIES_DB.INTERMEDIATE.INT_WEATHER_DAILY` — tested, passing
- `dbt_condies/models/marts/fct_conditions.sql` — written, not yet run
- `dbt_condies/models/marts/schema.yml` — written
- `dbt run` and `dbt test` not yet run for the mart layer

**Remaining steps:**
1. Run `dbt run` and verify `CONDIES_DB.MARTS.FCT_CONDITIONS` table builds in Snowflake
2. Run `dbt test` to confirm all mart tests pass
3. Commit everything to GitHub

---

## 2026-05-01 — Full dbt pipeline passing, all 12 tests green
**Completed:** `dbt run && dbt test` passed cleanly across all three layers. `CONDIES_DB.MARTS.FCT_CONDITIONS` table built and tested. Also added `temp_avg_f` and `hours_in_prime_temp` to `int_weather_daily`; updated temperature scoring in `fct_conditions` to use hours in the 44–63°F window instead of daily max.

**Decisions made:**
- Temperature scored on `hours_in_prime_temp` (count of hours between 44–63°F) — captures duration of climbable window, not just peak or average
- `temp_avg_f` added as an informational column (not used for scoring)
- Scoring thresholds: ≥6 hrs = 60 pts, ≥4 = 44, ≥2 = 30, ≥1 = 14, 0 = 0

**Current state:**
- `CONDIES_DB.STAGING.STG_WEATHER` — tested, passing
- `CONDIES_DB.INTERMEDIATE.INT_WEATHER_DAILY` — includes `temp_avg_f`, `hours_in_prime_temp`, tested, passing
- `CONDIES_DB.MARTS.FCT_CONDITIONS` — built as table, all tests passing
- Nothing committed to GitHub yet

**Remaining steps:**
1. ~~Commit everything to GitHub~~ Done

---

## 2026-05-01 — Window-based scoring implemented, all tests passing
**Completed:** Replaced `hours_in_prime_temp` approach with three time windows. Added `int_weather_windows.sql`, rewrote `fct_conditions.sql` to score morning/afternoon/evening independently. `dbt run && dbt test` passed.

**Decisions made:**
- Windows: morning 7–11am, afternoon 12–5pm, evening 6–11pm
- Each window scored independently: temp (60) + dewpoint (40) + wind bonus (3), zeroed by precip
- `climbability_score` = average of the three window scores (max 103)
- Removed `hours_in_prime_temp` from `int_weather_daily` — replaced by window-level scoring

**Current state:**
- `CONDIES_DB.STAGING.STG_WEATHER` — tested, passing
- `CONDIES_DB.INTERMEDIATE.INT_WEATHER_DAILY` — tested, passing
- `CONDIES_DB.INTERMEDIATE.INT_WEATHER_WINDOWS` — new, tested, passing
- `CONDIES_DB.MARTS.FCT_CONDITIONS` — rebuilt with window scores, all tests passing
- Nothing committed to GitHub yet

**Remaining steps:**
1. Install Dagster and wire up orchestration

---

## 2026-05-01 — Dagster installed, raw_weather asset materializing
**Completed:** Installed dagster, dagster-dbt, dagster-snowflake. Created `dagster_condies/` package with `raw_weather` SDA wrapping the Open-Meteo ingestion script. Asset materializes successfully in the UI.

**Decisions made:**
- `open_meteo.py` kept as standalone module — `weather_ingest.py` imports from it (framework separation)
- Run with `dg dev -f dagster_condies/definitions.py` from project root
- `MaterializeResult` returns `rows_inserted` and `crags` metadata

**Current state:**
- Full dbt pipeline built and tested in Snowflake
- `dagster_condies/assets/weather_ingest.py` — `raw_weather` asset working
- `dagster_condies/definitions.py` — registers `raw_weather`
- dbt assets not yet wired into Dagster

**Remaining steps:**
1. Wire dbt models into Dagster as assets using `@dbt_assets` and `DbtCliResource`
2. Fix BETWEEN scoring bug in `fct_conditions.sql`
3. Commit to GitHub

---

## 2026-05-01 — Fixed BETWEEN scoring bug in fct_conditions
**Completed:** Temperature scoring used `BETWEEN` with integer bounds, causing float temps like 57.65°F to fall in gaps and score 0. Replaced all three window scoring blocks with `>= / <` comparisons. `dbt run -s fct_conditions` confirmed fix.

**Decisions made:**
- `between 44 and 57` → `>= 44 and < 58` (and equivalent for all other bounds)
- Dewpoint scoring already used `<` — no change needed there

**Current state:**
- `CONDIES_DB.MARTS.FCT_CONDITIONS` — scoring bug fixed, rebuilt
- dbt assets not yet wired into Dagster
- Changes not yet committed to GitHub

**Remaining steps:**
1. Wire dbt models into Dagster as assets using `@dbt_assets` and `DbtCliResource`
2. Commit to GitHub

---

## 2026-05-02 — Full Dagster pipeline running end-to-end
**Completed:** Wired dbt models into Dagster via `@dbt_assets`. Full pipeline materializes in correct order: `raw_weather` → `stg_weather` → `int_weather_daily` + `int_weather_windows` → `fct_conditions`. All dbt tests passing.

**Decisions made:**
- `CondiesDbtTranslator` maps dbt source `open_meteo_weather` to `raw_weather` Dagster asset — establishes correct dependency order
- Removed `prepare_if_dev()` — manifest read from existing `target/manifest.json`; run `dbt parse` manually when models change
- Fixed `stg_weather.sql` deduplication: added `latest` CTE using `QUALIFY ROW_NUMBER()` to keep only most recent fetch per crag per date
- `profiles_dir=Path.home() / ".dbt"` added to `DbtCliResource` — profiles.yml lives outside the dbt project

**Current state:**
- Full Dagster pipeline working: `raw_weather` → dbt models, all tests passing
- `dagster_condies/assets/weather_ingest.py` — `raw_weather` SDA
- `dagster_condies/assets/dbt_assets.py` — `condies_dbt_assets` with custom translator
- `dagster_condies/definitions.py` — wires both assets + `DbtCliResource`
- `stg_weather.sql` — deduplication fixed
- Nothing committed to GitHub yet

**Remaining steps:**
1. Commit to GitHub
2. Add a daily schedule in Dagster
3. Start visualization layer (Metabase or Streamlit)

---

## 2026-05-02 — Streamlit dashboard built
**Completed:** Built `streamlit_app/` with a dark-themed forecast dashboard. Chose Streamlit over Metabase for portfolio flexibility and free local hosting.

**Decisions made:**
- Dark theme via `.streamlit/config.toml`; primary color `#2ecc71` (green)
- Single-column layout with `max-width: 860px` centered — caps on large screens, shrinks to viewport on mobile; `flex-wrap` so window cards stack on narrow screens
- Window cards colored by score tier: green ≥70, amber ≥40, red <40
- Precipitation renders 🌧 Rain inside the card; the score is already zeroed by the multiplier in dbt
- Removed map — added noise without value at this stage
- `config.py` created as single source of truth for CRAGS (lat/lon); imported by ingestion, Dagster, and Streamlit
- Kings Canyon added as fourth crag
- Run with `PYTHONPATH=. streamlit run streamlit_app/app.py`

**Current state:**
- `streamlit_app/app.py` — forecast UI with morning/afternoon/evening score cards
- `streamlit_app/data.py` — queries `fct_conditions` via Snowflake connector
- `config.py` — centralized CRAGS dict
- `.streamlit/config.toml` — dark theme config
- Nothing committed to GitHub yet

**Remaining steps:**
1. Commit to GitHub
2. Add a daily schedule in Dagster

---

## 2026-05-07 — Min/avg/max temp per window + UI polish
**Completed:** Added low/avg/high temperature to each window card. Fixed several UI details.

**Decisions made:**
- `int_weather_windows` now outputs `min_temp_f`, `avg_temp_f`, `max_temp_f` per window
- `fct_conditions` pivots and exposes all three for morning/afternoon/evening (9 new columns)
- Card displays `L 52° A 58° H 64°F` with dimmed L/A/H labels so values read first
- `/103` now styled to match the score color at 60% opacity — was too dark before
- Dew point label changed from "dew" to "dew pt"
- Day-header avg score bumped to `1rem bold` — was too small at `0.75rem`
- Scoring blurb added below the page caption explaining the formula and window times
- Window times corrected to `7am–12pm · 12pm–6pm · 6pm–12am` (hourly data means BETWEEN 7 AND 11 covers 7:00–11:59, not 7:00–11:00)
- All schema.yml descriptions updated to match

**Current state:**
- `int_weather_windows.sql` — outputs min/avg/max temp per window
- `fct_conditions.sql` — pivots and exposes all three; 9 new columns in final SELECT
- `intermediate/schema.yml` and `marts/schema.yml` — fully documented with corrected time ranges
- `streamlit_app/data.py` — queries all new columns
- `streamlit_app/app.py` — L/A/H temp display, /103 color fix, "dew pt", larger avg score, scoring blurb
- dbt run needed to materialize the new columns in Snowflake
- Nothing committed to GitHub yet

**Remaining steps:**
1. Re-materialize in Dagster (or `dbt run`) to push new columns to Snowflake
2. Commit to GitHub
3. Add a daily schedule in Dagster
