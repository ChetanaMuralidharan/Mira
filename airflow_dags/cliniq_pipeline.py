from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.empty import EmptyOperator
import os
import sys
import subprocess

CLINIQ_HOME = "/opt/cliniq"
PARQUET_DIR = f"{CLINIQ_HOME}/data/parquet/raw"
DBT_PROJECT_DIR = f"{CLINIQ_HOME}/dbt_project"
DBT_BIN = "/home/airflow/.local/bin/dbt"

default_args = {
    "owner": "cliniq",
    "depends_on_past": False,
    "start_date": datetime(2025, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "cliniq_data_pipeline",
    default_args=default_args,
    description="ClinIQ Phase 1: Full data pipeline",
    schedule_interval="0 2 * * *",
    catchup=False,
    tags=["cliniq", "phase1"],
)


def check_delta_tables_exist():
    from pathlib import Path
    required = ["patients", "encounters", "conditions", "observations", "medications"]
    all_exist = all(
        (Path(PARQUET_DIR) / t / "_delta_log").exists()
        for t in required
    )
    return "skip_generation" if all_exist else "generate_delta_tables"


def run_ge_validation():
    sys.path.insert(0, CLINIQ_HOME)
    os.environ["CLINIQ_PARQUET_DIR"] = PARQUET_DIR
    from pipeline.run_great_expectations import run_validation
    run_validation()


def run_schema_registry_update():
    sys.path.insert(0, CLINIQ_HOME)
    from pipeline.update_schema_registry import build_schema_registry
    build_schema_registry()

def run_vector_store_update(**context):
    """
    Incrementally re-embeds any new or changed documents.
    Only processes files whose MD5 hash has changed since last run.
    """
    result = subprocess.run(
       [sys.executable, f"{CLINIQ_HOME}/vector_store/embed_documents.py"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise Exception(f"Vector store update failed:\n{result.stderr}")
    print(result.stdout)

check_raw_data = BranchPythonOperator(
    task_id="check_raw_data",
    python_callable=check_delta_tables_exist,
    dag=dag,
)

skip_generation = EmptyOperator(
    task_id="skip_generation",
    dag=dag,
)

generate_delta_tables = BashOperator(
    task_id="generate_delta_tables",
    bash_command=f"cd {CLINIQ_HOME} && python pipeline/convert_to_delta.py",
    env={"CLINIQ_PARQUET_DIR": PARQUET_DIR, "HOME": "/tmp"},
    append_env=True,
    dag=dag,
)

dbt_env = {
    "CLINIQ_PARQUET_DIR": PARQUET_DIR,
    "HOME": "/tmp",
}
dbt_flags = f"--profiles-dir {DBT_PROJECT_DIR} --profile cliniq_dbt"

run_dbt_staging = BashOperator(
    task_id="run_dbt_staging",
    bash_command=f"cd {DBT_PROJECT_DIR} && {DBT_BIN} run --select staging {dbt_flags}",
    env=dbt_env,
    append_env=True,
    trigger_rule="none_failed_min_one_success",
    dag=dag,
)

run_dbt_marts = BashOperator(
    task_id="run_dbt_marts",
    bash_command=f"cd {DBT_PROJECT_DIR} && {DBT_BIN} run --select marts {dbt_flags}",
    env=dbt_env,
    append_env=True,
    dag=dag,
)

run_dbt_metrics = BashOperator(
    task_id="run_dbt_metrics",
    bash_command=f"cd {DBT_PROJECT_DIR} && {DBT_BIN} run --select metrics {dbt_flags}",
    env=dbt_env,
    append_env=True,
    dag=dag,
)

run_dbt_tests = BashOperator(
    task_id="run_dbt_tests",
    bash_command=f"cd {DBT_PROJECT_DIR} && {DBT_BIN} test {dbt_flags}",
    env=dbt_env,
    append_env=True,
    dag=dag,
)

run_great_expectations = PythonOperator(
    task_id="run_great_expectations",
    python_callable=run_ge_validation,
    dag=dag,
)

update_schema_registry = PythonOperator(
    task_id="update_schema_registry",
    python_callable=run_schema_registry_update,
    dag=dag,
)

update_vector_store = PythonOperator(
    task_id="update_vector_store",
    python_callable=run_vector_store_update,
    dag=dag,
)

# Wire the DAG
check_raw_data >> [skip_generation, generate_delta_tables]
[skip_generation, generate_delta_tables] >> run_dbt_staging
run_dbt_staging >> run_dbt_marts >> run_dbt_metrics >> run_dbt_tests
run_dbt_tests >> run_great_expectations >> update_schema_registry
update_schema_registry >> update_vector_store