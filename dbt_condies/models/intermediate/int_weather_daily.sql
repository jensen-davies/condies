with weather as (
    select * from {{ ref('stg_weather') }}
),

daily as (
    select
        crag_name,
        fetch_date,
        date(hour_at)                             as day,
        round(min(temperature_c) * 9/5 + 32, 2)   as temp_min_f,
        round(max(temperature_c) * 9/5 + 32, 2)   as temp_max_f,
        round(sum(precipitation_mm) / 25.4, 2)    as precip_total_in,
        round(avg(windspeed_kmh) / 1.609, 2)      as windspeed_avg_mph,
        round(max(windspeed_kmh) / 1.609, 2)             as windspeed_max_mph,
        round(avg(temperature_c) * 9/5 + 32, 2)           as temp_avg_f,
        round(avg(dewpoint_c) * 9/5 + 32, 2)             as dewpoint_avg_f,
        round(max(dewpoint_c) * 9/5 + 32, 2)             as dewpoint_max_f
    from weather
    group by crag_name, fetch_date, date(hour_at)
)

select * from daily