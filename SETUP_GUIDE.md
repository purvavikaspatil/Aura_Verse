# Step-by-Step Setup Guide

Follow these steps in order to get your Dynamic ETL application running.

## Prerequisites Check

✅ Python 3.8+ installed (you have Python 3.14.0 - perfect!)
✅ Project folder: `C:\Users\purva\OneDrive\Desktop\dynamic_etl-main`

---

## Step 1: Create MongoDB Configuration File

The application needs a `.env` file with your MongoDB connection string.

1. **Create a file named `.env`** in the project root folder (same folder as `api.py`)

2. **Add this content to `.env`**:

```env
MONGO_URI=mongodb://localhost:27017/
DB_NAME=dynamic_etl
```

**OR if you're using MongoDB Atlas (cloud):**

```env
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
DB_NAME=dynamic_etl
```

**Note:** Replace `username` and `password` with your actual MongoDB Atlas credentials.

---

## Step 2: Install Python Dependencies

Open PowerShell or Command Prompt in the project folder and run:

```powershell
pip install pandas genson pymongo requests fastapi uvicorn python-dotenv python-multipart
```

**Note:** We're skipping `streamlit` and `schedule` for now as they're optional. The main application will work without them.

**Expected output:** You should see packages being installed successfully.

---

## Step 3: Start the Backend Server

Keep your terminal open and run:

```powershell
python start_server.py
```

**OR directly:**

```powershell
uvicorn api:app --reload
```

**What you should see:**
```
Starting Dynamic ETL Backend Server
Server will be available at: http://localhost:8000
```

**✅ Keep this terminal window open!** The server must stay running.

---

## Step 4: Verify Backend is Running

Open your web browser and go to:

**http://localhost:8000**

You should see:
```json
{"message": "Dynamic ETL Backend is Running 🚀"}
```

**Also try:** http://localhost:8000/docs - This shows the API documentation.

If you see these, your backend is working! ✅

---

## Step 5: Start the Frontend Server

**Open a NEW terminal window** (keep the backend running in the first one).

Navigate to the project folder and run:

```powershell
python -m http.server 8080
```

**What you should see:**
```
Serving HTTP on 0.0.0.0 port 8080 (http://0.0.0.0:8080/) ...
```

**✅ Keep this terminal window open too!**

---

## Step 6: Open the Frontend Application

Open your web browser and go to:

**http://localhost:8080/index.html**

You should see the login page of the Dynamic ETL application.

---

## Step 7: Test the Application

1. **Create an account** or login (the app uses localStorage, so any email/password works)
2. **Upload a file** (JSON or text file)
3. **Click "Transform Data"** to process it
4. **View the results** in the output section

---

## Troubleshooting

### Problem: "MONGO_URI environment variable is not set"

**Solution:** Make sure you created the `.env` file in the project root with the correct content (see Step 1).

### Problem: "Cannot connect to backend server"

**Solution:** 
- Make sure Step 3 is completed and the backend server is running
- Check that you can access http://localhost:8000 in your browser
- Make sure no firewall is blocking port 8000

### Problem: CORS errors in browser console

**Solution:**
- Make sure you're opening the frontend via `http://localhost:8080/index.html`
- **NOT** by double-clicking the `index.html` file (that uses `file://` which causes CORS issues)

### Problem: Port 8000 already in use

**Solution:** 
- Close whatever is using port 8000, OR
- Change the port in `start_server.py` to 8001, and update `API_BASE_URL` in `index.html` (line 808) to `'http://localhost:8001'`

### Problem: Port 8080 already in use

**Solution:**
- Use a different port: `python -m http.server 8081`
- Then open: `http://localhost:8081/index.html`

---

## Quick Reference

**Backend URL:** http://localhost:8000  
**Frontend URL:** http://localhost:8080/index.html  
**API Docs:** http://localhost:8000/docs

**To stop servers:** Press `Ctrl+C` in each terminal window

---

## Next Steps After Setup

Once everything is working:
1. Try uploading different file types (JSON, TXT, CSV)
2. Test the Transform and Organize features
3. Check the output and download processed data
4. View file history using the History button

Good luck! 🚀

