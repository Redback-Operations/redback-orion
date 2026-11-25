# This script performs pose estimation on images using a pre-trained Keypoint R-CNN model.
# It calculates strain metrics for various exercises, visualizes the results, and identifies the best and worst forms.
# Inputs include image files, a specified exercise type, and a pre-trained pose estimation model.

import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import torch
from torchvision.models.detection import keypointrcnn_resnet50_fpn
from analysis.limb_position import calculate_strain
import os
import csv
import random

# Loads the pre-trained Keypoint R-CNN model for pose estimation.
# Input: device ('cpu' or 'cuda').
# Output: A PyTorch model ready for inference.
def load_pose_model(device='cpu'):
    model = keypointrcnn_resnet50_fpn(weights="KeypointRCNN_ResNet50_FPN_Weights.DEFAULT")
    model.to(device)
    model.eval()
    return model

# Performs pose estimation on a given image using the loaded model.
# Inputs: image (numpy array), model (PyTorch model), device ('cpu' or 'cuda').
# Output: Predictions containing keypoints and other details.
def pose_estimation(image, model, device='cpu'):
    image_tensor = torch.tensor(image.transpose(2, 0, 1)).float() / 255.0  
    image_tensor = image_tensor.to(device)
    with torch.no_grad():
        predictions = model([image_tensor])[0]  
    return predictions

# Draws the detected pose and strain results on the image.
# Inputs: image (numpy array), keypoints (list of keypoints), strain_results (dict), threshold (float).
# Output: Image with drawn poses and strain information.
def draw_pose(image, keypoints, strain_results=None, threshold=0.5):
    # Define drawing skeleton
    limb_pairs = {
        "lower_back_strain": (11, 12),  #hip to spine.
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

# Saves strain results to a CSV file.
# Inputs: strain_results (dict), csv_path (str).
def save_strain_results_to_csv(strain_results, csv_path):
    with open(csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Metric', 'Value'])  # Write header
        for key, value in strain_results.items():
            writer.writerow([key, value])

# Loads strain results from a CSV file.
# Input: csv_path (str).
# Output: strain_results (dict).
def load_strain_results_from_csv(csv_path):
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

# Lists files in the specified data directory.
# Input: data_dir (str).
# Output: List of file names.
def list_files_in_data_directory(data_dir):
    try:
        return [f for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f))]
    except FileNotFoundError:
        print(f"Error: Directory {data_dir} not found.")
        return []

# Evaluates images in the data directory to find the one with the best form based on strain metrics.
# Inputs: data_dir (str), model (PyTorch model), device ('cpu' or 'cuda'), exercise_type (str).
# Output: Path to the best image and its strain results.
def evaluate_images(data_dir, model, device, exercise_type):
    best_image_path = None
    best_strain_score = float('inf')  # Lower strain score is better
    best_strain_results = None

    for file in os.listdir(data_dir):
        image_path = os.path.join(data_dir, file)
        if not os.path.isfile(image_path):
            continue

        image = cv.imread(image_path)
        if image is None:
            print(f"Warning: Unable to read image {image_path}. Skipping.")
            continue

        predictions = pose_estimation(image, model, device)
        keypoints = predictions['keypoints'].cpu().numpy()  # Shape: [num_people, num_keypoints, 3]

        if len(keypoints) > 0:
            person_keypoints = keypoints[0][:, :2]  # Extract (x, y) coordinates
            strain_results = calculate_strain(person_keypoints, exercise_type)

            # Calculate a total strain score (sum of numeric strain metrics)
            numeric_strain_results = {
                key: value for key, value in strain_results.items()
                if isinstance(value, (int, float))
            }
            total_strain_score = sum(numeric_strain_results.values())

            # Update the best image if this one has a lower strain score
            if total_strain_score < best_strain_score:
                best_image_path = image_path
                best_strain_score = total_strain_score
                best_strain_results = strain_results

    return best_image_path, best_strain_results

