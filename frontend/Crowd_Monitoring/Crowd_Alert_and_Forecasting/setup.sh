#!/bin/bash

# Exit immediately if any command exits with a non-zero status
set -e

# Displaying a message for starting the setup process
echo "Starting setup process..."

# Step 1: Create and activate a Python virtual environment
echo "Creating a Python virtual environment..."
python3 -m venv venv

# Check if virtualenv creation was successful
if [ -d "venv" ]; then
    echo "Virtual environment created successfully."
else
    echo "Failed to create virtual environment."
    exit 1
fi

# Activate the virtual environment
echo "Activating the virtual environment..."
source venv/bin/activate

# Step 2: Upgrade pip to the latest version
echo "Upgrading pip to the latest version..."
pip install --upgrade pip

# Step 3: Install the required Python packages from requirements.txt
echo "Installing dependencies from requirements.txt..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "Dependencies installed successfully."
else
    echo "requirements.txt file not found! Please make sure the file exists."
    exit 1
fi

# Step 4: Download YOLOv8 pre-trained model weights (optional)
YOLO_WEIGHTS_URL="https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt"
echo "Downloading YOLOv8 model weights..."
if curl --output /dev/null --silent --head --fail "$YOLO_WEIGHTS_URL"; then
    curl -L -o yolov8n.pt $YOLO_WEIGHTS_URL
    echo "YOLOv8 model weights downloaded successfully."
else
    echo "Failed to download YOLOv8 model weights. Please check the URL."
fi

# Step 5: Create .env file for environment variables if it doesn't exist
if [ -f ".env" ]; then
    echo ".env file already exists."
else
    echo "Creating .env file for environment variables..."
    touch .env
    echo "MONGO_URI=mongodb://localhost:27017" >> .env
    echo ".env file created with default MongoDB URI."
fi

# Final Step: Display success message and instructions for activation
echo "Setup completed successfully!"
echo "To activate the virtual environment, run the following command:"
echo "source venv/bin/activate"

# Exit the script
exit 0
