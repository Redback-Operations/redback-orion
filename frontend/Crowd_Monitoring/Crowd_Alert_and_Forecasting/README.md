
# Automated Setup for Crowd Monitoring Project

This guide explains how to set up the project environment using the provided automated setup scripts for both Linux/Mac and Windows systems. The setup process includes the installation of necessary dependencies such as YOLOv8, Prophet for forecasting, Flask, OpenCV, and others.

The scripts automate the creation of a virtual environment, installation of dependencies from the `requirements.txt`, and setup for MongoDB connection via a `.env` file.

## Project Structure

```
├── README.md                # This file (setup guide)
├── setup.sh                 # Automated setup script for Linux/Mac
├── setup.bat                # Automated setup script for Windows
├── requirements.txt         # List of all dependencies for the project
```

## Prerequisites

Before running the setup scripts, make sure you have the following installed on your system:

- **Python 3.7+**
- **pip** (Python package manager)
- **curl** (for Linux/Mac) to download the YOLOv8 model weights
- **MongoDB** (optional, if using MongoDB for data storage)

## Setup Instructions

### For Linux/Mac Users

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Redback-Operations/redback-orion.git
   cd Crowd_Monitoring
   ```

2. **Run the automated setup script**:
   ```bash
   ./setup.sh
   ```

   This script will:
   - Create a Python virtual environment.
   - Install all the dependencies listed in `requirements.txt`.
   - Download the YOLOv8 pre-trained model weights.
   - Create a `.env` file for MongoDB connection.

3. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate
   ```

4. **Run the application** (after the setup is complete):
   ```bash
   python app.py  # Or the entry point for your project
   ```

---

### For Windows Users

1. **Clone the repository**:
   ```batch
   git clone https://github.com/Redback-Operations/redback-orion.git
   cd Crowd_Monitoring
   ```

2. **Run the automated setup script**:
   ```batch
   setup.bat
   ```

   This script will:
   - Create a Python virtual environment.
   - Install all the dependencies listed in `requirements.txt`.
   - Download the YOLOv8 pre-trained model weights.
   - Create a `.env` file for MongoDB connection.

3. **Activate the virtual environment**:
   ```batch
   call venv\Scripts\activate
   ```

4. **Run the application** (after the setup is complete):
   ```batch
   python app.py  # Or the entry point for your project
   ```

---

## Manual Setup (Optional)

If you want to set up the project manually without using the automated scripts, follow these steps:

1. **Create a Python virtual environment**:
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment**:
   - For Linux/Mac:
     ```bash
     source venv/bin/activate
     ```
   - For Windows:
     ```batch
     call venv\Scripts\activate
     ```

3. **Install dependencies from `requirements.txt`**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Download YOLOv8 pre-trained weights (optional)**:
   ```bash
   curl -L -o yolov8n.pt https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
   ```

5. **Create a `.env` file** for MongoDB connection (optional):
   ```bash
   echo MONGO_URI=mongodb://localhost:27017 > .env
   ```

6. **Run the application**:
   ```bash
   python app.py  # Or the entry point for your project
   ```

---

## Troubleshooting

- **Permission Issues (Linux/Mac)**: If you encounter a "Permission Denied" error when running the script, use this command to make the script executable:
  ```bash
  chmod +x setup.sh
  ```

- **Virtual Environment Activation Issues**: If you have trouble activating the virtual environment, ensure that Python is installed correctly and the virtual environment folder (`venv`) exists.

- **Missing Dependencies**: Make sure you have installed all prerequisites like Python 3.7+ and pip. If any package installation fails, check the error logs to manually install missing packages.

---

## Frequently Asked Questions (FAQ)

### 1. What does the setup script do?
The setup script automates the creation of a virtual environment, installs all necessary Python dependencies, downloads the YOLOv8 model weights, and sets up environment variables using a `.env` file.

### 2. What is the `.env` file for?
The `.env` file is used to securely store environment variables, such as MongoDB connection details. You can update this file with your specific connection strings or secrets.

### 3. How do I manually install dependencies without the script?
You can manually install the dependencies by activating your virtual environment and running:
```bash
pip install -r requirements.txt
```

---

## Conclusion

By following these instructions, you will be able to quickly set up your environment and get the project running without manually installing each component. If you encounter any issues or need further assistance, feel free to reach out for help.
