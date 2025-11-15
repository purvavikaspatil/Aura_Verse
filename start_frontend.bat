@echo off
echo ============================================================
echo Starting Frontend Server
echo ============================================================
echo.
echo Server will be available at: http://localhost:8080/index.html
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

cd /d "%~dp0"
python -m http.server 8080

pause

