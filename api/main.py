from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from mongoDAL import MongoDAL
import torch
from pytorch_basics import SimpleClassifier

app = FastAPI()
dal = MongoDAL()

model = SimpleClassifier(input_size=4, hidden_size=16, num_classes=3)
model.load_state_dict(torch.load("model.pth"))
model.eval()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Item(BaseModel):
    name: str
    id: Optional[str] = None
    description: Optional[str] = None

    def __str__(self):
        return f"Item: {self.name}\nDescription: {self.description}"

class PredictionRequest(BaseModel):
    features: list[float]

# In-memory storage
items_db: dict[int, Item] = {}
next_id: int = 0


@app.get("/items")
def get_items() -> list[Item]:
    items = dal.get_items()
    return items
    

@app.get("/items/{item_id}")
def get_item(item_id: str):
    item = dal.get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.post("/items")
def create_item(item: Item):
    item_dict = item.model_dump(exclude={"id"})
    item_id = dal.create_item(item_dict)
    item.id = item_id
    return item

@app.post("/predict")
def predict(req: PredictionRequest):
    # 1. Convert input to tensor
    # 2. Run inference (model.eval(), torch.no_grad())
    # 3. Return prediction as JSON
    features = torch.tensor(req.features, dtype=torch.float32)
    response: dict[str, any] = {}
    classNames = ["Iris-setosa", "Iris-versicolor", "Iris-virginica"]

    with torch.no_grad():
        output = model(features)
        probabilities = torch.softmax(output, dim=0)
        confidence, predicted = torch.max(probabilities, 0)
        response["prediction"] = classNames[predicted.item()]
        response["confidence"] = round(confidence.item(), 2)
    return response

@app.put("/items/{item_id}")
def update_item(item_id: str, item: Item):
    if dal.get_item(item_id) is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item_dict = item.model_dump(exclude={"id"})
    dal.update_item(item_id, item_dict)
    item.id = item_id
    return item
    

@app.delete("/items/{item_id}")
def delete_item(item_id: str):
    if dal.get_item(item_id) is None:
        raise HTTPException(status_code=404, detail="Item not found")
    dal.delete_item(item_id)
    return {"message": "Item deleted successfully"}


# Run with: uvicorn main:app --reload
