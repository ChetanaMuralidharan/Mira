with total_patients as (
    select count(*) as n from {{ ref('dim_patients') }}
)

select
    c.condition_system,
    c.condition_code,
    c.condition_description,
    count(distinct c.patient_id)                          as patient_count,
    round(100.0 * count(distinct c.patient_id) / t.n, 2) as prevalence_pct

from {{ ref('stg_conditions') }} c
cross join total_patients t
where c.is_active = true
group by c.condition_system, c.condition_code, c.condition_description, t.n
order by patient_count desc