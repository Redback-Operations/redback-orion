import cv2
import numpy as np
import torch

# This file is used to preprocess images for pose estimation and strain analysis
# If your data is already in the correct format, you can skip this step

def resize_image(image, target_size=(224, 224)):
    return cv2.resize(image, target_size)

def normalize_image(image):
    return image.astype(np.float32) / 255.0

def augment_image(image):
    if np.random.rand() > 0.5:
        image = cv2.flip(image, 1)
    return image

def preprocess_image(image):
    image = resize_image(image)
    image = normalize_image(image)
    image = torch.tensor(image.transpose(2, 0, 1))  # Convert to (C, H, W)
    return image

import cv2
import torch

def preprocess_image(image, target_size=(640, 480)):
    resized_image = cv2.resize(image, target_size)
    image_tensor = torch.tensor(resized_image.transpose(2, 0, 1)).float() / 255.0  # Normalize to [0, 1]
    return image_tensor