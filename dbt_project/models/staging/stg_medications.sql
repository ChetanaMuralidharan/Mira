with source as (
    select * from delta_scan('{{ env_var("CLINIQ_PARQUET_DIR") }}/medications')
),

renamed as (
    select
        "PATIENT"               as patient_id,
        "ENCOUNTER"             as encounter_id,
        "CODE"                  as rxnorm_code,
        "DESCRIPTION"           as medication_name,
        cast("START" as date)   as start_date,
        cast("STOP" as date)    as stop_date,

        "STOP" is null          as is_active,

        case
            when "STOP" is not null
            then date_diff('day', cast("START" as date), cast("STOP" as date))
            else null
        end                     as duration_days,

        "BASE_COST"             as base_cost,
        "TOTALCOST"             as total_cost,
        "REASONCODE"            as reason_code,
        "REASONDESCRIPTION"     as reason_description

    from source
)

select * from renamed