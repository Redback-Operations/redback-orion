import h5py
import scipy.io as io
import PIL.Image as Image
import numpy as np
from matplotlib import pyplot as plt, cm as c
from scipy.ndimage.filters import gaussian_filter 
import scipy
import torchvision.transforms.functional as F
from model import CSRNet
import torch
from torchvision import transforms
import time



transform=transforms.Compose([
                       transforms.ToTensor(),transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225]),
                   ])

model = CSRNet()

checkpoint = torch.load('weights.pth', map_location="cpu")
model.load_state_dict(checkpoint)

img_path = "/home/s223915978/LISA/afl_test_frame.png"

print("Original Image")
plt.imshow(plt.imread(img_path))
plt.show()

start_time = time.time()
img = transform(Image.open(img_path).convert('RGB'))
output = model(img.unsqueeze(0))
end_time = time.time()
print(f"Time taken: {end_time - start_time} seconds")
print("Predicted Count : ",int(output.detach().cpu().sum().numpy()))
temp = np.asarray(output.detach().cpu().reshape(output.detach().cpu().shape[2],output.detach().cpu().shape[3]))
# plt.imshow(temp,cmap = c.jet)
# Add text annotation for predicted count


# Save heatmap visualization
plt.figure(figsize=(10,10))
plt.imshow(temp, cmap=c.jet)
plt.colorbar()
plt.title("Density Map")

save_path = img_path.replace(".jpg", "_heatmap.jpg")
plt.text(0, 0, f'Count: {int(output.detach().cpu().sum().numpy())}', 
         color='white', fontsize=12, bbox=dict(facecolor='black', alpha=0.7))

plt.savefig(save_path)
plt.close()
print(f"Heatmap saved to: {save_path}")
