import sys
from pathlib import Path

import torch
from PIL import Image
from torch import nn
from torchvision import transforms


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_FOLDER / "models" / "jumper_digit_model.pth"
IMAGE_SIZE = 64


class JumperDigitModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Flatten(),
            nn.Linear(IMAGE_SIZE * IMAGE_SIZE, 128),
            nn.ReLU(),
        )
        self.tens_output = nn.Linear(128, 10)
        self.ones_output = nn.Linear(128, 10)

    def forward(self, images):
        features = self.features(images)
        return self.tens_output(features), self.ones_output(features)


if len(sys.argv) != 2:
    raise SystemExit("Usage: python predict_jumper_digits.py <image_path>")

image_path = Path(sys.argv[1])
if not image_path.is_file():
    raise SystemExit(f"Image not found: {image_path}")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
checkpoint = torch.load(MODEL_PATH, map_location=device, weights_only=True)

model = JumperDigitModel().to(device)
model.load_state_dict(checkpoint["model"])
model.eval()

transform = transforms.Compose(
    [
        transforms.Grayscale(),
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
    ]
)

image = transform(Image.open(image_path)).unsqueeze(0).to(device)

with torch.no_grad():
    tens_scores, ones_scores = model(image)
    tens_probabilities = torch.softmax(tens_scores, dim=1)
    ones_probabilities = torch.softmax(ones_scores, dim=1)
    tens_confidence, tens = tens_probabilities.max(dim=1)
    ones_confidence, ones = ones_probabilities.max(dim=1)

tens = tens.item()
ones = ones.item()
predicted_number = str(ones) if tens == 0 else str(tens * 10 + ones)
combined_confidence = tens_confidence.item() * ones_confidence.item()

print(f"Tens prediction: {'blank' if tens == 0 else tens}")
print(f"Ones prediction: {ones}")
print(f"Predicted jumper number: {predicted_number}")
print(f"Combined confidence: {combined_confidence:.1%}")
