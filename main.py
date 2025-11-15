from copy import deepcopy

from modules.extractor import fetch_data_from_api, save_raw_data
from modules.schema_detector import (
    generate_schema,
    save_schema,
    load_schema,
    compare_schemas,
)
from modules.transformer import transform_data
from modules.loader import insert_cleaned_data, insert_schema


def simulate_schema_change(data):
    """
    Simulate a change in the website data structure:
    - Add a new field 'loyalty_score'
    - Remove the 'phone' field
    """
    modified = deepcopy(data)
    for user in modified.get("results", []):
        # Add new field
        user["loyalty_score"] = 100

        # Remove existing field (if present)
        user.pop("phone", None)

    return modified


def run_version(version: int, data):
    """
    Run full ETL for a specific schema version.
    """
    # Save raw
    save_raw_data(data)

    # Schema
    schema = generate_schema(data)
    save_schema(schema, version)
    insert_schema(schema, version)

    # Transform
    cleaned_data = transform_data(data, version)

    # Load into MongoDB
    insert_cleaned_data(cleaned_data)

    return schema


if __name__ == "__main__":
    print("=== Running Version 1 (Original Data) ===")
    # ----- Version 1: original data from API -----
    data_v1 = fetch_data_from_api(results=10)
    schema_v1 = run_version(version=1, data=data_v1)

    print("\n=== Running Version 2 (Simulated Schema Change) ===")
    # ----- Version 2: simulate website changing its fields -----
    data_v2 = fetch_data_from_api(results=10)
    data_v2_changed = simulate_schema_change(data_v2)
    schema_v2 = run_version(version=2, data=data_v2_changed)

    # ----- Compare schemas -----
    added, removed = compare_schemas(schema_v1, schema_v2)
    print("\nSchema evolution detected:")
    print("  ➕ Added fields :", added)
    print("  ➖ Removed fields:", removed)

    print("\nStep 6 (Schema Evolution) Completed Successfully!")
