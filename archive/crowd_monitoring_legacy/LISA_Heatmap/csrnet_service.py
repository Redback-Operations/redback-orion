import io
from typing import Optional, Tuple

import numpy as np
import torch
from PIL import Image
from torchvision import transforms

from csrnet.model import CSRNet


class CSRNetService:
    """CSRNet inference wrapper with optional mask application.

    If a boolean mask is provided (H, W), the input image will be multiplied by the mask
    before running through the network, focusing the density on the masked area.
    """

    def __init__(self, weights_path: str = "/home/s223915978/LISA/csrnet/weights.pth", device: str = "cpu"):
        self.device = torch.device(device)
        self.model = CSRNet().to(self.device)
        checkpoint = torch.load(weights_path, map_location=self.device)
        self.model.load_state_dict(checkpoint)
        self.model.eval()

        self.transform = transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ]
        )

    @torch.no_grad()
    def infer(self, image: Image.Image, mask: Optional[np.ndarray] = None) -> Tuple[np.ndarray, float]:
        """
        Returns density map (H', W') as numpy float32 and estimated count as float.
        If mask is provided, it should be a boolean array matching the input image size (H, W).
        """
        img_np = np.array(image).astype(np.float32)
        if mask is not None:
            if mask.shape[:2] != img_np.shape[:2]:
                mask = np.array(Image.fromarray(mask.astype(np.uint8) * 255).resize((img_np.shape[1], img_np.shape[0]), Image.NEAREST)) > 0
            # Apply mask by zeroing non-masked pixels
            img_np = img_np * mask[..., None].astype(np.float32)

        img_tensor = self.transform(Image.fromarray(img_np.astype(np.uint8)).convert("RGB"))
        img_tensor = img_tensor.unsqueeze(0).to(self.device)

        output = self.model(img_tensor)
        density_map = output.detach().cpu().squeeze(0).squeeze(0).numpy().astype(np.float32)
        count = float(output.detach().cpu().sum().item())
        return density_map, count


