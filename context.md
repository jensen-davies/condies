# Condies — Session Log
*Append-only. Never edit past entries. One entry per working session.*

---

## 2026-04-19
**Status:** Project initialized — architecture phase complete.

**What happened:**
- Reviewed project spec (`condies_project.md`)
- Wrote `claude.md` with full development rules: dbt conventions, Snowflake setup, Dagster SDA pattern, Git workflow, folder structure, setup sequence

**Decisions made:**
- Dagster Software-Defined Assets API (not Jobs/Ops)
- Snowflake DB structure: `CONDIES_DB` → `RAW`, `STAGING`, `INTERMEDIATE`, `MARTS`
- Open-Meteo first (no auth), Terraform last
- X-SMALL warehouse with 1-min auto-suspend to protect trial credits

**Current state:**
- No GitHub repo
- No code written
- No Dagster, Terraform, or Metabase installed
- Snowflake trial active, ~20 days remaining

**Next session:**
1. Create GitHub repo (public)
2. Create Snowflake DB, schemas, warehouse
3. Configure `~/.dbt/profiles.yml`
4. Run `dbt debug` to confirm connection
