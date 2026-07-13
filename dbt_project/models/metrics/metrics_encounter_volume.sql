select
    encounter_year,
    encounter_month,
    encounter_month_start,
    encounter_class,
    count(*)                as encounter_count,
    avg(total_claim_cost)   as avg_claim_cost,
    sum(total_claim_cost)   as total_revenue

from {{ ref('fact_encounters') }}
group by
    encounter_year,
    encounter_month,
    encounter_month_start,
    encounter_class
order by
    encounter_year,
    encounter_month,
    encounter_class