# Dynamic ETL Pipeline

A Dynamic ETL (Extract, Transform, Load) Pipeline for processing unstructured data with intelligent schema detection and evolution.

## Features

- **File Upload**: Upload JSON or text files for processing
- **Data Transformation**: Automatic schema detection and data transformation
- **Data Organization**: Sort and organize data efficiently
- **Schema Evolution**: Track schema changes across different data versions
- **MongoDB Integration**: Store processed data and schemas

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure MongoDB

Make sure you have MongoDB configured. Update `config/settings.py` with your MongoDB connection string if needed.

### 3. Start the Backend Server

**Option A: Using the startup script (Recommended)**

On Windows:
```bash
start_server.bat
```

On Linux/Mac:
```bash
chmod +x start_server.sh
./start_server.sh
```

Or using Python directly:
```bash
python start_server.py
```

**Option B: Using uvicorn directly**

```bash
uvicorn api:app --reload
```

The backend will start on `http://localhost:8000`

### 4. Open the Frontend

**Important**: The frontend must be served via a web server, not opened directly as a file.

**Option A: Using Python's built-in server**

```bash
# Python 3
python -m http.server 8080

# Then open: http://localhost:8080/index.html
```

**Option B: Using Node.js http-server**

```bash
npx http-server -p 8080

# Then open: http://localhost:8080/index.html
```

**Option C: Using VS Code Live Server**

If you're using VS Code, install the "Live Server" extension and right-click on `index.html` → "Open with Live Server"

## Troubleshooting

### Backend Not Connecting

1. **Check if the backend is running**
   - Open `http://localhost:8000` in your browser
   - You should see: `{"message": "Dynamic ETL Backend is Running 🚀"}`
   - Or check `http://localhost:8000/docs` for API documentation

2. **Check the port**
   - Default port is 8000
   - If port 8000 is in use, change it in `start_server.py` or use:
     ```bash
     uvicorn api:app --reload --port 8001
     ```
   - Then update `API_BASE_URL` in `index.html` (line 808)

3. **Check firewall/antivirus**
   - Make sure nothing is blocking port 8000

4. **Check CORS**
   - CORS is already configured in `api.py` to allow all origins
   - If you still have issues, make sure the frontend is served via HTTP (not file://)

### Frontend Issues

1. **CORS Errors**
   - Make sure you're opening the frontend via a web server (http://localhost:8080/index.html)
   - NOT by double-clicking the file (file:///path/to/index.html)

2. **Connection Errors**
   - The frontend will automatically test the connection on load
   - If the backend is not running, you'll see a warning popup
   - Check the browser console (F12) for detailed error messages

3. **File Upload Not Working**
   - Make sure the backend server is running
   - Check browser console for errors
   - Verify the file format is supported (JSON, TXT, CSV, XML, HTML, JS, CSS, LOG)

## API Endpoints

- `GET /` - Health check
- `POST /upload` - Upload a file for processing
- `POST /transform` - Transform uploaded data (full ETL pipeline)
- `POST /organize` - Organize data (sort and structure)
- `GET /records` - Get all records with pagination
- `GET /records/by-version/{version}` - Get records by schema version
- `GET /schemas` - Get all schema versions

## Project Structure

```
dynamic_etl-main/
├── api.py                 # FastAPI backend server
├── index.html             # Frontend application
├── start_server.py        # Server startup script
├── requirements.txt       # Python dependencies
├── config/
│   └── settings.py       # Configuration (MongoDB, etc.)
├── modules/
│   ├── extractor.py      # Data extraction
│   ├── transformer.py    # Data transformation
│   ├── schema_detector.py # Schema detection
│   └── loader.py         # MongoDB operations
└── dashboard/
    └── dashboard.py      # Streamlit dashboard
```

## Usage

1. Start the backend server (see Setup Instructions)
2. Open the frontend in a browser (via web server)
3. Login or create an account
4. Upload a JSON or text file
5. Click "Transform Data" to run the ETL pipeline
6. Or click "Organize Data" to sort and organize
7. View results and download processed data

## Development

### Running the Dashboard

```bash
streamlit run dashboard/dashboard.py
```

### Testing the API

Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI)

## License

This project is part of Team Code 466 - Dynamic ETL Pipeline for Unstructured Data
