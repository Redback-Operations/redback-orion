# AFL Player Tracking and Crowd Monitoring

This project is a combined submodule of Redback Project 4  focused on using AI and computer vision to enhance **crowd safety monitoring** and **player tracking** during Australian Football League (AFL) matches.

---

## 🎯 Project Objectives

- 🏃‍♂️ **Track individual AFL players** in match footage using YOLOv11 and DeepSORT.
- 👥 **Estimate crowd density and movement** in stadium environments.
- 🎥 **Overlay visual analytics** (bounding boxes, heatmaps) on match videos.
- 📊 **Generate dashboards** with statistics and visualizations.
- 🧠 **Collaborate with sports analytics team** to align player events (e.g., tackles, kicks, marks) with visual data.

---

## 🖥️ Technologies Used

| Layer       | Tech Stack |
|-------------|------------|
| Frontend    | React, Vite, Tailwind CSS, Chart.js, Leaflet.js |
| Backend     | Python, FastAPI, OpenCV, Uvicorn, YOLOv11, DeepSORT |
| Models      | Ultralytics YOLOv11, OpenCV background subtraction |
| Others      | GitHub, VS Code, Google Colab, Jupyter |

---
## 🚀 How to Run the Project

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/redback-project4.git
cd redback-project4/Player_Tracking/afl_player_tracking_and_crowd_monitoring
```
### 2. Run the backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
### 3. Run the frontend
```bash
cd frontend
npm install
npm run dev
```
---
## 📊 Core Features

| Feature            | Description                                                                 |
|--------------------|-----------------------------------------------------------------------------|
| 🎯 **Player Tracking**     | Detect and track players in AFL match footage using YOLOv8 + DeepSORT         |
| 🔥 **Heatmaps**            | Visualize crowd intensity or player movement using density overlays          |
| 📈 **Dashboard**           | Live stats on tackles, movement, player positions, and crowd data           |
| 🎬 **Annotated Video**     | Render bounding boxes, player IDs, and heatmaps onto match videos           |
| 🔄 **API Integration**     | Backend APIs expose results for the frontend to visualize                   |

