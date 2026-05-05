# AFL Player Tracking and Crowd Monitoring

Project 4 Orion is part of the Redback Company that focuses on AI computer visions of VFL game footafge to enhance 
- **Player Tracking**
- **Crowd Monitoring**
- **VFL Analytics Dashboards**

The system follows a microservices architecture with a FastAPI backend acting as an API gateway between the frontend and ML services.

## 🎯 Project Objectives

- 🏃‍♂️ **Track individual VFL players**
- 👥 **Monitor crowd density and movement**
- 🎥 **Overlay visual analytics (bounding boxes, heatmaps**
- 📊 **Generate dashboards**
- 🧠 **Integrate multiple services through a backend API gateway**

---

## 🖥️ Technologies Used

| Layer       | Tech Stack |
|-------------|------------|
| Frontend    | React, Vite, Tailwind |
| Backend     | Python, FastAPI, Uvicorn |
| ML Models   | YOLO, DeepSORT |
| Dev Tools   | GitHub, VS Code, Docker.. |

---

## Architecture Overview

      Frontend (React)
              │
              ▼
    Backend API (FastAPI)
              │
              ▼
 ┌─────────────────────────┐
 │     API Gateway Layer   │
 └─────────────────────────┘
              │
   ┌──────────┴─────────┐
   ▼                    ▼
Player Service     Crowd Service
   (YOLO)           (Density)

## 🚀 How to Run the Project

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/redback-project4.git
cd redback-orion/26_T1/afl_player_tracking_and_crowd_monitoring
```
### 2. Run the backend
**Navigate to the backend folder**
cd backend

**Create and activate virtual environment**
**(Mac)**
python -m venv .venv
source .venv/bin/activate
**(Windows)**
.venv\Scripts\activate

**Install required Python packages**
pip install -r requirements.txt

**Start the FastAPI server**
uvicorn app.main:app --reload --port 8000

### 3. Run the frontend
**Open a new terminal (command + t)**
cd frontend

**Install the required Node.js dependencies**
npm install

**Start the development server**
npm run dev

cd frontend
npm install
npm run dev
```
---
## 📊 Core Features

| Feature            | Description                                                                 |
|--------------------|-----------------------------------------------------------------------------|
| 🎯 **Player Tracking**     | Detect and track players in VFL match footage using YOLO + tracking algs    |
| 👥 **Crowd Monitoring      | Analyse crowd density, movement and distribution across statium areas       |
| 🔥 **Heatmaps**            | Visualise crowd intensity or player movement using spatial heatmaps         |
| 📈 **Dashboard**           | Live stats on tackles, movement, player positions, and crowd data           |
| 🎬 **Annotated Video**     | Render bounding boxes, player IDs, directly onto video footage              |
| 🔄 **API Integration**     | FastAPI backend connects frontend with player and crowd services through a unified API |

