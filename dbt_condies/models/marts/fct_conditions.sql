with daily as (
    select * from {{ ref('int_weather_daily') }}
),

windows as (
    select * from {{ ref('int_weather_windows') }}
),

-- Pivot long window rows into one wide row per crag/fetch/day
pivoted as (
    select
        crag_name,
        fetch_date,
        day,
        max(case when time_window = 'morning'   then min_temp_f        end) as morning_min_temp_f,
        max(case when time_window = 'morning'   then avg_temp_f        end) as morning_avg_temp_f,
        max(case when time_window = 'morning'   then max_temp_f        end) as morning_max_temp_f,
        max(case when time_window = 'morning'   then avg_dewpoint_f    end) as morning_avg_dewpoint_f,
        max(case when time_window = 'morning'   then total_precip_in   end) as morning_precip_in,
        max(case when time_window = 'morning'   then avg_windspeed_mph end) as morning_windspeed_mph,
        max(case when time_window = 'afternoon' then min_temp_f        end) as afternoon_min_temp_f,
        max(case when time_window = 'afternoon' then avg_temp_f        end) as afternoon_avg_temp_f,
        max(case when time_window = 'afternoon' then max_temp_f        end) as afternoon_max_temp_f,
        max(case when time_window = 'afternoon' then avg_dewpoint_f    end) as afternoon_avg_dewpoint_f,
        max(case when time_window = 'afternoon' then total_precip_in   end) as afternoon_precip_in,
        max(case when time_window = 'afternoon' then avg_windspeed_mph end) as afternoon_windspeed_mph,
        max(case when time_window = 'evening'   then min_temp_f        end) as evening_min_temp_f,
        max(case when time_window = 'evening'   then avg_temp_f        end) as evening_avg_temp_f,
        max(case when time_window = 'evening'   then max_temp_f        end) as evening_max_temp_f,
        max(case when time_window = 'evening'   then avg_dewpoint_f    end) as evening_avg_dewpoint_f,
        max(case when time_window = 'evening'   then total_precip_in   end) as evening_precip_in,
        max(case when time_window = 'evening'   then avg_windspeed_mph end) as evening_windspeed_mph
    from windows
    group by crag_name, fetch_date, day
),

joined as (
    select
        d.crag_name,
        d.fetch_date,
        d.day,
        d.temp_min_f,
        d.temp_max_f,
        d.temp_avg_f,
        d.precip_total_in,
        d.windspeed_avg_mph,
        d.windspeed_max_mph,
        d.dewpoint_avg_f,
        d.dewpoint_max_f,
        p.morning_min_temp_f,
        p.morning_avg_temp_f,
        p.morning_max_temp_f,
        p.morning_avg_dewpoint_f,
        p.morning_precip_in,
        p.morning_windspeed_mph,
        p.afternoon_min_temp_f,
        p.afternoon_avg_temp_f,
        p.afternoon_max_temp_f,
        p.afternoon_avg_dewpoint_f,
        p.afternoon_precip_in,
        p.afternoon_windspeed_mph,
        p.evening_min_temp_f,
        p.evening_avg_temp_f,
        p.evening_max_temp_f,
        p.evening_avg_dewpoint_f,
        p.evening_precip_in,
        p.evening_windspeed_mph
    from daily d
    join pivoted p
        on  d.crag_name  = p.crag_name
        and d.fetch_date = p.fetch_date
        and d.day        = p.day
),

