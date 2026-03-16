# Documentation for Warning Message Feature

## 1. Introduction
This feature enhances real-time crowd detection by providing warnings when specific conditions related to crowd movement or density are met. The warning message is integrated within the final code and is designed to ensure timely alerts in situations requiring immediate attention.

---

## 2. Purpose
The purpose of this feature is to alert the system operator when unusual or rapid movement occurs in the crowd, enabling them to take necessary actions to ensure safety and manage the situation effectively.

---

## 3. Implementation Details
The warning message is triggered based on predefined thresholds for crowd behavior, such as:
- Rapid crowd movement
- Sudden increase in the number of people detected in a short time

The code block responsible for generating the warning is embedded within the real-time detection loop.

---

## 4. User Interface
The warning message is displayed on the video feed in real-time. When the specified condition is met, a red alert box appears on the screen with the message:

### Warning: Rapid Movement in Crowd

The message is positioned near the detected individuals.

![Warning Message Example](./images/warning_message_example1.png)  
[Click here to watch the video](./videos/video1.mp4)

![Warning Message Example](./images/warning_message_example2.png)  
[Click here to watch the video](./videos/video1.mp4)

![Warning Message Example](./images/warning_message_example3.png)  
[Click here to watch the video](./videos/video3.mp4)

---