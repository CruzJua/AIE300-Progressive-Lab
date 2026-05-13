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
    description: Optional[str] = None
    id: Optional[str] = None

    def __str__(self):
        return f"Item: {self.name}\nDescription: {self.description}"

class Iris(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

    def __str__(self):
        return f"Iris: {self.sepal_length}, {self.sepal_width}, {self.petal_length}, {self.petal_width}"

    def to_list(self) -> list[float]:
        return [self.sepal_length, self.sepal_width, self.petal_length, self.petal_width]


@app.get("/items")
def get_items():
    items = dal.get_items()
    return items
    

@app.get("/items/{item_id}")
def get_item(item_id: str):
    item = dal.get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.post("/items", status_code=status.HTTP_201_CREATED)
def create_item(item: Item):
    item_dict = item.model_dump(exclude={"id"})
    item_id = dal.create_item(item_dict)
    item.id = item_id
    return item


@app.post("/predict")
def predict(iris: Iris):
    response = requests.post(
        "http://model-service:8001/predict",
        json={"features": iris.to_list()}
    )
    result = response.json()
    item = Item(
        name=result["prediction"],
        description=f"This is an {result['prediction']} that was predicted with {result['confidence']*100}% confidence."
    )
    item_id = dal.create_item(item.model_dump(exclude={"id"}))
    item.id = item_id
    return item

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
