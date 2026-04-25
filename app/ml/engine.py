from app.utils.file_converter import FileConverter
import os
import onnxruntime as ort
import numpy as np


MODEL_PATH = "app/ml/Modelv2.onnx"

# Lazy loading model session
_ort_session = None

def get_ort_session():
    global _ort_session
    if _ort_session is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
        _ort_session = ort.InferenceSession(MODEL_PATH)
    return _ort_session

def extract_features(file_path: str) -> np.ndarray:
    
    with open(file_path, "rb") as f:
        file_bytes = f.read()
        
    image = FileConverter.bytes_to_image(file_bytes)
    
    # Resize the image to fixed size 224x224 required by the model
    image = image.resize((224, 224))
    
    # Convert grayscale to RGB to get 3 channels
    image = image.convert("RGB")
    
    # Create numpy array, shape will be (224, 224, 3)
    arr = np.array(image, dtype=np.float32)
    
    # Transpose to (channels, height, width) -> (3, 224, 224)
    arr = np.transpose(arr, (2, 0, 1))
    
    # Norm to [0, 1]
    arr = arr / 255.0
    
    # Add batch dimension -> (1, 3, 224, 224)
    arr = np.expand_dims(arr, axis=0)
    return arr
