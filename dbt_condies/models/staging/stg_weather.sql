with source as (
    select * from {{ source('raw', 'open_meteo_weather') }}
),

-- QUALIFY is Snowflake-only; BigQuery requires a ranked CTE + WHERE filter
ranked as (
    select
        *,
        row_number() over (
            partition by crag_name, fetch_date
            order by loaded_at desc
        ) as rn
    from source
),

-- Keep only the most recent fetch per crag per date — raw layer is append-only
latest as (
    select * except (rn)
    from ranked
    where rn = 1
),

-- Pre-extract all hourly arrays from the JSON blob into typed BigQuery arrays
arrays as (
    select
        fetch_date,
        crag_name,
        latitude,
        longitude,
        loaded_at,
        json_value_array(raw_json, '$.hourly.time')               as times,
        json_value_array(raw_json, '$.hourly.temperature_2m')     as temperatures,
        json_value_array(raw_json, '$.hourly.precipitation')      as precipitations,
        json_value_array(raw_json, '$.hourly.windspeed_10m')      as windspeeds,
        json_value_array(raw_json, '$.hourly.wind_direction_10m') as wind_directions,
        json_value_array(raw_json, '$.hourly.weathercode')        as weathercodes,
        json_value_array(raw_json, '$.hourly.dewpoint_2m')        as dewpoints
    from latest
),

-- LATERAL FLATTEN equivalent: generate an integer index per hour and unnest it
flattened as (
    select
        fetch_date,
        crag_name,
        latitude,
        longitude,
        loaded_at,
        hour_index,
        parse_datetime('%Y-%m-%dT%H:%M', times[safe_offset(hour_index)])         as hour_at,
        safe_cast(temperatures[safe_offset(hour_index)]  as float64)              as temperature_c,
        safe_cast(precipitations[safe_offset(hour_index)] as float64)             as precipitation_mm,
        safe_cast(windspeeds[safe_offset(hour_index)]    as float64)              as windspeed_kmh,
        safe_cast(wind_directions[safe_offset(hour_index)] as int64)              as wind_direction_deg,
        safe_cast(weathercodes[safe_offset(hour_index)]  as int64)                as weathercode,
        safe_cast(dewpoints[safe_offset(hour_index)]     as float64)              as dewpoint_c
    from arrays
    cross join unnest(generate_array(0, array_length(times) - 1)) as hour_index
)

select * from flattened