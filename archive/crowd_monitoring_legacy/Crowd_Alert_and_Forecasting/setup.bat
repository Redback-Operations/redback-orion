@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

:: Step 1: Create a Python virtual environment
echo Creating a Python virtual environment...
python -m venv venv

:: Check if the virtual environment was created successfully
if exist venv (
    echo Virtual environment created successfully.
) else (
    echo Failed to create virtual environment.
    exit /b 1
)

:: Step 2: Activate the virtual environment
echo Activating the virtual environment...
call venv\Scripts\activate

:: Step 3: Upgrade pip to the latest version
echo Upgrading pip to the latest version...
python -m pip install --upgrade pip

:: Step 4: Install the required Python packages from requirements.txt
echo Installing dependencies from requirements.txt...
if exist requirements.txt (
    pip install -r requirements.txt
    echo Dependencies installed successfully.
) else (
    echo requirements.txt file not found! Please make sure the file exists.
    exit /b 1
)

:: Step 5: Download YOLOv8 pre-trained model weights (optional)
set YOLO_WEIGHTS_URL=https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
echo Downloading YOLOv8 model weights...
curl -L -o yolov8n.pt %YOLO_WEIGHTS_URL%

if exist yolov8n.pt (
    echo YOLOv8 model weights downloaded successfully.
) else (
    echo Failed to download YOLOv8 model weights. Please check the URL or your internet connection.
)

:: Step 6: Create .env file for environment variables if it doesn't exist
if exist .env (
    echo .env file already exists.
) else (
    echo Creating .env file for environment variables...
    echo MONGO_URI=mongodb://localhost:27017 > .env
    echo .env file created with default MongoDB URI.
)

:: Final Step: Display success message and instructions for activation
echo Setup completed successfully!
echo To activate the virtual environment, run the following command:
echo call venv\Scripts\activate

pause
