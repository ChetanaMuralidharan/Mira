from pathlib import Path

import duckdb
import great_expectations as gx


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DUCKDB_PATH = PROJECT_ROOT / "cliniq.duckdb"
GX_ROOT = PROJECT_ROOT / "great_expectations"


def get_or_create_pandas_datasource(context, datasource_name: str):
    try:
        return context.data_sources.get(datasource_name)
    except Exception:
        return context.data_sources.add_pandas(name=datasource_name)


def get_or_create_dataframe_asset(datasource, asset_name: str):
    try:
        return datasource.get_asset(asset_name)
    except Exception:
        return datasource.add_dataframe_asset(name=asset_name)


def get_or_create_batch_definition(asset, batch_definition_name: str):
    try:
        return asset.get_batch_definition(batch_definition_name)
    except Exception:
        return asset.add_batch_definition_whole_dataframe(batch_definition_name)


def replace_suite(context, suite_name: str, expectations: list):
    try:
        context.suites.delete(name=suite_name)
    except Exception:
        pass

    suite = gx.ExpectationSuite(name=suite_name)
    suite = context.suites.add(suite)

    for expectation in expectations:
        suite.add_expectation(expectation)

    return suite


def get_or_create_validation_definition(context, name: str, batch_definition, suite):
    try:
        context.validation_definitions.delete(name=name)
    except Exception:
        pass

    validation_definition = gx.ValidationDefinition(
        name=name,
        data=batch_definition,
        suite=suite,
    )

    return context.validation_definitions.add(validation_definition)


def load_tables_from_duckdb():
    if not DUCKDB_PATH.exists():
        raise FileNotFoundError(f"DuckDB database not found: {DUCKDB_PATH}")

    con = duckdb.connect(str(DUCKDB_PATH), read_only=True)

    dim_patients_df = con.execute(
        "SELECT * FROM cliniq.main_marts.dim_patients"
    ).df()

    fact_lab_results_df = con.execute(
        "SELECT * FROM cliniq.main_marts.fact_lab_results"
    ).df()

    fact_encounters_df = con.execute(
        "SELECT * FROM cliniq.main_marts.fact_encounters"
    ).df()

    con.close()

    return dim_patients_df, fact_lab_results_df, fact_encounters_df


def print_failed_expectations(result, suite_name):
    if result.success:
        print(f"{suite_name}: PASSED")
        return

    print(f"\n{suite_name}: FAILED")

    for item in result.results:
        if not item.success:
            expectation_type = item.expectation_config.type
            kwargs = item.expectation_config.kwargs
            unexpected_count = item.result.get("unexpected_count")
            unexpected_percent = item.result.get("unexpected_percent")
            partial_unexpected = item.result.get("partial_unexpected_list")

            print(f"\nExpectation: {expectation_type}")
            print(f"Column/details: {kwargs}")
            print(f"Unexpected count: {unexpected_count}")
            print(f"Unexpected percent: {unexpected_percent}")
            print(f"Examples: {partial_unexpected}")


