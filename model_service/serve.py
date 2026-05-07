from fastapi import FastAPI
import torch
import numpy as np

app = FastAPI()

# Load model at startup
model = None

@app.on_event("startup")
def load_model():
    global model
    model = torch.load("./model/model.pth")
    model.eval()

@app.get("/health")
def health():
    return {"status": "healthy", "model_loaded": model is not None}

@app.post("/predict")
def predict(data: dict):
    # Convert input to tensor, run prediction, return result
    features = torch.tensor(data.features, dtype=torch.float32)
    response: dict[str, any] = {}
    classNames = ["Iris-setosa", "Iris-versicolor", "Iris-virginica"]

    with torch.no_grad():
        output = model(features)
        probabilities = torch.softmax(output, dim=0)
        confidence, predicted = torch.max(probabilities, 0)
        response["prediction"] = classNames[predicted.item()]
        response["confidence"] = round(confidence.item(), 2)
        response["model"] = "Iris-classifier-v1"
    return response