-- Score each window independently: temp (60 pts) + dewpoint (40 pts) + wind bonus (3 pts)
-- multiplied by precipitation gate (any rain in window = 0)
components as (
    select
        *,

        -- Morning temperature score (60 pts)
        case
            when morning_avg_temp_f >= 44 and morning_avg_temp_f < 58 then 60
            when morning_avg_temp_f >= 58 and morning_avg_temp_f < 64 then 44
            when (morning_avg_temp_f >= 35 and morning_avg_temp_f < 44) or (morning_avg_temp_f >= 64 and morning_avg_temp_f < 68) then 30
            when (morning_avg_temp_f >= 28 and morning_avg_temp_f < 35) or (morning_avg_temp_f >= 68 and morning_avg_temp_f < 76) then 14
            else 0
        end as morning_temp_score,
        -- Morning dew point score (40 pts)
        case
            when morning_avg_dewpoint_f < 45 then 40
            when morning_avg_dewpoint_f < 50 then 28
            when morning_avg_dewpoint_f < 55 then 20
            when morning_avg_dewpoint_f < 60 then 12
            when morning_avg_dewpoint_f < 65 then 5
            else 0
        end as morning_dewpoint_score,
        -- Morning wind bonus (+3)
        case when morning_windspeed_mph between 5 and 15 then 3 else 0 end as morning_wind_bonus,
        -- Morning precipitation gate
        case when morning_precip_in = 0 then 1 else 0 end as morning_precip_multiplier,

        -- Afternoon temperature score (60 pts)
        case
            when afternoon_avg_temp_f >= 44 and afternoon_avg_temp_f < 58 then 60
            when afternoon_avg_temp_f >= 58 and afternoon_avg_temp_f < 64 then 44
            when (afternoon_avg_temp_f >= 35 and afternoon_avg_temp_f < 44) or (afternoon_avg_temp_f >= 64 and afternoon_avg_temp_f < 68) then 30
            when (afternoon_avg_temp_f >= 28 and afternoon_avg_temp_f < 35) or (afternoon_avg_temp_f >= 68 and afternoon_avg_temp_f < 76) then 14
            else 0
        end as afternoon_temp_score,
        -- Afternoon dew point score (40 pts)
        case
            when afternoon_avg_dewpoint_f < 45 then 40
            when afternoon_avg_dewpoint_f < 50 then 28
            when afternoon_avg_dewpoint_f < 55 then 20
            when afternoon_avg_dewpoint_f < 60 then 12
            when afternoon_avg_dewpoint_f < 65 then 5
            else 0
        end as afternoon_dewpoint_score,
        -- Afternoon wind bonus (+3)
        case when afternoon_windspeed_mph between 5 and 15 then 3 else 0 end as afternoon_wind_bonus,
        -- Afternoon precipitation gate
        case when afternoon_precip_in = 0 then 1 else 0 end as afternoon_precip_multiplier,

        -- Evening temperature score (60 pts)
        case
            when evening_avg_temp_f >= 44 and evening_avg_temp_f < 58 then 60
            when evening_avg_temp_f >= 58 and evening_avg_temp_f < 64 then 44
            when (evening_avg_temp_f >= 35 and evening_avg_temp_f < 44) or (evening_avg_temp_f >= 64 and evening_avg_temp_f < 68) then 30
            when (evening_avg_temp_f >= 28 and evening_avg_temp_f < 35) or (evening_avg_temp_f >= 68 and evening_avg_temp_f < 76) then 14
            else 0
        end as evening_temp_score,
        -- Evening dew point score (40 pts)
        case
            when evening_avg_dewpoint_f < 45 then 40
            when evening_avg_dewpoint_f < 50 then 28
            when evening_avg_dewpoint_f < 55 then 20
            when evening_avg_dewpoint_f < 60 then 12
            when evening_avg_dewpoint_f < 65 then 5
            else 0
        end as evening_dewpoint_score,
        -- Evening wind bonus (+3)
        case when evening_windspeed_mph between 5 and 15 then 3 else 0 end as evening_wind_bonus,
        -- Evening precipitation gate
        case when evening_precip_in = 0 then 1 else 0 end as evening_precip_multiplier

    from joined
),

window_scores as (
    select
        *,
        (morning_temp_score   + morning_dewpoint_score   + morning_wind_bonus)   * morning_precip_multiplier   as morning_score,
        (afternoon_temp_score + afternoon_dewpoint_score + afternoon_wind_bonus) * afternoon_precip_multiplier as afternoon_score,
        (evening_temp_score   + evening_dewpoint_score   + evening_wind_bonus)   * evening_precip_multiplier   as evening_score
    from components
)

select
    crag_name,
    fetch_date,
    day,
    -- daily context
    temp_min_f,
    temp_max_f,
    temp_avg_f,
    precip_total_in,
    windspeed_avg_mph,
    windspeed_max_mph,
    dewpoint_avg_f,
    dewpoint_max_f,
    -- morning window
    morning_min_temp_f,
    morning_avg_temp_f,
    morning_max_temp_f,
    morning_avg_dewpoint_f,
    morning_precip_in,
    morning_windspeed_mph,
    morning_score,
    -- afternoon window
    afternoon_min_temp_f,
    afternoon_avg_temp_f,
    afternoon_max_temp_f,
    afternoon_avg_dewpoint_f,
    afternoon_precip_in,
    afternoon_windspeed_mph,
    afternoon_score,
    -- evening window
    evening_min_temp_f,
    evening_avg_temp_f,
    evening_max_temp_f,
    evening_avg_dewpoint_f,
    evening_precip_in,
    evening_windspeed_mph,
    evening_score,
    -- overall: average of the three window scores
    round((morning_score + afternoon_score + evening_score) / 3.0, 1) as climbability_score
from window_scores