# Displays images with their corresponding strain graphs.
# Inputs: data_dir (str), model (PyTorch model), device ('cpu' or 'cuda'), exercise_type (str).
def display_images_with_strain(data_dir, model, device, exercise_type):
    images = []
    strain_graphs = []

    for file in os.listdir(data_dir):
        image_path = os.path.join(data_dir, file)
        if not os.path.isfile(image_path):
            continue

        image = cv.imread(image_path)
        if image is None:
            print(f"Warning: Unable to read image {image_path}. Skipping.")
            continue

        predictions = pose_estimation(image, model, device)
        keypoints = predictions['keypoints'].cpu().numpy()  # Shape: [num_people, num_keypoints, 3]

        if len(keypoints) > 0:
            person_keypoints = keypoints[0][:, :2]  # Extract (x, y) coordinates
            strain_results = calculate_strain(person_keypoints, exercise_type)

            # Draw pose on the image
            image_with_pose = draw_pose(image.copy(), keypoints, strain_results)
            images.append(image_with_pose)

            # Create strain graph
            numeric_strain_results = {
                key: value for key, value in strain_results.items()
                if isinstance(value, (int, float))
            }
            if numeric_strain_results:
                keys = list(numeric_strain_results.keys())
                values = list(numeric_strain_results.values())
                fig, ax = plt.subplots(figsize=(4, 3))
                ax.barh(keys, values, color='skyblue')
                ax.set_title("Strain Metrics")
                ax.set_xlabel("Value")
                ax.set_xlim(0, max(values) * 1.2)
                fig.canvas.draw()
                graph_image = np.frombuffer(fig.canvas.tostring_argb(), dtype=np.uint8)
                graph_image = graph_image.reshape(fig.canvas.get_width_height()[::-1] + (4,))
                graph_image = graph_image[:, :, 1:]  # Convert ARGB to RGB by dropping the alpha channel
                plt.close(fig)
                strain_graphs.append(graph_image)
            else:
                strain_graphs.append(None)

    # Combine images and graphs into a single figure
    num_images = len(images)
    fig, axes = plt.subplots(num_images, 2, figsize=(10, 5 * num_images))

    for i, (image, graph) in enumerate(zip(images, strain_graphs)):
        axes[i, 0].imshow(cv.cvtColor(image, cv.COLOR_BGR2RGB))
        axes[i, 0].axis('off')
        axes[i, 0].set_title(f"Image {i + 1}")

        if graph is not None:
            axes[i, 1].imshow(graph)
            axes[i, 1].axis('off')
            axes[i, 1].set_title(f"Strain Graph {i + 1}")
        else:
            axes[i, 1].text(0.5, 0.5, "No Strain Data", ha='center', va='center', fontsize=12)
            axes[i, 1].axis('off')

    plt.tight_layout()
    plt.show()

# Displays the best and worst images based on strain metrics along with their corresponding strain graphs.
# Inputs: data_dir (str), model (PyTorch model), device ('cpu' or 'cuda'), exercise_type (str).
def display_best_and_worst_images_with_strain(data_dir, model, device, exercise_type):
    image_data = []

    for file in os.listdir(data_dir):
        image_path = os.path.join(data_dir, file)
        if not os.path.isfile(image_path):
            continue

        image = cv.imread(image_path)
        if image is None:
            print(f"Warning: Unable to read image {image_path}. Skipping.")
            continue

        predictions = pose_estimation(image, model, device)
        keypoints = predictions['keypoints'].cpu().numpy()  # Shape: [num_people, num_keypoints, 3]

        if len(keypoints) > 0:
            person_keypoints = keypoints[0][:, :2]  # Extract (x, y) coordinates
            strain_results = calculate_strain(person_keypoints, exercise_type)

            # Calculate a total strain score (sum of numeric strain metrics)
            numeric_strain_results = {
                key: value for key, value in strain_results.items()
                if isinstance(value, (int, float))
            }
            total_strain_score = sum(numeric_strain_results.values())

            # Store image data
            image_data.append({
                "image_path": image_path,
                "image": image,
                "keypoints": keypoints,
                "strain_results": strain_results,
                "total_strain_score": total_strain_score
            })

    if len(image_data) < 2:
        print("Not enough images to select best and worst. Exiting.")
        return

    # Find the best and worst images based on total strain score
    best_image = min(image_data, key=lambda x: x["total_strain_score"])
    worst_image = max(image_data, key=lambda x: x["total_strain_score"])

    # Display the best and worst images with their strain graphs
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))  # 2 rows, 2 columns

    for i, (rank, data) in enumerate([("Best", best_image), ("Worst", worst_image)]):
        # Draw pose on the image
        image_with_pose = draw_pose(data["image"].copy(), data["keypoints"], data["strain_results"])

        # Display the image
        axes[i, 0].imshow(cv.cvtColor(image_with_pose, cv.COLOR_BGR2RGB))
        axes[i, 0].axis('off')
        axes[i, 0].set_title(f"{rank} Form: {data['image_path']}")

        # Create and display the strain graph
        numeric_strain_results = {
            key: value for key, value in data["strain_results"].items()
            if isinstance(value, (int, float))
        }
        if numeric_strain_results:
            keys = list(numeric_strain_results.keys())
            values = list(numeric_strain_results.values())
            axes[i, 1].barh(keys, values, color='skyblue')
            axes[i, 1].set_title(f"Strain Metrics ({rank} Form)")
            axes[i, 1].set_xlabel("Value")
        else:
            axes[i, 1].text(0.5, 0.5, "No Strain Data", ha='center', va='center', fontsize=12)
            axes[i, 1].axis('off')

    plt.tight_layout()
    plt.show()

# Main function to load the model, prompt user for workout type, and display best and worst images with strain graphs.
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

    # List files in the data directory
    data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')  # Relative path to the data directory
    if not os.path.exists(data_dir):
        print(f"Error: Data directory {data_dir} does not exist. Exiting.")
        return

    # Display the best and worst images with their corresponding strain graphs
    display_best_and_worst_images_with_strain(data_dir, model, device, exercise_type)

if __name__ == "__main__":
    main()