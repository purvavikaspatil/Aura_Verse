from fastapi import FastAPI, Query, UploadFile, File, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from modules.extractor import fetch_data_from_api, save_raw_data
from modules.schema_detector import generate_schema, save_schema
from modules.transformer import transform_data
from modules.loader import (
    insert_cleaned_data,
    insert_schema,
    get_all_records,
    get_all_schemas,
    get_db
)
from modules.content_parser import parse_file_content
from modules.content_formatter import format_content

import datetime
import json
import os
import tempfile
from bson import ObjectId
from typing import Any

# Helper function to convert ObjectId to string for JSON serialization
def convert_objectid_to_str(obj: Any) -> Any:
    """
    Recursively convert MongoDB ObjectId objects to strings for JSON serialization.
    """
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {key: convert_objectid_to_str(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid_to_str(item) for item in obj]
    else:
        return obj

# Initialize API App
app = FastAPI(
    title="Dynamic ETL Backend API",
    description="Dynamic ETL Pipeline with Schema Evolution for Unstructured Data",
    version="2.0"
)

# Enable CORS for Frontend Integration
# Note: When using allow_origins=["*"], allow_credentials must be False
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Must be False when using "*"
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],
)


# Home Route (Health Check)
@app.get("/")
def home():
    return JSONResponse(
        content={"message": "Dynamic ETL Backend is Running 🚀"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )


# Test endpoint to verify file upload works
@app.post("/test-upload")
async def test_upload(file: UploadFile = File(...)):
    """Test endpoint to verify file upload is working"""
    try:
        content = await file.read()
        file_content = content.decode('utf-8')
        return JSONResponse(
            content={
                "status": "success",
                "filename": file.filename,
                "size": len(content),
                "content_preview": file_content[:200]
            },
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "error": str(e)},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )

