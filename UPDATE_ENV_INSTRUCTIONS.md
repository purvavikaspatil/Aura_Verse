# How to Update .env File for MongoDB Atlas

## Step 1: Get Your MongoDB Atlas Connection String

1. Go to: https://cloud.mongodb.com/v2/6918195a1435227765a57723#/clusters
2. Click **"Connect"** button on your cluster
3. Select **"Connect your application"**
4. Choose **"Python"** and version **"3.6 or later"**
5. Copy the connection string (it looks like):
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/
   ```

## Step 2: Update the .env File

1. Open the `.env` file in the project root folder:
   `C:\Users\purva\OneDrive\Desktop\dynamic_etl-main\.env`

2. Replace the content with:
   ```env
   MONGO_URI=mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/
   DB_NAME=dynamic_etl
   ```

3. Replace:
   - `YOUR_USERNAME` with your MongoDB Atlas database username
   - `YOUR_PASSWORD` with your MongoDB Atlas database password
   - `cluster0.xxxxx.mongodb.net` with your actual cluster address from the connection string

## Example:

If your connection string is:
```
mongodb+srv://myuser:mypassword123@cluster0.abc123.mongodb.net/
```

Then your `.env` file should be:
```env
MONGO_URI=mongodb+srv://myuser:mypassword123@cluster0.abc123.mongodb.net/
DB_NAME=dynamic_etl
```

## Important Notes:

- Make sure there are **no spaces** around the `=` sign
- The password might contain special characters - keep them as they are
- Don't include the database name in the MONGO_URI (we specify it separately as DB_NAME)
- Make sure your MongoDB Atlas IP whitelist allows connections (add `0.0.0.0/0` for all IPs, or your specific IP)

## Test the Connection:

After updating, try starting the backend:
```powershell
python start_server.py
```

If it connects successfully, you'll see the server start without errors!

