## MongoDB

### Introduction

MongoDB is is a NoSQL database management platform, which is utilised in this project for storing the crowd monitoring data. As the current aim of the project is to concentrate on tracking the crowd and extracting the collected data to analyse the movement trend, MongoDB would be an acceptable option. The NoSQL database platform is chosen because of its schemaless and non-relational properties. When the project gets more complicated with more components, a standard SQL database should be considered.

### Installation

For establishing a database on MongoDB, the database and clusters can be easliy created by following the instruction on the MongoDB website. In regard to the cluster configuration, the team would stick to the free-tier with 512 MB storage.
To connect to MongoDB, it is imporatnt to choose the current driver and version to get appropriate instruction in the below image.
Following the below command line to install MongoDB driver to the local machine
!(MongoDBConnect.png)

```
python -m pip install "pymongo[srv]"
```

### Data Recording
The below block has the function of connecting to the MongoDB driver.
It would directly access to the CrowdTracking database and Crowd collection

```
from pymongo import MongoClient

client = MongoClient('mongo+srv:// ')
db = client["CrowTracking"]
collection = db["Crowd"]
```
In regard to real-time crowd monitoring there would be two main approachs. 
```
now = datetime.now()
data = {            
    "frame_id": frame_id,
    "timestamp": now.strftime("%d/%m/%Y %H:%M:%S"),
    "total_persons": len(boxes)
}
collection.insert_one(data)
```
This code would record the captured data based on every round of loop. The advantage of this approach is that the data would be imported into MongoDB in every frame ID. However, as the recursion os executed hastely, YOLO could process mutiple of frames in a second leading to the burdern of storage.

```
if current_time - last_update_time < update_interval:
    now = datetime.now()
    data = {
        "frame_id": frame_id,
        "timestamp": now.strftime("%d/%m/%Y %H:%M:%S"),
        "total_persons": len(boxes)
    }
    collection.insert_one(data)
    last_update_time = current_time
```
With the above code, by setting up a variable for interval time, we can easily adjust this variable to update the recorded data on MongoDB in every second, minute or hour.

