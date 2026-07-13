with encounters as (
    select * from {{ ref('stg_encounters') }}
),

patients as (
    select patient_id, gender, race, ethnicity, birth_date, age_bucket, income
    from {{ ref('stg_patients') }}
),

primary_conditions as (
    select distinct on (encounter_id)
        encounter_id,
        condition_code as primary_diagnosis_code,
        condition_system as primary_diagnosis_system,
        condition_description   as primary_diagnosis_description
    from {{ ref('stg_conditions') }}
    order by encounter_id, onset_date desc
)

select
    e.encounter_id,
    e.patient_id,
    e.start_datetime,
    e.stop_datetime,
    e.encounter_class,
    e.encounter_description,
    e.reason_description,
    e.base_encounter_cost,
    e.total_claim_cost,
    e.payer_coverage,
    e.duration_hours,

    extract(year  from e.start_datetime)            as encounter_year,
    extract(month from e.start_datetime)            as encounter_month,
    date_trunc('month', e.start_datetime)           as encounter_month_start,

    p.gender,
    p.race,
    p.age_bucket,
    p.income,
    date_diff('year', p.birth_date,
        cast(e.start_datetime as date))             as age_at_encounter,

    pc.primary_diagnosis_system,
    pc.primary_diagnosis_code,
    pc.primary_diagnosis_description

from encounters e
left join patients p          on e.patient_id  = p.patient_id
left join primary_conditions pc on e.encounter_id = pc.encounter_id