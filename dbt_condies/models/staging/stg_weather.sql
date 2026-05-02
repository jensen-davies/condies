with source as (
    select * from {{ source('raw', 'open_meteo_weather') }}
),

flattened as (
    select 
        source.fetch_date,
        source.crag_name,
        source.latitude,
        source.longitude,
        source.loaded_at,
        f.index as hour_index,
        source.raw_json:hourly.time[f.index]::timestamp as hour_at,
        source.raw_json:hourly.temperature_2m[f.index]::float as temperature_c,
        source.raw_json:hourly.precipitation[f.index]::float as precipitation_mm,                                                    
        source.raw_json:hourly.windspeed_10m[f.index]::float as windspeed_kmh,                                                       
        source.raw_json:hourly.wind_direction_10m[f.index]::int as wind_direction_deg,                                                  
        source.raw_json:hourly.weathercode[f.index]::int   as weathercode,
        source.raw_json:hourly.dewpoint_2m[f.index]::float as dewpoint_c                                                          
    from source,
          lateral flatten(input => source.raw_json:hourly.time) f
  )                                                                    
   
  select * from flattened