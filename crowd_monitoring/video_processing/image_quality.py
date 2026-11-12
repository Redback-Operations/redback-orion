import cv2
import numpy as np
import os

class ImageQualityAnalyzer:
    """
    Analyze basic image quality metrics for extracted video frames.
    """

    def analyze(self, image_path: str) -> dict:
        image = cv2.imread(image_path)

        if image is None:
            raise FileNotFoundError(f"Image not found: {image_path}")

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        brightness = float(np.mean(gray))
        contrast = float(np.std(gray))
        blur = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        sharpness = float(
            np.mean(np.sqrt(sobelx ** 2 + sobely ** 2))
        )

        return {
            "image_path": image_path,
            "brightness": round(brightness, 2),
            "contrast": round(contrast, 2),
            "blur": round(blur, 2),
            "sharpness": round(sharpness, 2),
        }


BRIGHTNESS_THRESHOLD = 50
CONTRAST_THRESHOLD = 49
BLUR_THRESHOLD = 150
SHARPNESS_THRESHOLD = 45


def recommend_enhancement(metrics: dict) -> dict:
    recommendations = []

    if metrics["contrast"] < CONTRAST_THRESHOLD:
        recommendations.append("Apply CLAHE")

    if metrics["brightness"] < BRIGHTNESS_THRESHOLD:
        recommendations.append("Increase brightness")

    if metrics["blur"] < BLUR_THRESHOLD:
        recommendations.append("Frame may be blurred")

    if metrics["sharpness"] < SHARPNESS_THRESHOLD:
        recommendations.append("Low sharpness detected")

    return {
        "recommendations": recommendations or ["No enhancement required"]
    }


if __name__ == "__main__":
    sample_image = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "data",
        "validation_frames",
        "top&distant_frame_000000.jpg"
    )

    analyzer = ImageQualityAnalyzer()
    metrics = analyzer.analyze(sample_image)

    print("\nImage Quality Metrics\n")

    for key, value in metrics.items():
        print(f"{key}: {value}")

    result = recommend_enhancement(metrics)

    print("\nEnhancement Recommendations\n")

    for item in result["recommendations"]:
        print(f"- {item}")