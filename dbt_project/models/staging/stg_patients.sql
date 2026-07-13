with source as (
    select * from delta_scan('{{ env_var("CLINIQ_PARQUET_DIR") }}/patients')
),

renamed as (
    select
        "Id"                                        as patient_id,
        cast("BIRTHDATE" as date)                   as birth_date,
        cast("DEATHDATE" as date)                   as death_date,
        "GENDER"                                    as gender,
        "RACE"                                      as race,
        "ETHNICITY"                                 as ethnicity,
        "CITY"                                      as city,
        "STATE"                                     as state,
        "COUNTY"                                    as county,
        "INCOME"                                    as income,
        "HEALTHCARE_EXPENSES"                       as healthcare_expenses,
        "HEALTHCARE_COVERAGE"                       as healthcare_coverage,

        "DEATHDATE" is not null                     as is_deceased,

        date_diff('year',
            cast("BIRTHDATE" as date),
            coalesce(cast("DEATHDATE" as date), current_date)
        )                                           as age_at_generation,

        case
            when date_diff('year', cast("BIRTHDATE" as date),
                coalesce(cast("DEATHDATE" as date), current_date)) < 18  then '0-17'
            when date_diff('year', cast("BIRTHDATE" as date),
                coalesce(cast("DEATHDATE" as date), current_date)) < 45  then '18-44'
            when date_diff('year', cast("BIRTHDATE" as date),
                coalesce(cast("DEATHDATE" as date), current_date)) < 65  then '45-64'
            else '65+'
        end                                         as age_bucket

    from source
)

select * from renamed