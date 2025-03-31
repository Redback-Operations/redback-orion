import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import torch
from torchvision.models.detection import keypointrcnn_resnet50_fpn
from analysis.limb_position import calculate_strain
import os
import csv

def load_pose_model(device='cpu'):
    model = keypointrcnn_resnet50_fpn(weights="KeypointRCNN_ResNet50_FPN_Weights.DEFAULT")
    model.to(device)
    model.eval()
    return model

def pose_estimation(image, model, device='cpu'):
    image_tensor = torch.tensor(image.transpose(2, 0, 1)).float() / 255.0  
    image_tensor = image_tensor.to(device)
    with torch.no_grad():
        predictions = model([image_tensor])[0]  
    return predictions

def draw_pose(image, keypoints, strain_results=None, threshold=0.5):
    # Define drawing skeleton
    limb_pairs = {
        "lower_back_strain": (11, 12),  #Hip to spine
        "knee_strain": (12, 14),       #Hip to knee
        "shoulder_strain": (8, 10),    #Hip to shoulder
        "elbow_strain": (10, 12),      #Shoulder to elbow
    }

    for person_keypoints in keypoints:  # Iterate over each detected person
        for keypoint in person_keypoints:
            if keypoint[2] > threshold:  # Check confidence score
                cv.circle(image, (int(keypoint[0]), int(keypoint[1])), 5, (0, 255, 0), -1)

        for limb, (start_idx, end_idx) in limb_pairs.items():
            if strain_results and limb in strain_results and "High strain" in strain_results[limb]:
                if person_keypoints[start_idx][2] > threshold and person_keypoints[end_idx][2] > threshold:
                    start_point = (int(person_keypoints[start_idx][0]), int(person_keypoints[start_idx][1]))
                    end_point = (int(person_keypoints[end_idx][0]), int(person_keypoints[end_idx][1]))
                    cv.line(image, start_point, end_point, (0, 0, 255), 3)  # Red line for strain
            else:
                if person_keypoints[start_idx][2] > threshold and person_keypoints[end_idx][2] > threshold:
                    start_point = (int(person_keypoints[start_idx][0]), int(person_keypoints[start_idx][1]))
                    end_point = (int(person_keypoints[end_idx][0]), int(person_keypoints[end_idx][1]))
                    cv.line(image, start_point, end_point, (0, 255, 0), 2)  # Green line for normal

    if strain_results:
        y_offset = 20  # Starting y-coordinate for text
        for key, value in strain_results.items():
            text = f"{key}: {value}"
            cv.putText(image, text, (10, y_offset), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
            y_offset += 20  # Increment y-coordinate for the next line of text
    return image

def save_strain_results_to_csv(strain_results, csv_path):
    """
    Save strain results to a CSV file.

    Parameters:
    strain_results (dict): The dictionary containing strain metrics.
    csv_path (str): The path to the CSV file.
    """
    with open(csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Metric', 'Value'])  # Write header
        for key, value in strain_results.items():
            writer.writerow([key, value])

def load_strain_results_from_csv(csv_path):
    """
    Load strain results from a CSV file.

    Parameters:
    csv_path (str): The path to the CSV file.

    Returns:
    dict: A dictionary containing strain metrics.
    """
    strain_results = {}
    with open(csv_path, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            key, value = row
            try:
                strain_results[key] = float(value)  # Convert numeric values
            except ValueError:
                strain_results[key] = value  # Keep non-numeric values as strings
    return strain_results

def list_files_in_data_directory(data_dir):
    """
    List all files in the specified data directory.

    Parameters:
    data_dir (str): Path to the data directory.

    Returns:
    list: A list of filenames in the directory.
    """
    try:
        return [f for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f))]
    except FileNotFoundError:
        print(f"Error: Directory {data_dir} not found.")
        return []

def main():
    print("Current working directory:", os.getcwd())  # Debugging statement
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = load_pose_model(device)

    # Prompt user for workout type
    workout_types = ['deadlift', 'bench press', 'squat']
    print("Available workout types:")
    for i, workout in enumerate(workout_types, start=1):
        print(f"{i}. {workout}")

    try:
        workout_index = int(input("Enter the number of the workout type: ")) - 1
        if workout_index < 0 or workout_index >= len(workout_types):
            print("Error: Invalid workout selection. Exiting.")
            return
        exercise_type = workout_types[workout_index]
    except ValueError:
        print("Error: Invalid input. Exiting.")
        return

    # List files in the data directory and prompt user to select one
    data_dir = r"c:\Users\Lukgv\OneDrive\Desktop\REDBACK\redback-orion\Player_Tracking\Pose_Matching_project\Pose_Estimation\data"
    files = list_files_in_data_directory(data_dir)
    if not files:
        print("No files found in the data directory. Exiting.")
        return

    print("Available files in the data directory:")
    for i, file in enumerate(files, start=1):
        print(f"{i}. {file}")

    try:
        file_index = int(input("Enter the number of the file to load: ")) - 1
        if file_index < 0 or file_index >= len(files):
            print("Error: Invalid file selection. Exiting.")
            return
        image_path = os.path.join(data_dir, files[file_index])
    except ValueError:
        print("Error: Invalid input. Exiting.")
        return

    csv_path = os.path.join(data_dir, "strain_results.csv")
    image = cv.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    predictions = pose_estimation(image, model, device)
    keypoints = predictions['keypoints'].cpu().numpy()  # Shape: [num_people, num_keypoints, 3]
    strain_results = None

    if len(keypoints) > 0:
        person_keypoints = keypoints[0][:, :2]  # Extract (x, y) coordinates
        strain_results = calculate_strain(person_keypoints, exercise_type)
        print("Strain Results:", strain_results)

        # Save strain results to CSV
        save_strain_results_to_csv(strain_results, csv_path)

    # Load strain results from CSV for plotting
    strain_results = load_strain_results_from_csv(csv_path)

    # Filter out non-numeric or unwanted keys
    numeric_strain_results = {
        key: value for key, value in strain_results.items()
        if isinstance(value, (int, float)) and key not in ['back_straightness', 'hip_alignment']
    }

    image_with_pose = draw_pose(image, keypoints, strain_results)

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    axes[0].imshow(cv.cvtColor(image_with_pose, cv.COLOR_BGR2RGB))
    axes[0].axis('off')
    axes[0].set_title("Pose Estimation")

    if numeric_strain_results:
        keys = list(numeric_strain_results.keys())
        values = list(numeric_strain_results.values())
        axes[1].barh(keys, values, color='skyblue')
        axes[1].set_title("Strain Metrics")
        axes[1].set_xlabel("Value")
    else:
        axes[1].text(0.5, 0.5, "No Strain Data", ha='center', va='center', fontsize=12)
        axes[1].axis('off')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()