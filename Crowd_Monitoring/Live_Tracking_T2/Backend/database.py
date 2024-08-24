from pymongo import MongoClient
import time

class Database:
    def __init__(self):
        self.client = MongoClient("")
        self.db = self.client["CrowdTracking"]
        self.collection = self.db["Crowd"]
        self.lastRecorded = 0

    def insertRecord(self, count, framdId):
        currentTime = time.time()

        if currentTime - self.lastRecorded >= 1:
            record = {
                "frameId": frameId,
                "peopleCount": count,
                "timestamp": currentTime.strftime("%d-%m-%Y %H:%M:%S")
            }
            self.collection.insert_one(record)
            self.lastRecorded = currentTime

    def getlastestRecord(self):
        latestRecord = self.collection.find_one(sort=[("timestamp", -1)])
        return latestRecord["peopleCount"] if latestRecord else 0
    
    def close(self):
        self.client.close()

