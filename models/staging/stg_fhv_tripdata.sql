{{ config(materialized='view') }}

with tripdata as 
(
  select *
  from {{ source('staging','fhv_2019_trips') }}
)

select
    dispatching_base_num,

    -- timestamps
    cast(pickup_datetime as timestamp) as pickup_datetime,
    cast(dropOff_datetime as timestamp) as dropoff_datetime,
    
    -- identifiers
    {{ dbt.safe_cast("PUlocationID", api.Column.translate_type("integer")) }} as pickup_locationid,
    {{ dbt.safe_cast("DOlocationID", api.Column.translate_type("integer")) }} as dropoff_locationid,

    SR_Flag as sr_flag,
    Affiliated_base_number as affiliated_base_number
from tripdata

-- {% if var('is_test_run', default=true) %}
--     limit 100
-- {% endif %}

