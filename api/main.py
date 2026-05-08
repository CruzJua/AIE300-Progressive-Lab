from fastapi import FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from mongoDAL import MongoDAL
import requests

app = FastAPI()
dal = MongoDAL()

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
def create_item(item: Item, response: Response):
    item_dict = item.model_dump(exclude={"id"})
    item_id = dal.create_item(item_dict)
    item.id = item_id
    response.status_code = status.HTTP_201_CREATED
    return item


@app.post("/predict")
def predict(req: PredictionRequest):

    # Forward to model service instead of running locally
    response = requests.post(
        "http://model-service:8001/predict",
        json={"features": req.features}
    )
    return response.json()

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
