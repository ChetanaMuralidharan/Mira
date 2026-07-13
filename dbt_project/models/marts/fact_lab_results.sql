with labs as (
    select * from {{ ref('stg_observations') }}
    where observation_category in ('laboratory', 'vital-signs')
    and value_numeric is not null
),

patients as (
    select patient_id, gender, age_bucket, age_at_generation
    from {{ ref('stg_patients') }}
),

normal_ranges as (
    select * from {{ ref('loinc_normal_ranges') }}
)

select
    l.patient_id,
    l.encounter_id,
    l.observation_date,
    l.loinc_code,
    l.observation_description   as test_name,
    l.value_numeric,
    l.units,

    p.gender,
    p.age_bucket,
    p.age_at_generation,

    extract(year  from l.observation_date)  as result_year,
    extract(month from l.observation_date)  as result_month,

    case
        when nr.normal_low  is not null and nr.normal_high is not null
            then l.value_numeric < nr.normal_low or l.value_numeric > nr.normal_high
        when nr.normal_low  is not null
            then l.value_numeric < nr.normal_low
        when nr.normal_high is not null
            then l.value_numeric > nr.normal_high
        else null
    end as is_abnormal,

    nr.normal_low,
    nr.normal_high

from labs l
left join patients p      on l.patient_id  = p.patient_id
left join normal_ranges nr on l.loinc_code = nr.loinc_code