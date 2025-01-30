import torch
from torchvision import models, transforms
from PIL import Image
import json
import pandas as pd
import os
import kagglehub
from pathlib import Path
from torchvision.models import ResNet18_Weights
import re

# Define image folder path
image_folder = f"{Path(__file__).resolve().parent.parent}/images/fish"
# Initialize list to store dataset entries
dataset = []

# Download latest version
path = kagglehub.dataset_download("tusonggao/imagenet-labels")

# Load ImageNet labels
with open(f"{path}/imagenet_labels.json", "r") as f:
    imagenet_classes = json.load(f)

# Load pretrained model (Resnet)
model = models.resnet18(weights=ResNet18_Weights.DEFAULT)
model.eval()

# Image preprocessing
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

import re

# Function to sort filenames naturally (e.g., fish_2 before fish_10)
def natural_sort_key(filename):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', filename)]

# List and sort images naturally
image_files = sorted(os.listdir(image_folder), key=natural_sort_key)


# Iterate through images
for img_id, image_file in enumerate(image_files):
    image_path = os.path.join(image_folder, image_file)
    
    # Load and preprocess image
    img = Image.open(image_path).convert("RGB")
    img_tensor = preprocess(img).unsqueeze(0)  # Add batch dimension
    
    # Get model predictions
    with torch.no_grad():
        outputs = model(img_tensor)
        _, predicted_idx = torch.max(outputs, 1)
        predicted_class = predicted_idx.item()
    
    # Get class label
    predicted_label = imagenet_classes[str(predicted_class)]  # Convert ID to label
    
    # Append to dataset
    dataset.append([img_id, image_file, predicted_label])

# Convert to DataFrame
df = pd.DataFrame(dataset, columns=["id", "img", "label"])

# Save dataset
df.to_csv("labeled_dataset.csv", index=False)

print("Dataset saved as labeled_dataset.csv")

