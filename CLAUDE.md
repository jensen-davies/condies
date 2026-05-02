# Condies — Climbing Conditions Dashboard
*Analytics Engineering Portfolio Project*

## Project Purpose
Build an end-to-end data pipeline that surfaces climbing conditions (temperature, wind, precipitation, air quality) for specific crags. The primary goal is developing **employable Data Engineering and Analytics Engineering skills** — every technical decision should be understandable and defensible in a professional interview.

## Stack
| Layer | Tool | Status |
|-------|------|--------|
| Ingestion | Python scripts | Working (Open-Meteo) |
| Orchestration | Dagster (OSS) | Not installed |
| Storage | Snowflake | Trial active |
| Transformation | dbt Core | Staging + intermediate + marts built |
| IaC | Terraform | Not started |
| Visualization | Metabase or Streamlit | TBD |
| Version Control | GitHub (public) | Repo: `condies` |

## CLAUDE.md Update Rules

This file is **not a running log** — it is a stable reference document. Edit it sparingly.

- Only update when a project milestone is reached or a major design decision is made
- Do **not** add implementation details, step-by-step notes, or anything that belongs in `context.md`
- **Always suggest the change and get confirmation before editing** — never edit this file unilaterally

---

## Session Log Rules (`context.md`)

`context.md` is the source of truth for where the project is at. Follow these rules exactly:

**At the start of every session:**
- Read `context.md` fully before writing or running anything
- Use the "Current state" and "Remaining steps" fields from the last entry to orient yourself — do not rely on memory or assumptions

**Log after each confirmed step — not at end of session:**
- Append a new entry to `context.md` as soon as the user confirms a step is complete
- Do not batch multiple steps into one entry — one step = one entry
- This prevents context loss if the terminal crashes or the session ends unexpectedly
- "Current state" must be a complete snapshot — someone reading only that entry should know exactly where things stand
- Use today's actual date (`YYYY-MM-DD`)

**Format for each entry:**
```
## YYYY-MM-DD — <short step name>
**Completed:** one-line description of what was just done

**Decisions made:**
- decision — reason (omit section if none)

**Current state:**
- complete snapshot of what exists and what doesn't

**Remaining steps:**
1. numbered list of what still needs to happen
```

**What counts as a step worth logging:**
- Any command confirmed run successfully
- Any file created or code written
- Any architectural decision made
- Any blocker hit

**What does NOT go in context.md:**
- Exploratory conversation with no concrete output
- Questions and answers that didn't change anything

---

## Development Rules

### Learning-First Rule
**This project exists to teach.** When writing any non-trivial code or making any architectural decision:
- Explain the *why* behind it, not just the *what*
- Name the concept being used (e.g. "this is a slowly changing dimension", "this is an idempotent pipeline")
- If there's a tradeoff (cost vs. freshness, simplicity vs. flexibility), spell it out explicitly
- The user should be able to re-explain any part of this codebase in a job interview

### dbt Rules
- **Model naming is strict**: prefix `stg_` for staging, `int_` for intermediate, `fct_` for fact tables, `dim_` for dimensions
- Every model must have a corresponding entry in `schema.yml` with a description
- Every primary key column must have `unique` and `not_null` tests — no exceptions
- `sources.yml` must define all raw source tables before they are referenced in staging models
- Use `{{ ref() }}` for model-to-model references and `{{ source() }}` for raw tables — never hardcode schema names
- Keep staging models 1:1 with source tables (rename/recast only, no joins)
- Joins and business logic belong in intermediate or mart models, not staging
- The climbability score formula in `fct_conditions.sql` must have an inline comment explaining each weighted factor
- The climbability score is a **first-pass model** — it scores on temperature, dew point, wind bonus, and precipitation only. Future iterations should incorporate rock type and aspect, which affect how a crag responds to temperature and humidity (e.g. north-facing granite stays wet longer after rain than south-facing sandstone)

### Snowflake Rules
- **Warehouse**: use `COMPUTE_WH` (X-SMALL) for all development — auto-suspend set to 1 minute to conserve trial credits
- **Database structure**: `CONDIES_DB` → schemas: `RAW`, `STAGING`, `INTERMEDIATE`, `MARTS`
- Never query the `RAW` schema directly in dbt models — always go through a staging model
- Profile credentials go in `~/.dbt/profiles.yml`, never in the repo
- Add `snowflake_warehouse: COMPUTE_WH` to every dbt model config that runs expensive joins — prevents accidental large warehouse usage

