with patients as (
    select * from {{ ref('stg_patients') }}
),

conditions as (
    select
        patient_id,
        condition_system,
        condition_code
    from {{ ref('stg_conditions') }}
    where is_active = true
),

condition_map as (
    select * from {{ ref('condition_concept_map') }}
),

condition_flags as (
    select
        c.patient_id,

        max(case when m.condition_group = 'diabetes' then 1 else 0 end) as has_diabetes,
        max(case when m.condition_group = 'hypertension' then 1 else 0 end) as has_hypertension,
        max(case when m.condition_group = 'copd' then 1 else 0 end) as has_copd,
        max(case when m.condition_group = 'heart_failure' then 1 else 0 end) as has_heart_failure,
        max(case when m.condition_group = 'ckd' then 1 else 0 end) as has_ckd,
        max(case when m.condition_group = 'asthma' then 1 else 0 end) as has_asthma

    from conditions c
    left join condition_map m
        on c.condition_system = m.condition_system
       and c.condition_code = m.condition_code
    group by c.patient_id
),

latest_a1c as (
    select patient_id, value_numeric as latest_a1c_value
    from (
        select
            patient_id,
            value_numeric,
            row_number() over (partition by patient_id order by observation_date desc) as rn
        from {{ ref('stg_observations') }}
        where loinc_code = '4548-4'
        and value_numeric is not null
    ) t
    where rn = 1
),

latest_bmi as (
    select patient_id, value_numeric as latest_bmi_value
    from (
        select
            patient_id,
            value_numeric,
            row_number() over (partition by patient_id order by observation_date desc) as rn
        from {{ ref('stg_observations') }}
        where loinc_code = '39156-5'
        and value_numeric is not null
    ) t
    where rn = 1
)

select
    p.patient_id,
    p.birth_date,
    p.death_date,
    p.gender,
    p.race,
    p.ethnicity,
    p.city,
    p.state,
    p.income,
    p.is_deceased,
    p.age_at_generation,
    p.age_bucket,
    p.healthcare_expenses,
    p.healthcare_coverage,

    coalesce(cf.has_diabetes, 0)      as has_diabetes,
    coalesce(cf.has_hypertension, 0)  as has_hypertension,
    coalesce(cf.has_copd, 0)          as has_copd,
    coalesce(cf.has_heart_failure, 0) as has_heart_failure,
    coalesce(cf.has_ckd, 0)           as has_ckd,
    coalesce(cf.has_asthma, 0)        as has_asthma,

    la.latest_a1c_value,
    lb.latest_bmi_value

from patients p
left join condition_flags cf on p.patient_id = cf.patient_id
left join latest_a1c la      on p.patient_id = la.patient_id
left join latest_bmi lb      on p.patient_id = lb.patient_id