from pathlib import Path

from dagster import Definitions
from dagster_dbt import DbtCliResource

from dagster_condies.assets.weather_ingest import raw_weather
from dagster_condies.assets.dbt_assets import condies_dbt_assets, dbt_project

defs = Definitions(
    assets=[raw_weather, condies_dbt_assets],
    resources={
        "dbt": DbtCliResource(
            project_dir=dbt_project,
            profiles_dir=Path.home() / ".dbt",
        ),
    },
)
