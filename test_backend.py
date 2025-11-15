"""
Quick test script to verify backend is working
"""
import requests
import json

# Test 1: Check if backend is running
print("Test 1: Checking if backend is running...")
try:
    response = requests.get("http://localhost:8000/")
    print(f"✓ Backend is running: {response.json()}")
except Exception as e:
    print(f"✗ Backend is not running: {e}")
    exit(1)

# Test 2: Check CORS headers
print("\nTest 2: Checking CORS headers...")
try:
    response = requests.options("http://localhost:8000/transform", headers={
        "Origin": "http://localhost:8081",
        "Access-Control-Request-Method": "POST"
    })
    cors_headers = {
        "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
        "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
    }
    print(f"✓ CORS headers: {cors_headers}")
except Exception as e:
    print(f"✗ CORS test failed: {e}")

# Test 3: Test transform endpoint with a simple HTML file
print("\nTest 3: Testing transform endpoint...")
html_content = """<!DOCTYPE html>
<html>
<head>
<title>Test</title>
</head>
<body>
<h1>Test Heading</h1>
<p>Test paragraph</p>
</body>
</html>"""

try:
    files = {"file": ("test.html", html_content, "text/html")}
    response = requests.post(
        "http://localhost:8000/transform",
        files=files,
        headers={"Origin": "http://localhost:8081"}
    )
    print(f"✓ Transform response status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Transform successful: {data.get('status')}")
        print(f"  Records processed: {data.get('records_processed', 0)}")
    else:
        print(f"✗ Transform failed: {response.text}")
except Exception as e:
    print(f"✗ Transform test failed: {e}")
    import traceback
    traceback.print_exc()

print("\nAll tests completed!")

