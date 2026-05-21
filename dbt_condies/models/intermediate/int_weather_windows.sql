with hourly as (
    select * from {{ ref('stg_weather') }}
),

windowed as (
    select
        crag_name,
        fetch_date,
        date(hour_at)                                      as day,
        case
            when extract(hour from hour_at) between 7  and 11 then 'morning'
            when extract(hour from hour_at) between 12 and 17 then 'afternoon'
            when extract(hour from hour_at) between 18 and 23 then 'evening'
        end                                                as time_window,
        round(min(temperature_c) * 9/5 + 32, 1)           as min_temp_f,
        round(avg(temperature_c) * 9/5 + 32, 1)           as avg_temp_f,
        round(max(temperature_c) * 9/5 + 32, 1)           as max_temp_f,
        round(avg(dewpoint_c) * 9/5 + 32, 2)              as avg_dewpoint_f,
        round(sum(precipitation_mm) / 25.4, 2)            as total_precip_in,
        round(avg(windspeed_kmh) / 1.609, 2)              as avg_windspeed_mph
    from hourly
    where extract(hour from hour_at) between 7 and 23
    group by crag_name, fetch_date, date(hour_at), time_window
)

select * from windowed
