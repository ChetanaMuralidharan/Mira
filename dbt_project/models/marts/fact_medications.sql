with medications as (
    select * from {{ ref('stg_medications') }}
),

patients as (
    select * from {{ ref('dim_patients') }}
),

drug_classes as (
    select * from {{ ref('drug_classes') }}
),

drug_class_matches as (
    select
        m.patient_id,
        m.encounter_id,
        m.rxnorm_code,
        m.start_date,
        string_agg(distinct dc.drug_class, ', ') as drug_classes,
        -- string_agg(distinct dc.drug_subclass, ', ') as drug_subclasses

    from medications m
    left join drug_classes dc
        on m.medication_name ilike '%' || dc.medication_name_pattern || '%'

    group by
        m.patient_id,
        m.encounter_id,
        m.rxnorm_code,
        m.start_date
)

select
    m.patient_id,
    m.encounter_id,
    m.rxnorm_code,
    m.medication_name,
    dcm.drug_classes,
    -- dcm.drug_subclasses,
    m.start_date,
    m.stop_date,
    m.is_active,
    m.duration_days,

    p.age_at_generation,
    p.gender,
    p.race,
    p.ethnicity,
    p.has_diabetes,
    p.has_hypertension,
    p.has_copd,
    p.has_heart_failure,
    p.has_ckd,
    p.has_asthma

from medications m
left join patients p
    on m.patient_id = p.patient_id
left join drug_class_matches dcm
    on m.patient_id = dcm.patient_id
   and m.encounter_id = dcm.encounter_id
   and m.rxnorm_code = dcm.rxnorm_code
   and m.start_date = dcm.start_date