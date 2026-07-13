with source as (
    select * from delta_scan('{{ env_var("CLINIQ_PARQUET_DIR") }}/conditions')
),

renamed as (
    select
        "PATIENT"               as patient_id,
        "ENCOUNTER"             as encounter_id,
        "SYSTEM"                as condition_system,
        "CODE"                  as condition_code,
        "DESCRIPTION"           as condition_description,
        cast("START" as date)   as onset_date,
        cast("STOP" as date)    as resolution_date,
        "STOP" is null          as is_active
    from source
)

select * from renamed