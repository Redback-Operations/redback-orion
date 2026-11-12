import argparse
import random
from pathlib import Path

import pandas as pd
import torch
from PIL import Image
from torch import nn
from torch.utils.data import DataLoader, Dataset, Subset
from torchvision import transforms


BLANK_TENS = 10


class NFLJumperDataset(Dataset):
    """Load images from one folder and labels from the Kaggle CSV file."""

    def __init__(self, dataframe, images_folder, transform=None):
        self.data = dataframe.reset_index(drop=True)
        self.images_folder = Path(images_folder)
        self.transform = transform

        columns = {column.lower(): column for column in self.data.columns}

        if "label" not in columns:
            raise ValueError(
                f"CSV must contain a 'label' column. Found: {list(self.data.columns)}"
            )

        if "filename" in columns:
            self.image_column = columns["filename"]
        elif "filepath" in columns:
            self.image_column = columns["filepath"]
        else:
            raise ValueError(
                "CSV must contain a 'filename' or 'filepath' column. "
                f"Found: {list(self.data.columns)}"
            )

        self.label_column = columns["label"]

    def __len__(self):
        return len(self.data)

    def _find_image(self, stored_path):
        """Handle either a filename or a relative path stored in the CSV."""
        stored_path = Path(str(stored_path).replace("\\", "/"))

        candidates = [
            stored_path,
            self.images_folder / stored_path,
            self.images_folder / stored_path.name,
        ]

        for candidate in candidates:
            if candidate.is_file():
                return candidate

        raise FileNotFoundError(
            f"Could not find '{stored_path}'. Checked inside "
            f"'{self.images_folder}'."
        )

    def __getitem__(self, index):
        row = self.data.iloc[index]
        image_path = self._find_image(row[self.image_column])
        image = Image.open(image_path).convert("RGB")

        number = int(float(row[self.label_column]))
        if not 0 <= number <= 99:
            raise ValueError(f"Invalid jumper number {number} in row {index}")

        if number < 10:
            tens_label = BLANK_TENS
            ones_label = number
        else:
            tens_label = number // 10
            ones_label = number % 10

        if self.transform is not None:
            image = self.transform(image)

        return (
            image,
            torch.tensor(tens_label, dtype=torch.long),
            torch.tensor(ones_label, dtype=torch.long),
        )


class JumperNumberCNN(nn.Module):
    """Small CNN with separate outputs for the tens and ones digits."""

    def __init__(self):
        super().__init__()

        self.features = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )

        self.shared = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * 8 * 8, 256),
            nn.ReLU(),
            nn.Dropout(0.4),
        )

        self.tens_output = nn.Linear(256, 11)
        self.ones_output = nn.Linear(256, 10)

    def forward(self, images):
        features = self.features(images)
        features = self.shared(features)
        return self.tens_output(features), self.ones_output(features)


def prepare_dataframe(csv_path):
    dataframe = pd.read_csv(csv_path)
    columns = {column.lower(): column for column in dataframe.columns}

    if "label" not in columns:
        raise ValueError(
            f"CSV must contain a 'label' column. Found: {list(dataframe.columns)}"
        )

    label_column = columns["label"]
    dataframe[label_column] = pd.to_numeric(
        dataframe[label_column], errors="coerce"
    )
    dataframe = dataframe.dropna(subset=[label_column]).copy()
    dataframe = dataframe[
        (dataframe[label_column] >= 0) & (dataframe[label_column] <= 99)
    ]

    if len(dataframe) < 2:
        raise ValueError("Not enough valid rows were found in the CSV file.")

    return dataframe.reset_index(drop=True)


def make_loaders(dataframe, images_folder, batch_size, val_fraction, seed):
    train_transform = transforms.Compose(
        [
            transforms.Resize((64, 64)),
            transforms.Grayscale(num_output_channels=1),
            transforms.RandomRotation(5),
            transforms.ColorJitter(brightness=0.2, contrast=0.2),
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,)),
        ]
    )

    val_transform = transforms.Compose(
        [
            transforms.Resize((64, 64)),
            transforms.Grayscale(num_output_channels=1),
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,)),
        ]
    )

    generator = torch.Generator().manual_seed(seed)
    indices = torch.randperm(len(dataframe), generator=generator).tolist()

    val_size = max(1, int(len(indices) * val_fraction))
    val_indices = indices[:val_size]
    train_indices = indices[val_size:]

    train_dataset = NFLJumperDataset(dataframe, images_folder, train_transform)
    val_dataset = NFLJumperDataset(dataframe, images_folder, val_transform)

    train_loader = DataLoader(
        Subset(train_dataset, train_indices),
        batch_size=batch_size,
        shuffle=True,
        num_workers=0,
    )
    val_loader = DataLoader(
        Subset(val_dataset, val_indices),
        batch_size=batch_size,
        shuffle=False,
        num_workers=0,
    )

    return train_loader, val_loader, len(train_indices), len(val_indices)


