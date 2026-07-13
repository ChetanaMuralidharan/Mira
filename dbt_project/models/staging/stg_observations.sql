with source as (
    select * from delta_scan('{{ env_var("CLINIQ_PARQUET_DIR") }}/observations')
),

renamed as (
    select
        cast("DATE" as date)    as observation_date,
        "PATIENT"               as patient_id,
        "ENCOUNTER"             as encounter_id,
        "CATEGORY"              as observation_category,
        "CODE"                  as loinc_code,
        "DESCRIPTION"           as observation_description,
        "VALUE"                 as raw_value,
        "UNITS"                 as units,
        "TYPE"                  as value_type,

        case
            when "TYPE" = 'numeric' then try_cast("VALUE" as float)
            else null
        end                     as value_numeric,

        case
            when "TYPE" != 'numeric' then "VALUE"
            else null
        end                     as value_text

    from source
)

select * from renamed