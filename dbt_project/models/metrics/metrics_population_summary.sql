select
    count(*)                                        as total_patients,
    count(*) filter (where not is_deceased)         as alive_patients,
    count(*) filter (where is_deceased)             as deceased_patients,
    count(*) filter (where gender = 'M')            as male_patients,
    count(*) filter (where gender = 'F')            as female_patients,
    round(avg(age_at_generation), 1)                as average_age,
    count(*) filter (where has_diabetes = 1)        as diabetic_patients,
    count(*) filter (where has_hypertension = 1)    as hypertensive_patients,
    count(*) filter (where has_heart_failure = 1)   as heart_failure_patients,
    count(*) filter (where has_copd = 1)            as copd_patients,
    round(100.0 * count(*) filter (where gender = 'F') / count(*), 1)      as pct_female,
    round(100.0 * count(*) filter (where has_diabetes = 1) / count(*), 1)  as pct_diabetic

from {{ ref('dim_patients') }}