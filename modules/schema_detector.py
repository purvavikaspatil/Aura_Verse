import json
import os
from genson import SchemaBuilder

SCHEMA_DIR = "schemas"

def generate_schema(data):
    """
    Automatically generate a JSON schema from the list of user records.
    We focus on the 'results' array which contains user objects.
    """
    records = data.get("results", [])
    builder = SchemaBuilder()
    builder.add_object(records)
    schema = builder.to_schema()
    return schema

def save_schema(schema, version):
    """
    Save the generated schema with versioning.
    """
    os.makedirs(SCHEMA_DIR, exist_ok=True)
    filepath = os.path.join(SCHEMA_DIR, f"schema_v{version}.json")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)

    print(f"Schema saved: schema_v{version}.json")

def load_schema(version):
    filepath = os.path.join(SCHEMA_DIR, f"schema_v{version}.json")
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def _get_field_names(schema):
    """
    Helper: get all top-level field names for a single user record
    from the schema generated over the 'results' array.
    """
    # schema for array: { "type": "array", "items": { "type": "object", "properties": {...} } }
    items = schema.get("items", {})
    properties = items.get("properties", {})
    return set(properties.keys())

def compare_schemas(schema_old, schema_new):
    """
    Compare two schemas and return sets of added and removed fields.
    """
    old_fields = _get_field_names(schema_old)
    new_fields = _get_field_names(schema_new)

    added = new_fields - old_fields
    removed = old_fields - new_fields
    return added, removed
