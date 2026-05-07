from fastapi import FastAPI
import torch
import numpy as np

app = FastAPI()

# Load model at startup
model = None

@app.on_event("startup")
def load_model():
    global model
    model = torch.load("model/my_model.pt")  # or keras.models.load_model(...)
    model.eval()

@app.get("/health")
def health():
    return {"status": "healthy", "model_loaded": model is not None}

@app.post("/predict")
def predict(data: dict):
    # Convert input to tensor, run prediction, return result
    input_data = np.array(data["features"])
    features = torch.tensor(input_data, dtype=torch.float32)

    with torch.no_grad():
        result = model(features)
    
    return {"prediction": result, "model": "your-model-v1"}