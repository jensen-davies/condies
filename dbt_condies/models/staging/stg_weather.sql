with source as (
    select * from {{ source('raw', 'open_meteo_weather') }}
),

-- Keep only the most recent fetch per crag per date — raw layer is append-only
latest as (
    select *
    from source
    qualify row_number() over (
        partition by crag_name, fetch_date
        order by loaded_at desc
    ) = 1
),

flattened as (
    select
        latest.fetch_date,
        latest.crag_name,
        latest.latitude,
        latest.longitude,
        latest.loaded_at,
        f.index as hour_index,
        latest.raw_json:hourly.time[f.index]::timestamp as hour_at,
        latest.raw_json:hourly.temperature_2m[f.index]::float as temperature_c,
        latest.raw_json:hourly.precipitation[f.index]::float as precipitation_mm,
        latest.raw_json:hourly.windspeed_10m[f.index]::float as windspeed_kmh,
        latest.raw_json:hourly.wind_direction_10m[f.index]::int as wind_direction_deg,
        latest.raw_json:hourly.weathercode[f.index]::int   as weathercode,
        latest.raw_json:hourly.dewpoint_2m[f.index]::float as dewpoint_c                                                          
    from latest,
          lateral flatten(input => latest.raw_json:hourly.time) f
  )                                                                    
   
  select * from flattened