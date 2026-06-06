from fastapi import FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from mongoDAL import MongoDAL
import requests
import anthropic
from dotenv import load_dotenv
import os
import json
from agent_tools import AGENT_TOOLS, add_items, find_item, predict_iris_species, naturally_delete_item

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

class AnalyzeRequest(BaseModel):
    content: str # e.g., item descriptions, user text, etc.

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


class AgentRequest(BaseModel):
    messages: List[Dict[str, Any]] = []
    task: str

class AgentResponse(BaseModel):
    status: str
    result: Optional[str] = None
    steps: List[Dict[str, Any]] = []
    tool_call_to_confirm: Optional[Dict[str, Any]] = None
    messages: List[Dict[str, Any]] = []

@app.post("/agent", response_model=AgentResponse)
async def agent(request: AgentRequest):
    max_steps = 10
    messages = list(request.messages)
    steps_tracked = []

    # This for loop was main entirly by Claude 
    for msg in messages:
        if msg.get("role") != "user":
            continue
        content = msg.get("content", [])
        if not isinstance(content, list):
            continue
        for block in content:
            if (isinstance(block, dict) and
                    block.get("type") == "tool_result" and
                    "User confirmed" in str(block.get("content", ""))):
                # Find the matching tool_use block in the conversation
                tool_use_id = block.get("tool_use_id")
                for prev_msg in messages:
                    if prev_msg.get("role") != "assistant":
                        continue
                    for prev_block in (prev_msg.get("content") or []):
                        if (isinstance(prev_block, dict) and
                                prev_block.get("type") == "tool_use" and
                                prev_block.get("id") == tool_use_id):
                            tool_name = prev_block["name"]
                            tool_input = prev_block["input"]
                            real_output = ""
                            try:
                                if tool_name == "add_items":
                                    real_output = str(add_items(**tool_input))
                                elif tool_name == "naturally_delete_item":
                                    real_output = str(naturally_delete_item(**tool_input))
                            except Exception as e:
                                real_output = f"Error executing tool: {e}"
                            # Replace the placeholder with the real output
                            block["content"] = real_output
                            steps_tracked.append({
                                "tool": tool_name,
                                "input": tool_input,
                                "output": real_output
                            })

    if not messages:
        messages.append({"role": "user", "content": request.task})

    for i in range(max_steps):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                messages=messages,
                system=(
                    "You are a helpful assistant that manages items/iris storage as well as iris predictions. "
                    "When you complete a task, summarize the outcome in one or two plain sentences. "
                    "Never return raw JSON, object dumps, or lists of key-value pairs in your final answer. "
                    "Describe what was found, added, or deleted in natural language."
                ),
                max_tokens=1024,
                tools=AGENT_TOOLS
            )
            messages.append({"role": "assistant", "content": response.content})
            tool_calls = [section for section in response.content if section.type == "tool_use"]

            if not tool_calls:
                message_sections = [section.text for section in response.content if section.type == "text"]
                return AgentResponse(
                    status="complete",
                    result="".join(message_sections),
                    steps=steps_tracked,
                    messages=[  # I had Cluade help with this
                        {
                            "role": m["role"],
                            "content": [b.model_dump(exclude_none=True) for b in m["content"]]
                            if isinstance(m["content"], list) and hasattr(m["content"][0], "model_dump")
                            else m["content"]
                        }
                            for m in messages
                        ]
                )
            
            tool_results = []
            
            for tool_call in tool_calls:
                if tool_call.name in ["add_items", "naturally_delete_item"] and not request.messages: 
                    return AgentResponse(
                        status="requires_confirmation",
                        tool_call_to_confirm={"id": tool_call.id, "name": tool_call.name, "input": tool_call.input},
                        steps=steps_tracked,
                        messages=[
                            {
                                "role": m["role"],
                                "content": [b.model_dump(exclude_none=True) for b in m["content"]]
                                if isinstance(m["content"], list) and m["content"] and hasattr(m["content"][0], "model_dump")
                                else m["content"]
                            }
                            for m in messages
                        ]
                    )
                
                # Execute tool
                tool_output = ""
                try:
                    if tool_call.name == "find_item":
                        tool_output = str(find_item(**tool_call.input))
                    elif tool_call.name == "add_items":
                        tool_output = str(add_items(**tool_call.input))
                    elif tool_call.name == "predict_iris_species":
                        tool_output = str(predict_iris_species(**tool_call.input))
                    elif tool_call.name == "naturally_delete_item":
                        tool_output = str(naturally_delete_item(**tool_call.input))
                    else:
                        tool_output = f"Unknown tool: {tool_call.name}"
                except Exception as e:
                    tool_output = f"Error executing tool: {str(e)}"
                
                # Record trace
                steps_tracked.append({
                    "tool": tool_call.name,
                    "input": tool_call.input,
                    "output": tool_output
                })
                
                # Append result for next turn
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_call.id,
                    "content": tool_output
                })
                
            messages.append({"role": "user", "content": tool_results})
            
        except Exception as e:
             return AgentResponse(status="error", result=str(e), steps=steps_tracked)
             
    return AgentResponse(status="error", result="Step limit reached (Max Iterations Guardrail).", steps=steps_tracked)

    

@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    system_prompt = """You are a data analysis assistant. Analyze the provided content
and respond with ONLY valid JSON in this exact format:
{
  "categories": ["category1", "category2"],
  "tags": ["tag1", "tag2", "tag3"],
  "sentiment": "positive" | "negative" | "neutral",
  "summary": "one sentence summary"
}
Do not include any text outside the JSON object."""

    # Few-shot example in the prompt
    few_shot = """Example:
Input: "The new laptop is incredibly fast and the battery lasts all day. Best purchase this year."
Output: {"categories": ["technology", "review"], "tags": ["laptop", "performance", "battery"], "sentiment": "positive", "summary": "Highly positive review praising laptop speed and battery life."}"""

    messages = [
        {"role": "user", "content": few_shot + "\n\nNow analyze this:\n" + request.content}
    ]

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            messages=messages,
            system=system_prompt,
            max_tokens=512,
            temperature=0.2  # Low temperature for consistent structured output
        )
        raw = response.content[0].text

        # Parse and validate JSON
        result = json.loads(raw)

        # Validate expected fields exist
        required = ["categories", "tags", "sentiment", "summary"]
        for field in required:
            if field not in result:
                raise ValueError(f"Missing field: {field}")

        return result

    except json.JSONDecodeError:
        # Retry once or return fallback
        raise HTTPException(status_code=422, detail="LLM returned invalid JSON. Try again.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    system_prompt = (
        "You are a helpful assistant for a simple class assignment website that allows for creation and storing of Items "
        "({name: string, description: string}) and iris flower predictions from sepal and petal measurements. "
        "IMPORTANT: You cannot perform actions yourself in this chat mode. If the user asks to add, delete, or search items, "
        "or to predict an iris species, tell them to switch to the 'Agent' tab in the chat widget to perform those actions. "
        "Be concise and helpful."
    )

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
