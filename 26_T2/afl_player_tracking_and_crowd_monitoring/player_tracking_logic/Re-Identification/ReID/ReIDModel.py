import cv2 
import numpy as np
import torch
import torch.nn 
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import cosine
import torchreid
from PIL import Image
import torchvision.transforms.v2 as T
class ReIDModel:
    """
    Act as a wrapper to load pretrained ReID model
    Converts player image crops into embedding vectors.
    
    Input:
        - model_name (str): name of pretrained ReID model to load, default is 'osnet_x1_0'
        - device (str): 'cude' or 'cpu'
    Output: 
        - embedding vector (np.array) feature per player representing player appearance
    """
    def __init__(self,model_name='osnet_x1_0', device='cuda'):
        self.device = device if device else ('cuda' if torch.cuda.is_available() else 'cpu')
        
        #Load pretrained OSNet
        self.model = torchreid.models.build_model(
            name = model_name,
            num_classes = 1000,
            pretrained = True,
        )
        self.model.eval()
        self.model = self.model.half()
        self.model.to(self.device)
        
        # Transform
        self.transform = T.Compose([
            T.Resize((256,128)),
            T.ToDtype(torch.float32, scale=True),           # normalize [0,255] → [0,1]
            T.Normalize(mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225]),
        ])

    # Old method inefficient 
    def extract_embedding(self,image):
        """
        Extract embedding vector from player crop image
            - Converts OpenCV image (np) to PIL Image
            - Apply normalization + resize
            - Pass through ReID model
            - Return embedding vector

        Input:
            - image (np.array): cropped player image
        Output:
            - embedding vector (np.array) feature per player representing player appearance
        """
        # Handle empty crop
        if image is None or image.size ==0:
            return None
        
        #convet BGR to RGB
        image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        # Convert Numpy -> PIL
        image = Image.fromarray(image)
        
        #Apply Transforms to batch tensor
        image = self.transform(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            features = self.model(image)
        
        embedding = features.cpu().numpy().flatten()
        #Normalize
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding
    
    def extract_embeddings_batch(self, crops):
        """
        Extract embeddings from multiple player crops in batch
            - Converts list of NumPy images → Torch tensors
            - Applies transforms on GPU
            - Runs batch inference
            - Returns embeddings for all players

        Input:
            - crops: list of NumPy arrays (BGR images)

        Output:
            - embeddings: list of numpy vectors
        """

        valid_tensors = []

        for crop in crops:
            # Handle empty crop
            if crop is None or crop.size == 0:
                continue

            # Convert BGR → RGB
            #crop = crop[:, :, ::-1].copy()
            crop = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
            
            # NumPy → Tensor (C,H,W)
            tensor = torch.from_numpy(crop).permute(2, 0, 1).contiguous()
            
            #Resize to ReID expected size (H = 256, W=128)
            tensor = torch.nn.functional.interpolate(
                tensor.unsqueeze(0).float(),
                size=(256,128),
                mode='bilinear',
                align_corners=False
            ).squeeze(0)
            
            valid_tensors.append(tensor)

        if len(valid_tensors) == 0:
            return []

        # Stack batch
        batch = torch.stack(valid_tensors).to(self.device)
        batch = batch.to(self.device,non_blocking=True)
        
        # Apply transforms
        batch = self.transform(batch)
         # Normalize (manual instead of torchvision overhead)
        # batch = batch / 255.0
        # mean = torch.tensor([0.485, 0.456, 0.406], device=self.device).view(1,3,1,1)
        # std = torch.tensor([0.229, 0.224, 0.225], device=self.device).view(1,3,1,1)
        # batch = (batch - mean) / std

        # Half precision
        batch = batch.half()

        with torch.no_grad():
            features = self.model(batch)

        # Convert to numpy
        embeddings = features.float().cpu().numpy()
        #Normalize
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

        return embeddings