def run_validation():
    print("Running Great Expectations validation...")

    context = gx.get_context(context_root_dir=str(GX_ROOT))

    dim_patients_df, fact_lab_results_df, fact_encounters_df = load_tables_from_duckdb()

    datasource = get_or_create_pandas_datasource(
        context=context,
        datasource_name="mira_pandas_duckdb",
    )

    dim_asset = get_or_create_dataframe_asset(datasource, "dim_patients")
    lab_asset = get_or_create_dataframe_asset(datasource, "fact_lab_results")
    encounter_asset = get_or_create_dataframe_asset(datasource, "fact_encounters")

    dim_batch_definition = get_or_create_batch_definition(
        dim_asset,
        "dim_patients_whole_dataframe",
    )

    lab_batch_definition = get_or_create_batch_definition(
        lab_asset,
        "fact_lab_results_whole_dataframe",
    )

    encounter_batch_definition = get_or_create_batch_definition(
        encounter_asset,
        "fact_encounters_whole_dataframe",
    )

    dim_suite = replace_suite(
        context,
        "dim_patients_suite",
        [
            gx.expectations.ExpectColumnValuesToNotBeNull(column="patient_id"),
            gx.expectations.ExpectColumnValuesToBeUnique(column="patient_id"),
            gx.expectations.ExpectColumnValuesToBeBetween(
                column="age_at_generation",
                min_value=0,
                max_value=120,
            ),
            gx.expectations.ExpectColumnValuesToBeInSet(
                column="gender",
                value_set=["M", "F"],
            ),
            gx.expectations.ExpectColumnValuesToBeBetween(
                column="income",
                min_value=0,
            ),
            gx.expectations.ExpectColumnValuesToBeInSet(
                column="has_diabetes",
                value_set=[0, 1],
            ),
            gx.expectations.ExpectColumnValuesToBeInSet(
                column="has_hypertension",
                value_set=[0, 1],
            ),
            gx.expectations.ExpectColumnValuesToBeInSet(
                column="has_copd",
                value_set=[0, 1],
            ),
            gx.expectations.ExpectColumnValuesToBeInSet(
                column="has_heart_failure",
                value_set=[0, 1],
            ),
            gx.expectations.ExpectColumnValuesToBeInSet(
                column="has_ckd",
                value_set=[0, 1],
            ),
            gx.expectations.ExpectColumnValuesToBeInSet(
                column="has_asthma",
                value_set=[0, 1],
            ),
        ],
    )

    lab_suite = replace_suite(
        context,
        "fact_lab_results_suite",
        [
            gx.expectations.ExpectColumnValuesToNotBeNull(column="patient_id"),
            gx.expectations.ExpectColumnValuesToNotBeNull(column="loinc_code"),
            gx.expectations.ExpectColumnValuesToBeBetween(
                column="value_numeric",
                min_value=2.0,
                max_value=15.0,
                row_condition="loinc_code == '4548-4'",
                condition_parser="pandas",
            ),
            gx.expectations.ExpectColumnValuesToBeBetween(
                column="value_numeric",
                min_value=20,
                max_value=600,
                row_condition="loinc_code == '2339-0'",
                condition_parser="pandas",
            ),
            gx.expectations.ExpectColumnValuesToBeBetween(
                column="value_numeric",
                min_value=40,
                max_value=300,
                row_condition="loinc_code == '8480-6'",
                condition_parser="pandas",
                mostly=0.999,
            ),
            gx.expectations.ExpectColumnValuesToBeBetween(
                column="value_numeric",
                min_value=10,
                max_value=80,
                row_condition="loinc_code == '39156-5'",
                condition_parser="pandas",
            ),
        ],
    )

    encounter_suite = replace_suite(
        context,
        "fact_encounters_suite",
        [
            gx.expectations.ExpectColumnValuesToNotBeNull(column="encounter_id"),
            gx.expectations.ExpectColumnValuesToBeUnique(column="encounter_id"),
            gx.expectations.ExpectColumnValuesToNotBeNull(column="patient_id"),
            gx.expectations.ExpectColumnValuesToBeBetween(
                column="duration_hours",
                min_value=0,
            ),
            gx.expectations.ExpectColumnValuesToBeBetween(
                column="total_claim_cost",
                min_value=0,
            ),
            gx.expectations.ExpectColumnPairValuesAToBeGreaterThanB(
                column_A="stop_datetime",
                column_B="start_datetime",
                or_equal=True,
            ),
        ],
    )

    dim_validation = get_or_create_validation_definition(
        context,
        "dim_patients_validation",
        dim_batch_definition,
        dim_suite,
    )

    lab_validation = get_or_create_validation_definition(
        context,
        "fact_lab_results_validation",
        lab_batch_definition,
        lab_suite,
    )

    encounter_validation = get_or_create_validation_definition(
        context,
        "fact_encounters_validation",
        encounter_batch_definition,
        encounter_suite,
    )

    print("Validating dim_patients...")
    dim_result = dim_validation.run(
        batch_parameters={"dataframe": dim_patients_df}
    )

    print("Validating fact_lab_results...")
    lab_result = lab_validation.run(
        batch_parameters={"dataframe": fact_lab_results_df}
    )

    print("Validating fact_encounters...")
    encounter_result = encounter_validation.run(
        batch_parameters={"dataframe": fact_encounters_df}
    )

    print_failed_expectations(dim_result, "dim_patients_suite")
    print_failed_expectations(lab_result, "fact_lab_results_suite")
    print_failed_expectations(encounter_result, "fact_encounters_suite")

    print("Building Great Expectations Data Docs...")
    context.build_data_docs()

    all_success = (
        dim_result.success
        and lab_result.success
        and encounter_result.success
    )

    if not all_success:
        raise Exception(
            "Great Expectations validation failed. "
            "Open great_expectations/uncommitted/data_docs/local_site/index.html"
        )

    print("Great Expectations validation passed.")

    return {
        "dim_patients": dim_result.success,
        "fact_lab_results": lab_result.success,
        "fact_encounters": encounter_result.success,
    }


if __name__ == "__main__":
    run_validation()