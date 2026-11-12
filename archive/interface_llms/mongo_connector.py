from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
# MongoDB Setup
# Connect to MongoDB (replace the connection string with your MongoDB credentials)
client = MongoClient(os.getenv("MONGO_URI"))  # Local MongoDB connection
db = client[os.getenv("DB")]
collection = db[os.getenv("COLLECTION")]


def get_occupancy_by_criteria(criteria):
    """
    Query the occupancy collection based on various criteria.
    
    Parameters:
    criteria (dict): A dictionary containing the query criteria.
    
    Returns:
    list: A list of records matching the criteria.
    """
    if 'time' in criteria:
        criteria['time'] = criteria['time'].strftime("%Y-%m-%dT%H:%M:%S")
    
    records = collection.find(criteria)
    return list(records)