@echo off
echo ============================================================
echo Starting Backend Server
echo ============================================================
echo.
echo Server will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

cd /d "%~dp0"
python start_server.py

pause