### Dagster Rules
- Use the **Software-Defined Assets** (SDA) API — not the older Jobs/Ops API. SDAs are the modern Dagster paradigm and what interviewers expect to hear about.
- Each data source (Open-Meteo, Mountain Project, OpenAQ) gets its own asset
- Use **daily partitions** — the pipeline should be able to backfill any date range independently
- The dbt project integrates via `dagster-dbt` — use `DbtCliResource` and `@dbt_assets`, not subprocess calls
- Asset metadata (row counts, last updated) should be attached via `MaterializeResult` so the Dagster UI shows meaningful output

### Python / Ingestion Rules
- Ingestion scripts are dumb extractors only — no transformation logic
- Write raw API responses to Snowflake `RAW` schema as-is (use `snowflake-connector-python` or `snowflake-sqlalchemy`)
- Every API call must handle rate limits with exponential backoff
- API keys go in environment variables, never hardcoded

### Git / GitHub Rules
- Repo must be **public** — it's a portfolio piece
- Branch from `main`, PR back to `main`, squash merge
- Commit messages: imperative present tense (`add stg_weather model`, not `added stg_weather model`)
- `.gitignore` must exclude: `.env` files, `target/`, `dbt_packages/`, `logs/`

### File / Folder Structure
```
condies/
├── .github/
│   └── workflows/          # CI (dbt compile check at minimum)
├── dagster_condies/
│   ├── assets/             # one file per data source + dbt assets
│   ├── resources/          # Snowflake connection, dbt resource
│   └── definitions.py      # Dagster Definitions object
├── dbt_condies/
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   └── marts/
│   ├── seeds/              # climbing areas CSV (lat/long, rock type, aspect)
│   ├── tests/              # custom singular tests
│   └── dbt_project.yml
├── ingestion/              # raw Python extraction scripts
├── terraform/              # Snowflake IaC (add last)
├── .env.example            # template with required env var names, no values
└── claude.md
```

## Setup Sequence (do in order)
1. Create GitHub repo, clone locally
2. Set up Snowflake: create `CONDIES_DB`, schemas, `COMPUTE_WH` with 1-min auto-suspend
3. Configure `~/.dbt/profiles.yml` for Snowflake connection
4. `dbt init dbt_condies` — confirm connection with `dbt debug`
5. `pip install dagster dagster-dbt dagster-snowflake` — confirm with `dagster dev`
6. Build ingestion script for Open-Meteo first (no auth required — easiest win)
7. Build `stg_weather.sql` — first dbt model
8. Wire up Dagster asset for weather ingestion → dbt run
9. Add remaining sources incrementally

## Interview Talking Points to Build Toward
- Why the dbt staging → intermediate → marts layer separation exists
- What Software-Defined Assets are and why they replaced the Jobs/Ops model in Dagster
- How Snowflake virtual warehouses and credit consumption work
- What idempotency means in a data pipeline and how partitioning achieves it
- How the climbability score formula was designed (domain knowledge + weighted factors)
- Why this is a star schema and what that means for query performance

## Constraints
- 3-4 hours available on non-climbing weekends
- Snowflake trial: ~20 days remaining — prioritize the dbt ↔ Snowflake connection first
- Target completion: 6-8 weeks
- Terraform is last — get the rest of the stack working first

## Roadmap

### V2 — Route-Level Scoring
- Add `boulder_routes` dbt seed (CSV) with: rock type, aspect, overhang angle, drainage/seepage/shade ratings
- Join route metadata to `fct_conditions` to adjust scores per problem, not just per crag
- Sandstone wet sensitivity, granite drying speed, aspect-driven sun exposure are the first modifiers worth adding

### V2 — Multi-Dimensional Score Output
- Replace single `climbability_score` with weighted sub-scores: friction, dryness, comfort, wind, sun exposure
- Overall score = weighted rollup; sub-scores exposed for transparency
- Requires route metadata (aspect, rock type) and additional weather variables (solar radiation, relative humidity)

### V3+ — Historical Validation & Feedback
- Store forecast snapshots + actual observations to backtest scoring accuracy
- Community session feedback ("greasy", "prime", "still wet") as tuning signal
- ML only after deterministic heuristics are validated against real data
