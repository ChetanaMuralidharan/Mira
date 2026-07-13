"""
Phase 1A: Convert Synthea CSVs to Delta Lake tables (Bronze tier).

Why Delta Lake over raw CSVs:
- Columnar Parquet format: 10-100x faster for analytical queries
- ACID transactions: failed writes never corrupt the table
- Schema enforcement: column types cannot change accidentally
- Time travel: query historical versions for debugging
"""

import os
import sys
import logging
from pathlib import Path
import pyarrow as pa
import pyarrow.csv as pa_csv
from deltalake import write_deltalake, DeltaTable

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import RAW_DIR, PARQUET_DIR

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SCHEMAS = {
    "patients": pa.schema([
        pa.field("Id", pa.string()),
        pa.field("BIRTHDATE", pa.string()),
        pa.field("DEATHDATE", pa.string()),
        pa.field("SSN", pa.string()),
        pa.field("DRIVERS", pa.string()),
        pa.field("PASSPORT", pa.string()),
        pa.field("PREFIX", pa.string()),
        pa.field("FIRST", pa.string()),
        pa.field("LAST", pa.string()),
        pa.field("SUFFIX", pa.string()),
        pa.field("MAIDEN", pa.string()),
        pa.field("MARITAL", pa.string()),
        pa.field("RACE", pa.string()),
        pa.field("ETHNICITY", pa.string()),
        pa.field("GENDER", pa.string()),
        pa.field("BIRTHPLACE", pa.string()),
        pa.field("ADDRESS", pa.string()),
        pa.field("CITY", pa.string()),
        pa.field("STATE", pa.string()),
        pa.field("COUNTY", pa.string()),
        pa.field("FIPS", pa.string()),
        pa.field("ZIP", pa.string()),
        pa.field("LAT", pa.float64()),
        pa.field("LON", pa.float64()),
        pa.field("HEALTHCARE_EXPENSES", pa.float64()),
        pa.field("HEALTHCARE_COVERAGE", pa.float64()),
        pa.field("INCOME", pa.int64()),
    ]),
    "encounters": pa.schema([
        pa.field("Id", pa.string()),
        pa.field("START", pa.string()),
        pa.field("STOP", pa.string()),
        pa.field("PATIENT", pa.string()),
        pa.field("ORGANIZATION", pa.string()),
        pa.field("PROVIDER", pa.string()),
        pa.field("PAYER", pa.string()),
        pa.field("ENCOUNTERCLASS", pa.string()),
        pa.field("CODE", pa.string()),
        pa.field("DESCRIPTION", pa.string()),
        pa.field("BASE_ENCOUNTER_COST", pa.float64()),
        pa.field("TOTAL_CLAIM_COST", pa.float64()),
        pa.field("PAYER_COVERAGE", pa.float64()),
        pa.field("REASONCODE", pa.string()),
        pa.field("REASONDESCRIPTION", pa.string()),
    ]),
    "conditions": pa.schema([
        pa.field("START", pa.string()),
        pa.field("STOP", pa.string()),
        pa.field("PATIENT", pa.string()),
        pa.field("ENCOUNTER", pa.string()),
        pa.field("CODE", pa.string()),
        pa.field("DESCRIPTION", pa.string()),
    ]),
    "observations": pa.schema([
        pa.field("DATE", pa.string()),
        pa.field("PATIENT", pa.string()),
        pa.field("ENCOUNTER", pa.string()),
        pa.field("CATEGORY", pa.string()),
        pa.field("CODE", pa.string()),
        pa.field("DESCRIPTION", pa.string()),
        pa.field("VALUE", pa.string()),
        pa.field("UNITS", pa.string()),
        pa.field("TYPE", pa.string()),
    ]),
    "medications": pa.schema([
        pa.field("START", pa.string()),
        pa.field("STOP", pa.string()),
        pa.field("PATIENT", pa.string()),
        pa.field("PAYER", pa.string()),
        pa.field("ENCOUNTER", pa.string()),
        pa.field("CODE", pa.string()),
        pa.field("DESCRIPTION", pa.string()),
        pa.field("BASE_COST", pa.float64()),
        pa.field("PAYER_COVERAGE", pa.float64()),
        pa.field("DISPENSES", pa.int64()),
        pa.field("TOTALCOST", pa.float64()),
        pa.field("REASONCODE", pa.string()),
        pa.field("REASONDESCRIPTION", pa.string()),
    ]),
}


def delta_table_exists(table_path: str) -> bool:
    delta_log = Path(table_path) / "_delta_log"
    return delta_log.exists()


def convert_csv_to_delta(entity_name: str, csv_path: str, delta_path: str) -> None:
    logger.info(f"Converting {entity_name}...")

    convert_options = pa_csv.ConvertOptions(
        null_values=['', 'NULL', 'null'],
        true_values=['true', 'True', 'TRUE'],
        false_values=['false', 'False', 'FALSE'],
    )

    table = pa_csv.read_csv(
        csv_path,
        convert_options=convert_options,
    )

    if entity_name in SCHEMAS:
        schema = SCHEMAS[entity_name]
        for field in schema:
            if field.name in table.schema.names:
                col_index = table.schema.get_field_index(field.name)
                if table.schema.field(field.name).type != field.type:
                    try:
                        cast_array = table.column(col_index).cast(field.type, safe=False)
                        table = table.set_column(col_index, field, cast_array)
                    except Exception:
                        pass

    row_count = len(table)

    write_deltalake(
        delta_path,
        table,
        mode='overwrite',
        schema_mode='overwrite',
    )

    logger.info(f"  {entity_name}: {row_count:,} rows -> {delta_path}")


def main():
    os.makedirs(PARQUET_DIR, exist_ok=True)

    entities = list(SCHEMAS.keys())
    skipped = []
    converted = []

    for entity in entities:
        csv_path = os.path.join(RAW_DIR, f"{entity}.csv")
        delta_path = os.path.join(PARQUET_DIR, entity)

        if not os.path.exists(csv_path):
            logger.warning(f"CSV not found for {entity}: {csv_path}")
            continue

        if delta_table_exists(delta_path):
            logger.info(f"Delta table already exists for {entity}, skipping.")
            skipped.append(entity)
            continue

        convert_csv_to_delta(entity, csv_path, delta_path)
        converted.append(entity)

    logger.info(f"\nPhase 1A complete.")
    logger.info(f"  Converted: {converted}")
    logger.info(f"  Skipped (already exist): {skipped}")

    logger.info("\nVerifying Delta tables...")
    for entity in entities:
        delta_path = os.path.join(PARQUET_DIR, entity)
        if delta_table_exists(delta_path):
            dt = DeltaTable(delta_path)
            count = dt.to_pyarrow_table().num_rows
            logger.info(f"  {entity}: {count:,} rows verified")


if __name__ == "__main__":
    main()