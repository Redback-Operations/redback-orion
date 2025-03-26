import cv2
import numpy as np
import torch

def resize_image(image, target_size=(224, 224)):
    """Resize the input image to the target size."""
    return cv2.resize(image, target_size)

def normalize_image(image):
    """Normalize the pixel values of the image to the range [0, 1]."""
    return image.astype(np.float32) / 255.0

def augment_image(image):
    """Apply data augmentation techniques to the image."""
    # Example augmentation: flipping the image horizontally
    if np.random.rand() > 0.5:
        image = cv2.flip(image, 1)
    return image

def preprocess_image(image):
    """Preprocess the input image by resizing, normalizing, and converting to a tensor."""
    image = resize_image(image)
    image = normalize_image(image)
    image = torch.tensor(image.transpose(2, 0, 1))  # Convert to (C, H, W)
    return image

# filepath: c:\Users\Lukgv\OneDrive\Desktop\REDBACK\redback-orion\Player_Tracking\Pose_Matching_project\Pose_Estimation\pose-estimation-fitness\src\data\preprocess.py
import cv2
import torch

def preprocess_image(image, target_size=(640, 480)):
    resized_image = cv2.resize(image, target_size)
    image_tensor = torch.tensor(resized_image.transpose(2, 0, 1)).float() / 255.0  # Normalize to [0, 1]
    return image_tensor