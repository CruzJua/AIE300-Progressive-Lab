from fastapi import FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from mongoDAL import MongoDAL
import requests
import anthropic
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
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


class ChatRequest(BaseModel):
    message: str
    conversation_history: list = []

class ChatResponse(BaseModel):
    reply: str
    conversation_history: list

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    system_prompt = "You are a helpful assistant for a simple class assignment website that allows for creation and storing of Items ({name: string, description: string}) and iris flower predictions from sepal and petal measurements. Be concise and helpful."

    messages = list(request.conversation_history)
    messages.append({"role": "user", "content": request.message})

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            system=system_prompt,
            messages=messages,
            max_tokens=512,
            temperature=0.7
        )
        reply = response.content[0].text

        # Return updated history so the frontend can send it back
        updated_history = request.conversation_history + [
            {"role": "user", "content": request.message},
            {"role": "assistant", "content": reply}
        ]
        return ChatResponse(reply=reply, conversation_history=updated_history)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
