from fastapi import FastAPI
from pydantic import BaseModel
import torch
import torch.nn as nn

app = FastAPI()

class PredictRequest(BaseModel):
    features: list[float]

class SimpleClassifier(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super().__init__()
        self.layer1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.layer2 = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        x = self.relu(self.layer1(x))
        x = self.layer2(x)
        return x

model = None

@app.on_event("startup")
def load_model():
    global model
    model = SimpleClassifier(input_size=4, hidden_size=16, num_classes=3)
    model.load_state_dict(torch.load("./model/model.pth", weights_only=True))
    model.eval()

@app.get("/health")
def health():
    return {"status": "healthy", "model_loaded": model is not None}

@app.post("/predict")
def predict(data: PredictRequest):
    features = torch.tensor(data.features, dtype=torch.float32)
    classNames = ["Iris-setosa", "Iris-versicolor", "Iris-virginica"]

    with torch.no_grad():
        output = model(features)
        probabilities = torch.softmax(output, dim=0)
        confidence, predicted = torch.max(probabilities, 0)

    return {
        "prediction": classNames[predicted.item()],
        "confidence": round(confidence.item(), 2),
        "model": "Iris-classifier-v1"
    }