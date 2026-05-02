from pathlib import Path

from dagster import AssetKey
from dagster_dbt import DbtProject, DbtCliResource, DagsterDbtTranslator, dbt_assets

DBT_PROJECT_DIR = Path(__file__).parent.parent.parent / "dbt_condies"

dbt_project = DbtProject(project_dir=DBT_PROJECT_DIR)


class CondiesDbtTranslator(DagsterDbtTranslator):
    def get_asset_key(self, dbt_resource_props):
        # Map the dbt source open_meteo_weather to the raw_weather Dagster asset
        if (
            dbt_resource_props["resource_type"] == "source"
            and dbt_resource_props["name"] == "open_meteo_weather"
        ):
            return AssetKey("raw_weather")
        return super().get_asset_key(dbt_resource_props)


@dbt_assets(manifest=dbt_project.manifest_path, dagster_dbt_translator=CondiesDbtTranslator())
def condies_dbt_assets(context, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()
