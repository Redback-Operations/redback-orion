import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import torch
from torchvision.models.detection import keypointrcnn_resnet50_fpn
from analysis.limb_position import calculate_strain
import os

def load_pose_model(device='cpu'):
    model = keypointrcnn_resnet50_fpn(weights="KeypointRCNN_ResNet50_FPN_Weights.DEFAULT")
    model.to(device)
    model.eval()
    return model

def pose_estimation(image, model, device='cpu'):
    image_tensor = torch.tensor(image.transpose(2, 0, 1)).float() / 255.0  # Convert to [C, H, W]
    image_tensor = image_tensor.to(device)
    with torch.no_grad():
        predictions = model([image_tensor])[0]  # Pass as a list of tensors
    return predictions

def draw_pose(image, keypoints, strain_results=None, threshold=0.5):
    # Define limb pairs for drawing skeleton
    limb_pairs = {
        "lower_back_strain": (11, 12),  # Example: Hip to spine
        "knee_strain": (12, 14),       # Example: Hip to knee
        "shoulder_strain": (8, 10),    # Example: Hip to shoulder
        "elbow_strain": (10, 12),      # Example: Shoulder to elbow
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

def main():
    print("Current working directory:", os.getcwd())  # Debugging statement
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = load_pose_model(device)

    # Use absolute path for the image
    image_path = r"c:\Users\Lukgv\OneDrive\Desktop\REDBACK\redback-orion\Player_Tracking\Pose_Matching_project\Pose_Estimation\data\pose5.jpg"
    image = cv.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    predictions = pose_estimation(image, model, device)
    keypoints = predictions['keypoints'].cpu().numpy()  # Shape: [num_people, num_keypoints, 3]
    strain_results = None

    if len(keypoints) > 0:
        person_keypoints = keypoints[0][:, :2]  # Extract (x, y) coordinates
        exercise_type = 'deadlift'  # Change based on the exercise
        strain_results = calculate_strain(person_keypoints, exercise_type)
        print("Strain Results:", strain_results)

    image_with_pose = draw_pose(image, keypoints, strain_results)

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    axes[0].imshow(cv.cvtColor(image_with_pose, cv.COLOR_BGR2RGB))
    axes[0].axis('off')
    axes[0].set_title("Pose Estimation")

    if strain_results:
        keys = list(strain_results.keys())
        values = [v if isinstance(v, (int, float)) else 0 for v in strain_results.values()]  # Use 0 for non-numeric values
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