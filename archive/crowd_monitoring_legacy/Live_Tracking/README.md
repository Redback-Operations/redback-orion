## Folder Structure

Live_Tracking
|--Assemble
|--BackendUpdate
|--Live_Tracking

1. Modules_Dev is the program with real-time monitoring, MongoDB, and 2D visualisation features.
2. Backend_v2 is the system to run the program for web-interface.
3. Live_tracking is for testing the live-tracking with RTSP and MongoDB data importing.

## MongoDB

### Introduction

MongoDB is is a NoSQL database management platform, which is utilised in this project for storing the crowd monitoring data. As the current aim of the project is to concentrate on tracking the crowd and extracting the collected data to analyse the movement trend, MongoDB would be an acceptable option. The NoSQL database platform is chosen because of its schemaless and non-relational properties. When the project gets more complicated with more components, a standard SQL database should be considered.

### Installation

For establishing a database on MongoDB, the database and clusters can be easliy created by following the instruction on the MongoDB website. In regard to the cluster configuration, the team would stick to the free-tier with 512 MB storage.
To connect to MongoDB, it is imporatnt to choose the current driver and version to get appropriate instruction in the below image.
Following the below command line to install MongoDB driver to the local machine
![MongoDB](MongoDBConnect.png)

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

With the above code, by setting up a variable for interval time, we can easily adjust this variable to update the recorded data on MongoDB in every second, minute or hour. This approach will put less stress on the data storage section, but lack of detail.

## Live-Tracking Method

### Introduction

Currently there are three different methods of real-time crowd monitoring including using the computer bulit in web-cam, the external camera, and the IP camera. This project would solely focus on the Real-Time Streaming Protocol of an IP camera and utilising OpenCV to process the recording frame.

During testing the program, we had used built-in camera or external devices with cameras for convenience. Those two could be utilised by assigning "0" and "1" in the video capture statement. 0 is for the bulit-in camera whilst 1 is for connected devices (mobile camera - Camo App).

```
cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture(1)
```
### Camo App setup
Download Camo app through App Store/Google Play for your computer and the mobile device. After installed, open the app and pair your mobile device with your computer.
    ![CamoApp](Camo.png)

### Retrieving RTSP

There are two ways of retrieving the livestream protocol:

1. The simpliest one is using iSpy application. The advantage of this method is providing a full form RTSP, whiles merely be available on Window system is its cirtical drawbacks to condiser. In regard to see the RTSP, first filling out the authentication and choose the network.
   ![iSpy](iSpy.png)

2. The second method is to use the network anaylsing application, WireShark. The application is widely aviable on different operating systems. By accessing to the current network that the machine is connecting to and filter the protocol, we can retrieve these networking components including IP address, port, stream, and channel.With those pieces of data, we can form a complete RTSP:

```
rtsp://<User_name>:<Password>@<ip_address>:<port>/Streaming/Channels
```

![WireShark](WireShark.png)

### Using OpenCV to load the camera frame with RTSP

The following code is the example of how to load the camera frame using OpenCV:

- Using VideoCapture to read the RTSP
- Using Loop accompanying imshow to open the frame
- Closing all opened winows when finishing the program

```
import cv2

rtsp_url = 'Fill in your RTSP'
cap = cv2.VideoCapture(rtsp_url)

while True:
    ret, frame = cap.read()
        if not ret:
            print('Error reading the frame')
            break

    cv2.imshow('Crowd Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### Important Notice

1. It is remarkable that these two methods will require the useername and password from the camera. Furthermore, the camera would always run on port 554 and 2.5 GHz band.
2. Both iSpy and WireShark RTSP retrieving methods solely work, when the computer used to search them connect to a 2.5GHz network.
3. There should be less than two devices or programs using the same RTSP. For three to four entities, two different RTSP can be used with two devices connecting to the 480p protocol and the other two connecting the the 720p option.