# Test CORS endpoint
@app.get("/test-cors")
async def test_cors():
    """Test endpoint to verify CORS is working"""
    return JSONResponse(
        content={"message": "CORS is working!", "origin": "allowed"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )


# Run full ETL pipeline remotely
@app.post("/run-etl")
def run_etl(results: int = 10):
    # Extract
    data = fetch_data_from_api(results)
    save_raw_data(data)

    # Detect Schema Version
    schemas = get_all_schemas()
    version = len(schemas) + 1 if schemas else 1

    # Generate Schema
    schema = generate_schema(data)
    save_schema(schema, version)
    insert_schema(schema, version)

    # Transform
    cleaned_data = transform_data(data, version)
    insert_cleaned_data(cleaned_data)

    response = {
        "status": "success",
        "records_inserted": len(cleaned_data),
        "schema_version": version,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
    # Convert any ObjectIds to strings for JSON serialization
    return convert_objectid_to_str(response)


# Fetch Records With Pagination
@app.get("/records")
def records(page: int = Query(1, ge=1), limit: int = Query(10, ge=1)):
    skip = (page - 1) * limit
    db = get_db()
    data = list(db.records.find({}, {"_id": 0}).skip(skip).limit(limit))
    response = {
        "page": page,
        "limit": limit,
        "count": len(data),
        "records": data
    }
    # Convert any ObjectIds to strings for JSON serialization (safety check)
    return convert_objectid_to_str(response)


# Filter by Schema Version
@app.get("/records/by-version/{version}")
def records_by_version(version: int):
    db = get_db()
    data = list(db.records.find({"schema_version": version}, {"_id": 0}))
    response = {
        "schema_version": version,
        "count": len(data),
        "records": data
    }
    # Convert any ObjectIds to strings for JSON serialization (safety check)
    return convert_objectid_to_str(response)


# Fetch All Schema Versions
@app.get("/schemas")
def schemas():
    all_schemas = get_all_schemas()
    response = {"schemas": all_schemas}
    # Convert any ObjectIds to strings for JSON serialization (safety check)
    return convert_objectid_to_str(response)


# File Upload Endpoint
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file for processing.
    Supports: .txt, .pdf, .md, .json, .html, .csv, .xml, .js, .css, .log
    Returns the parsed data structure.
    """
    try:
        # Read file content
        content = await file.read()
        
        # Try to decode as UTF-8, fallback to latin-1 for binary files
        try:
            file_content = content.decode('utf-8')
        except UnicodeDecodeError:
            # For PDF or binary files, we'll handle differently
            if file.filename and file.filename.lower().endswith('.pdf'):
                return {
                    "status": "info",
                    "message": "PDF file detected. PDF parsing requires additional libraries (PyPDF2 or pdfplumber). Please install: pip install PyPDF2",
                    "filename": file.filename,
                    "file_size": len(content),
                    "data_structure": {
                        "type": "pdf",
                        "note": "PDF parsing not yet implemented"
                    }
                }
            file_content = content.decode('latin-1', errors='ignore')
        
        # Use content parser to extract structured data
        normalized_data = parse_file_content(file_content, file.filename or "")
        
        # Save raw data
        save_raw_data(normalized_data)
        
        # Determine file type
        file_type = "unknown"
        if file.filename:
            ext = file.filename.lower().split('.')[-1]
            if ext in ['html', 'htm']:
                file_type = "html"
            elif ext in ['md', 'markdown']:
                file_type = "markdown"
            elif ext == 'csv':
                file_type = "csv"
            elif ext == 'json':
                file_type = "json"
            elif ext == 'txt':
                file_type = "text"
            elif ext == 'pdf':
                file_type = "pdf"
        
        response = {
            "status": "success",
            "message": f"File uploaded and parsed successfully ({file_type})",
            "filename": file.filename,
            "file_size": len(content),
            "data_structure": {
                "type": file_type,
                "records_count": len(normalized_data.get("results", [])),
                "extracted_types": list(set([r.get("type", "unknown") for r in normalized_data.get("results", [])]))
            },
            "preview": normalized_data.get("results", [])[:5] if len(normalized_data.get("results", [])) > 0 else []
        }
        # Convert any ObjectIds to strings for JSON serialization (safety check)
        return convert_objectid_to_str(response)
    except Exception as e:
        import traceback
        print(f"Upload error: {traceback.format_exc()}")
        return JSONResponse(
            status_code=400,
            content={"detail": f"Error processing file: {str(e)}"},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )


# Transform Data Endpoint
@app.post("/transform")
async def transform_uploaded_data(file: UploadFile = File(...)):
    """
    Transform and format uploaded file content.
    Fixes broken structure, corrects indentation, and formats the file.
    Returns ONLY the formatted file content (raw text, not JSON).
    Preserves original file type and extension.
    """
    try:
        # Read file content
        content = await file.read()
        
        # Try to decode as UTF-8
        try:
            file_content = content.decode('utf-8')
        except UnicodeDecodeError:
            # For binary files, return error
            if file.filename and file.filename.lower().endswith('.pdf'):
                return Response(
                    status_code=400,
                    content="PDF files cannot be formatted. Please use a text-based format.",
                    media_type="text/plain",
                    headers={
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                        "Access-Control-Allow-Headers": "*",
                    }
                )
            # Try latin-1 as fallback
            file_content = content.decode('latin-1', errors='ignore')
        
        # Format and fix the file content
        from modules.content_formatter import format_content
        
        try:
            formatted_content = format_content(file_content, file.filename or "")
        except Exception as format_error:
            import traceback
            print(f"Format error: {traceback.format_exc()}")
            # If formatting fails, return original content
            formatted_content = file_content
        
        # Determine MIME type based on file extension
        mime_type = "text/plain"
        if file.filename:
            ext = file.filename.lower().split('.')[-1]
            mime_map = {
                'html': 'text/html',
                'htm': 'text/html',
                'json': 'application/json',
                'xml': 'application/xml',
                'csv': 'text/csv',
                'md': 'text/markdown',
                'markdown': 'text/markdown',
                'txt': 'text/plain',
                'text': 'text/plain',
                'js': 'application/javascript',
                'css': 'text/css',
                'log': 'text/plain'
            }
            mime_type = mime_map.get(ext, 'text/plain')
        
        # Return ONLY the formatted content (raw text, not JSON)
        return Response(
            content=formatted_content,
            media_type=mime_type,
            headers={
                "Content-Disposition": f'inline; filename="{file.filename or "transformed.txt"}"',
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )
    except HTTPException as e:
        # Return HTTPException as text
        return Response(
            status_code=e.status_code,
            content=e.detail,
            media_type="text/plain",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Transform error: {error_details}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        
        # Return error as text
        error_msg = f"Error transforming data: {str(e)}"
        
        # Return error as text response with CORS headers
        return Response(
            status_code=500,
            content=error_msg,
            media_type="text/plain",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )


# Organize Data Endpoint
@app.post("/organize")
async def organize_data(file: UploadFile = File(...)):
    """
    Organize uploaded data by cleaning and formatting content.
    Preserves original format - returns raw formatted content (not JSON).
    - HTML: Proper indentation and spacing
    - JSON: Pretty-printed with indentation
    - Markdown: Consistent spacing
    - XML: Proper indentation
    - CSV: Consistent formatting
    - Text: Clean spacing and indentation
    """
    try:
        # Read file content
        content = await file.read()
        
        # Try to decode as UTF-8
        try:
            file_content = content.decode('utf-8')
        except UnicodeDecodeError:
            # For binary files, return as-is
            if file.filename and file.filename.lower().endswith('.pdf'):
                return JSONResponse(
                    status_code=400,
                    content={"detail": "PDF files cannot be formatted. Please use a text-based format."},
                    headers={
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                        "Access-Control-Allow-Headers": "*",
                    }
                )
            # Try latin-1 as fallback
            file_content = content.decode('latin-1', errors='ignore')
        
        # Format the content while preserving original format
        formatted_content = format_content(file_content, file.filename or "")
        
        # Return raw formatted content (not wrapped in JSON)
        # Use Response with media_type to return raw text
        from fastapi import Response
        return Response(
            content=formatted_content,
            media_type="text/plain",
            headers={
                "Content-Disposition": f'inline; filename="{file.filename or "organized.txt"}"',
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )
        
    except HTTPException as e:
        # Return HTTPException with CORS headers
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": e.detail},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Organize error: {error_details}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error organizing data: {str(e)}"},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )
