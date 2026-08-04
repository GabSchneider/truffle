from pymongo import MongoClient, ASCENDING, DESCENDING
from app.config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
news_collection = db["news"]

def setup_indexes():
    news_collection.create_index([("ticker", ASCENDING)])
    news_collection.create_index([("setor", ASCENDING)])
    news_collection.create_index([("data", DESCENDING)])
    news_collection.create_index([("ticker", ASCENDING), ("data", DESCENDING)])
    news_collection.create_index([("link", ASCENDING)], unique=True)
