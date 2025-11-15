import os
from dotenv import load_dotenv

# Find the .env file in the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, ".env")

if os.path.exists(env_path):
    load_dotenv(env_path)

# Environment variables
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "dynamic_etl")

if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is not set. Please create a .env file in the project root.")
