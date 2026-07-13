import sys
import duckdb
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

DUCKDB_PATH = str(Path(__file__).parent.parent / "cliniq.duckdb")


def run_validation():
    con = duckdb.connect(DUCKDB_PATH)
    results = []

    def check(name, query, description):
        violations = con.execute(query).fetchdf()
        passed = len(violations) == 0
        results.append({
            "check": name,
            "description": description,
            "passed": passed,
            "violation_count": len(violations),
        })
        if not passed:
            print(f"  FAIL: {name} — {len(violations)} violations")
            print(violations.head(3).to_string())
        else:
            print(f"  PASS: {name}")
        return passed

    print("\n=== Running Clinical Data Quality Validations ===\n")

    print("--- dim_patients ---")
    check(
        "patient_age_range",
        "SELECT patient_id, age_at_generation FROM main_marts.dim_patients WHERE age_at_generation < 0 OR age_at_generation > 120",
        "Patient ages must be between 0 and 120 years"
    )
    check(
        "patient_gender_values",
        "SELECT patient_id, gender FROM main_marts.dim_patients WHERE gender NOT IN ('M', 'F')",
        "Gender must be M or F"
    )
    check(
        "patient_income_non_negative",
        "SELECT patient_id, income FROM main_marts.dim_patients WHERE income < 0",
        "Income cannot be negative"
    )
    check(
        "condition_flags_binary",
        "SELECT patient_id, has_diabetes FROM main_marts.dim_patients WHERE has_diabetes NOT IN (0, 1)",
        "Condition flags must be 0 or 1"
    )

    print("\n--- fact_lab_results ---")
    check(
        "a1c_physiological_range",
        """
        SELECT patient_id, loinc_code, value_numeric
        FROM main_marts.fact_lab_results
        WHERE loinc_code = '4548-4'
        AND (value_numeric < 2.0 OR value_numeric > 15.0)
        """,
        "A1c must be between 2.0 and 15.0 percent"
    )
    check(
        "glucose_physiological_range",
        """
        SELECT patient_id, loinc_code, value_numeric
        FROM main_marts.fact_lab_results
        WHERE loinc_code = '2339-0'
        AND (value_numeric < 20 OR value_numeric > 600)
        """,
        "Fasting glucose must be between 20 and 600 mg/dL"
    )
    check(
        "systolic_bp_range",
        """
        SELECT patient_id, loinc_code, value_numeric
        FROM main_marts.fact_lab_results
        WHERE loinc_code = '8480-6'
        AND (value_numeric < 50 OR value_numeric > 300)
        """,
        "Systolic BP must be between 50 and 300 mmHg"
    )
    check(
        "bmi_range",
        """
        SELECT patient_id, loinc_code, value_numeric
        FROM main_marts.fact_lab_results
        WHERE loinc_code = '39156-5'
        AND (value_numeric < 10 OR value_numeric > 80)
        """,
        "BMI must be between 10 and 80 kg/m2"
    )

    print("\n--- fact_encounters ---")
    check(
        "encounter_duration_non_negative",
        "SELECT encounter_id, duration_hours FROM main_marts.fact_encounters WHERE duration_hours < 0",
        "Encounter duration cannot be negative"
    )
    check(
        "encounter_cost_non_negative",
        "SELECT encounter_id, total_claim_cost FROM main_marts.fact_encounters WHERE total_claim_cost < 0",
        "Encounter cost cannot be negative"
    )

    con.close()

    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed
    pass_rate = 100 * passed / total

    print(f"\n=== Validation Summary ===")
    print(f"Total checks: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Pass rate: {pass_rate:.1f}%")

    if pass_rate < 90:
        print("\nFAILED: Pass rate below 90% threshold.")
        sys.exit(1)
    else:
        print("\nPASSED: Data quality sufficient to proceed.")
        return results


if __name__ == "__main__":
    run_validation()