def train_one_epoch(model, loader, optimizer, loss_function, device):
    model.train()
    running_loss = 0.0

    for images, tens_labels, ones_labels in loader:
        images = images.to(device)
        tens_labels = tens_labels.to(device)
        ones_labels = ones_labels.to(device)

        tens_predictions, ones_predictions = model(images)
        loss = loss_function(tens_predictions, tens_labels)
        loss += loss_function(ones_predictions, ones_labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)

    return running_loss / len(loader.dataset)


def validate(model, loader, loss_function, device):
    model.eval()
    running_loss = 0.0
    tens_correct = 0
    ones_correct = 0
    complete_correct = 0

    with torch.no_grad():
        for images, tens_labels, ones_labels in loader:
            images = images.to(device)
            tens_labels = tens_labels.to(device)
            ones_labels = ones_labels.to(device)

            tens_predictions, ones_predictions = model(images)
            loss = loss_function(tens_predictions, tens_labels)
            loss += loss_function(ones_predictions, ones_labels)

            predicted_tens = tens_predictions.argmax(dim=1)
            predicted_ones = ones_predictions.argmax(dim=1)

            tens_correct += (predicted_tens == tens_labels).sum().item()
            ones_correct += (predicted_ones == ones_labels).sum().item()
            complete_correct += (
                (predicted_tens == tens_labels)
                & (predicted_ones == ones_labels)
            ).sum().item()

            running_loss += loss.item() * images.size(0)

    total = len(loader.dataset)
    return {
        "loss": running_loss / total,
        "tens_accuracy": tens_correct / total,
        "ones_accuracy": ones_correct / total,
        "complete_accuracy": complete_correct / total,
    }


def parse_args():
    parser = argparse.ArgumentParser(
        description="Train a two-digit CNN on the NFL Player Numbers dataset."
    )
    parser.add_argument("--csv", required=True, help="Path to the labels CSV")
    parser.add_argument(
        "--images", required=True, help="Folder containing all dataset images"
    )
    parser.add_argument(
        "--output", default="models/nfl_jumper_cnn.pth", help="Saved model path"
    )
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--learning-rate", type=float, default=0.001)
    parser.add_argument("--val-fraction", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main():
    args = parse_args()

    if not 0 < args.val_fraction < 1:
        raise ValueError("--val-fraction must be between 0 and 1.")

    random.seed(args.seed)
    torch.manual_seed(args.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    dataframe = prepare_dataframe(args.csv)
    train_loader, val_loader, train_size, val_size = make_loaders(
        dataframe,
        args.images,
        args.batch_size,
        args.val_fraction,
        args.seed,
    )

    print(f"Valid labelled images: {len(dataframe)}")
    print(f"Training images: {train_size}")
    print(f"Validation images: {val_size}")

    model = JumperNumberCNN().to(device)
    loss_function = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    best_accuracy = 0.0

    for epoch in range(args.epochs):
        train_loss = train_one_epoch(
            model, train_loader, optimizer, loss_function, device
        )
        metrics = validate(model, val_loader, loss_function, device)

        print(
            f"Epoch {epoch + 1}/{args.epochs} | "
            f"train loss: {train_loss:.4f} | "
            f"val loss: {metrics['loss']:.4f} | "
            f"tens: {metrics['tens_accuracy']:.1%} | "
            f"ones: {metrics['ones_accuracy']:.1%} | "
            f"complete number: {metrics['complete_accuracy']:.1%}"
        )

        if metrics["complete_accuracy"] > best_accuracy:
            best_accuracy = metrics["complete_accuracy"]
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "blank_tens": BLANK_TENS,
                    "image_size": 64,
                    "grayscale": True,
                    "best_validation_accuracy": best_accuracy,
                },
                output_path,
            )
            print("New best model saved")

    print(f"Best complete-number accuracy: {best_accuracy:.1%}")
    print(f"Best model saved to: {output_path}")


if __name__ == "__main__":
    main()
