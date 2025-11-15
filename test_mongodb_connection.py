"""
Test MongoDB Connection
Run this to verify your MongoDB credentials are correct
"""
from config.settings import MONGO_URI, DB_NAME
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from urllib.parse import unquote

print("=" * 60)
print("Testing MongoDB Connection")
print("=" * 60)
print(f"Database: {DB_NAME}")
print(f"Connection String (partial): {MONGO_URI[:30]}...")
print()

try:
    # Create client with timeout
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
    
    # Test connection
    print("Attempting to connect...")
    client.admin.command('ping')
    print("✅ Connection successful!")
    
    # List databases
    print("\nAvailable databases:")
    for db_name in client.list_database_names():
        print(f"  - {db_name}")
    
    # Test database access
    db = client[DB_NAME]
    print(f"\n✅ Database '{DB_NAME}' is accessible")
    
    # List collections
    collections = db.list_collection_names()
    print(f"\nCollections in '{DB_NAME}':")
    if collections:
        for col in collections:
            count = db[col].count_documents({})
            print(f"  - {col}: {count} documents")
    else:
        print("  (no collections yet)")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed! MongoDB connection is working.")
    print("=" * 60)
    
except OperationFailure as e:
    if "authentication" in str(e).lower() or "bad auth" in str(e).lower():
        print("❌ Authentication failed!")
        print(f"Error: {e}")
        print("\nPossible issues:")
        print("1. Incorrect username or password")
        print("2. Password needs URL encoding (special characters)")
        print("3. Database user doesn't have proper permissions")
        print("\nTo fix:")
        print("1. Check your MongoDB Atlas Database Access")
        print("2. Verify the password in your .env file")
        print("3. Make sure special characters are URL-encoded")
    else:
        print(f"❌ Operation failed: {e}")
    
except ConnectionFailure as e:
    print("❌ Connection failed!")
    print(f"Error: {e}")
    print("\nPossible issues:")
    print("1. IP address not whitelisted in MongoDB Atlas")
    print("2. Network connectivity issues")
    print("3. Incorrect connection string")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()

