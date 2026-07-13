with source as (
    select * from delta_scan('{{ env_var("CLINIQ_PARQUET_DIR") }}/encounters')
),

renamed as (
    select
        "Id"                                        as encounter_id,
        cast("START" as timestamp)                  as start_datetime,
        cast("STOP" as timestamp)                   as stop_datetime,
        "PATIENT"                                   as patient_id,
        "ENCOUNTERCLASS"                            as encounter_class,
        "CODE"                                      as encounter_code,
        "DESCRIPTION"                               as encounter_description,
        "REASONCODE"                                as reason_code,
        "REASONDESCRIPTION"                         as reason_description,
        "BASE_ENCOUNTER_COST"                       as base_encounter_cost,
        "TOTAL_CLAIM_COST"                          as total_claim_cost,
        "PAYER_COVERAGE"                            as payer_coverage,

        date_diff('minute',
            cast("START" as timestamp),
            cast("STOP" as timestamp)
        ) / 60.0                                    as duration_hours

    from source
)

select * from renamed