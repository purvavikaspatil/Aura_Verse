import os
import sys

# Make sure the project root (dynamic_etl) is on Python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)


import streamlit as st
import pandas as pd
from pymongo import MongoClient

from config.settings import MONGO_URI, DB_NAME

# ---------------------------
# Helper functions
# ---------------------------

def get_db():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

def get_records(db):
    # Get all records, but hide MongoDB _id field
    docs = list(db.records.find({}, {"_id": 0}))
    return docs

def get_schemas(db):
    docs = list(db.schemas.find({}, {"_id": 0}))
    # Sort by version number (1, 2, 3, ...)
    docs = sorted(docs, key=lambda d: d.get("version", 0))
    return docs

def get_field_names_from_schema(schema: dict):
    """
    Extract top-level field names of a single user record
    from a schema built over the 'results' array.
    """
    items = schema.get("items", {})
    properties = items.get("properties", {})
    return set(properties.keys())

def compare_two_schemas(schema_old: dict, schema_new: dict):
    old_fields = get_field_names_from_schema(schema_old)
    new_fields = get_field_names_from_schema(schema_new)

    added = new_fields - old_fields
    removed = old_fields - new_fields
    return added, removed

# ---------------------------
# Streamlit UI
# ---------------------------

def main():
    st.title("🔍 Dynamic ETL – Schema Evolution Dashboard")
    st.caption("Team Code 466 – Dynamic ETL Pipeline for Unstructured Data")

    db = get_db()

    # Load data
    records = get_records(db)
    schemas = get_schemas(db)

    if not records:
        st.warning("No records found in MongoDB. Run main.py first to load data.")
        return

    # Convert records to DataFrame
    df_records = pd.DataFrame(records)

    # -----------------------
    # Top metrics
    # -----------------------
    st.subheader("📊 Pipeline Summary")

    total_records = len(df_records)
    versions = df_records["schema_version"].unique().tolist() if "schema_version" in df_records.columns else []
    num_versions = len(versions)

    col1, col2 = st.columns(2)
    col1.metric("Total Records Ingested", total_records)
    col2.metric("Schema Versions Detected", num_versions)

    # -----------------------
    # Records preview
    # -----------------------
    st.subheader("📄 Sample Records")
    st.write("Showing first 10 records from MongoDB:")
    st.dataframe(df_records.head(10))

    # -----------------------
    # Schema versions overview
    # -----------------------
    st.subheader("🧱 Schema Versions")

    schema_rows = []
    for doc in schemas:
        version = doc.get("version")
        schema = doc.get("schema", {})
        fields = get_field_names_from_schema(schema)
        schema_rows.append({
            "version": version,
            "num_fields": len(fields),
            "fields": ", ".join(sorted(fields))
        })

    df_schemas = pd.DataFrame(schema_rows)
    st.write("Overview of schema versions stored in MongoDB:")
    st.dataframe(df_schemas)

    # Expanders for each schema JSON
    for doc in schemas:
        version = doc.get("version")
        with st.expander(f"View raw JSON schema for version v{version}"):
            st.json(doc.get("schema", {}))

    # -----------------------
    # Schema evolution comparison (v1 vs v2, v2 vs v3, ...)
    # -----------------------
    st.subheader("🔁 Schema Evolution (Differences Between Versions)")

    if len(schemas) < 2:
        st.info("Need at least two schema versions to show evolution. Run the pipeline for another version.")
    else:
        evolution_rows = []
        for i in range(len(schemas) - 1):
            v_old = schemas[i]["version"]
            v_new = schemas[i + 1]["version"]
            added, removed = compare_two_schemas(schemas[i]["schema"], schemas[i + 1]["schema"])

            evolution_rows.append({
                "from_version": v_old,
                "to_version": v_new,
                "added_fields": ", ".join(sorted(added)) if added else "-",
                "removed_fields": ", ".join(sorted(removed)) if removed else "-"
            })

        df_evolution = pd.DataFrame(evolution_rows)
        st.write("Field-level differences between consecutive schema versions:")
        st.dataframe(df_evolution)

    st.markdown("---")
    st.caption("This dashboard is powered by Streamlit + MongoDB Atlas + Python ETL.")


if __name__ == "__main__":
    main()
