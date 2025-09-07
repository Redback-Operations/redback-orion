from pymongo import MongoClient
import time
from datetime import datetime


class Database:
    def __init__(self):
        # Initialize the MongoDB client and database
        self.client = MongoClient("")
        self.db = self.client["CrowdTracking"]
        self.collection = self.db["Crowd"]
        self.lastRecorded = time.time()  # Initialize with current timestamp

    def insertRecord(self, count, frameId):
        currentTime = datetime.now()  # Use datetime object for formatting
        currentTimestamp = time.time()  # Get current timestamp

        # Only record data every second
        if currentTimestamp - self.lastRecorded >= 1:  # Use timestamps for comparison
            record = {
                "frameId": frameId,
                "peopleCount": count,
                "timestamp": currentTime.strftime(
                    "%d-%m-%Y %H:%M:%S"
                ),  # Format datetime object
            }
            try:
                self.collection.insert_one(record)
                print(
                    f"Recorded: Frame {frameId}, Time {currentTime.strftime('%d-%m-%Y %H:%M:%S')}, People {count}"
                )
            except Exception as e:
                print(f"Failed to insert record into database: {e}")
            self.lastRecorded = currentTimestamp  # Update the last recorded timestamp

    def getlastestRecord(self):
        latestRecord = self.collection.find_one(sort=[("timestamp", -1)])
        return latestRecord["peopleCount"] if latestRecord else 0

    def close(self):
        self.client.close()
