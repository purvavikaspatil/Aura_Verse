import pandas as pd
import os
import numpy as np
import json

def transform_data(data, schema_version):
    """
    Transform nested JSON into clean tabular form.
    """
    # Convert nested JSON to DataFrame
    results = data.get("results", [])
    
    if not results:
        return []
    
    df = pd.json_normalize(results)

    # Add schema version column
    df["schema_version"] = schema_version

    # Standardize column names (remove dots and make lowercase)
    df.columns = [col.replace('.', '_').lower() for col in df.columns]

    # Replace NaN, Infinity, and -Infinity with None (which becomes null in JSON)
    df = df.replace([np.nan, np.inf, -np.inf], None)

    # Create cleaned folder if not exists
    os.makedirs("data/cleaned", exist_ok=True)

    # Save cleaned CSV
    filepath = f"data/cleaned/cleaned_v{schema_version}.csv"
    df.to_csv(filepath, index=False)

    print(f"Cleaned data saved: cleaned_v{schema_version}.csv")

    # Convert to dict and handle NaN/Inf values for JSON serialization
    records = df.to_dict(orient="records")
    
    # Clean up any remaining NaN/Inf values that might have been missed
    def clean_value(val):
        """Clean value to be JSON-compliant"""
        if val is None:
            return None
        if pd.isna(val):
            return None
        if isinstance(val, (float, np.floating)):
            if np.isinf(val) or np.isnan(val):
                return None
        # Convert numpy types to Python native types
        if isinstance(val, (np.integer, np.int64, np.int32)):
            return int(val)
        if isinstance(val, (np.floating, np.float64, np.float32)):
            if np.isnan(val) or np.isinf(val):
                return None
            return float(val)
        if isinstance(val, np.bool_):
            return bool(val)
        # Convert other numpy types to string
        if isinstance(val, np.generic):
            return str(val)
        return val
    
    # Recursively clean all values in records
    cleaned_records = []
    for record in records:
        cleaned_record = {}
        for key, value in record.items():
            # Ensure key is a string
            key_str = str(key) if not isinstance(key, str) else key
            cleaned_record[key_str] = clean_value(value)
        cleaned_records.append(cleaned_record)

    return cleaned_records
