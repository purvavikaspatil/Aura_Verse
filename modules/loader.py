from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from config.settings import MONGO_URI, DB_NAME

# Lazy MongoDB connection - only connect when needed
_client = None
_db = None

def get_db():
    """Get MongoDB database connection (lazy initialization)"""
    global _client, _db
    if _db is None:
        try:
            _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            # Test the connection
            _client.admin.command('ping')
            _db = _client[DB_NAME]
            print(f"Successfully connected to MongoDB: {DB_NAME}")
        except (ConnectionFailure, OperationFailure) as e:
            print(f"MongoDB connection error: {e}")
            print(f"MONGO_URI: {MONGO_URI[:20]}...")  # Print partial URI for debugging
            raise
        except Exception as e:
            print(f"Unexpected MongoDB error: {e}")
            raise
    return _db

# For backward compatibility - create a simple module-level db object
class DBProxy:
    def __getattr__(self, name):
        return getattr(get_db(), name)

db = DBProxy()

def get_all_records():
    """
    Fetch all records from MongoDB without _id field.
    """
    db = get_db()
    return list(db.records.find({}, {"_id": 0}))


def get_all_schemas():
    """
    Fetch all schema documents from MongoDB without _id field.
    """
    db = get_db()
    return list(db.schemas.find({}, {"_id": 0}))


def insert_cleaned_data(records):
    """
    Insert transformed records into MongoDB.
    """
    if not records:
        print("No records to insert into MongoDB.")
        return

    db = get_db()
    db.records.insert_many(records)
    print(f"Inserted {len(records)} cleaned records into MongoDB!")

def insert_schema(schema, version):
    """
    Save schema versions to MongoDB.
    """
    db = get_db()
    doc = {
        "version": version,
        "schema": schema
    }
    db.schemas.insert_one(doc)
    print(f"Inserted schema version v{version} into MongoDB!")
