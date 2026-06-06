# AIE300 Progressive Lab

A full-stack **CRUD inventory management** application built with **FastAPI**,
**MongoDB**, and a vanilla **HTML/CSS/JS** frontend — fully containerized with
**Docker Compose**.

Also features an **Iris species classifier** — a PyTorch neural network trained
on the classic Iris dataset and served via a REST endpoint, with predictions
displayed directly in the UI.

In later labs, an **LLM-powered chat assistant** (via the Anthropic API) and a
**content analysis endpoint** were added, enabling natural-language interaction
and structured AI-driven text analysis within the same application.

---

## Quick Start

### Prerequisites

- [Docker](https://www.docker.com/get-started) & Docker Compose installed

### Run with Docker Compose

```bash
docker-compose up --build -d
```

| Service  | URL                         |
| -------- | --------------------------- |
| Frontend | http://localhost            |
| Backend  | http://localhost:8000       |
| API Docs | http://localhost:8000/docs  |
| MongoDB  | `mongodb://localhost:27017` |

### Stop the App

```bash
docker-compose down
```

---

## Local Development (without Docker)

### 1. Configure Environment Variables

Copy the example file and fill in your credentials:

```bash
cp api/.env.example api/.env
```

```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
MONGO_URI=your_mongodb_connection_string_here
```

### 2. Install Dependencies

```bash
cd api
pip install -r requirements.txt
```

### 3. Start the API Server

```bash
uvicorn main:app --reload
```

The server will be available at `http://localhost:8000`.

---

## API Endpoints

### Items (CRUD)

| Method   | Endpoint           | Description                    |
| -------- | ------------------ | ------------------------------ |
| `GET`    | `/items`           | Retrieve all items             |
| `GET`    | `/items/{item_id}` | Retrieve a specific item by ID |
| `POST`   | `/items`           | Create a new item              |
| `PUT`    | `/items/{item_id}` | Update an existing item by ID  |
| `DELETE` | `/items/{item_id}` | Delete an item by ID           |

#### Item Schema

```json
{
  "name": "string (required)",
  "description": "string (optional)",
  "id": "string (auto-generated)"
}
```

### ML Model (Iris Classifier)

| Method | Endpoint   | Description                                           |
| ------ | ---------- | ----------------------------------------------------- |
| `POST` | `/predict` | Classify an Iris flower and return a confidence score |

#### Prediction Request

```json
{
  "sepal_length": 5.1,
  "sepal_width": 3.5,
  "petal_length": 1.4,
  "petal_width": 0.2
}
```

> Fields represent `[sepal_length, sepal_width, petal_length, petal_width]` in
> centimeters.

#### Prediction Response

```json
{
  "prediction": "Iris-setosa",
  "confidence": 0.98
}
```

A successful prediction is also automatically saved as an item in MongoDB.

### LLM Endpoints

| Method | Endpoint   | Description                                              |
| ------ | ---------- | -------------------------------------------------------- |
| `POST` | `/chat`    | Send a message and receive a conversational reply        |
| `POST` | `/analyze` | Analyze a text string and receive structured JSON output |

See the [Prompt Documentation](#prompt-documentation) section below for full
details on how these endpoints are prompted.

---

## Project Structure

```
ProgressiveLab/
├── api/
│   ├── Dockerfile          # Backend container config
│   ├── main.py             # FastAPI application & routes
│   ├── mongoDAL.py         # MongoDB Data Access Layer
│   ├── pytorch_basics.py   # SimpleClassifier model definition & training script
│   ├── model.pth           # Saved Iris classifier weights (torch.save)
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example        # Environment variable template
│   └── .env                # Local environment variables (not committed)
├── frontend/
│   ├── Dockerfile          # Frontend container config (Nginx)
│   ├── index.html          # Main HTML page
│   ├── css/                # Stylesheets
│   └── js/                 # Client-side JavaScript
├── model_service/          # PyTorch model inference service
├── docker-compose.yml      # Multi-service orchestration
└── README.md
```

---

## Iris Classification Model

The app includes a feed-forward neural network trained on the
[Iris dataset](https://scikit-learn.org/stable/auto_examples/datasets/plot_iris_dataset.html)
to classify flowers into one of three species:

- Iris-setosa
- Iris-versicolor
- Iris-virginica

### Architecture

| Layer  | Details                       |
| ------ | ----------------------------- |
| Input  | 4 features (sepal/petal dims) |
| Hidden | Linear(4 → 16) + ReLU         |
| Output | Linear(16 → 3) — 3 classes    |

### Training

- **Dataset split:** 80% train / 20% test via `random_split`
- **DataLoader:** batch size 32, shuffled
- **Loss function:** `CrossEntropyLoss`
- **Optimizer:** `Adam` (lr=0.01)
- **Epochs:** 50 (loss printed every 10)
- **Saved with:** `torch.save(model.state_dict(), 'model.pth')`

To retrain the model, run:

```bash
cd api
uv run python pytorch_basics.py
```

The updated `model.pth` will be picked up automatically on the next container
restart.

---

## Prompt Documentation

This section describes how the two LLM-powered endpoints (`/chat` and
`/analyze`) are designed — including their system messages, few-shot examples,
expected output formats, and how failures are handled.

### /chat — Conversational Assistant

**Model:** `claude-sonnet-4-6` (Anthropic)

#### System Message

```
You are a helpful assistant for a simple class assignment website that allows
for creation and storing of Items ({name: string, description: string}) and
iris flower predictions from sepal and petal measurements. Be concise and helpful.
```

The system message anchors the assistant to the specific context of this
application. It explicitly names the two primary features (item management and
Iris prediction) so the model can answer user questions about them accurately
without hallucinating unrelated functionality.

#### Conversation History

The endpoint accepts a `conversation_history` array alongside each new
`message`. The full history is forwarded to the Anthropic API on every request,
enabling multi-turn conversation. The backend appends the user's new message
before sending and returns an updated history for the frontend to store and send
back on the next turn.

```json
{
  "message": "What is an Iris flower?",
  "conversation_history": [
    { "role": "user", "content": "Hello" },
    { "role": "assistant", "content": "Hi! How can I help you?" }
  ]
}
```

#### Format Expectations

The response is free-form natural language. No structured output is enforced.
The reply is extracted from `response.content[0].text`.

#### Failure Handling

Any exception raised during the Anthropic API call is caught and re-raised as an
HTTP `500` error with the original exception message included in the detail
field.

---

### /analyze — Structured Content Analysis

**Model:** `claude-sonnet-4-6` via Anthropic client (originally configured for
`gpt-4o-mini`)

#### System Message

```
You are a data analysis assistant. Analyze the provided content and respond
with ONLY valid JSON in this exact format:
{
  "categories": ["category1", "category2"],
  "tags": ["tag1", "tag2", "tag3"],
  "sentiment": "positive" | "negative" | "neutral",
  "summary": "one sentence summary"
}
Do not include any text outside the JSON object.
```

The system message does two things: it defines the model's role and, critically,
enforces strict output formatting. By instructing the model to return **only** a
JSON object with no surrounding text, the response can be parsed directly
without any post-processing or stripping.

#### Few-Shot Example

A single few-shot example is prepended to the user content to demonstrate the
expected input/output mapping:

```
Example:
Input: "The new laptop is incredibly fast and the battery lasts all day. Best purchase this year."
Output: {"categories": ["technology", "review"], "tags": ["laptop", "performance", "battery"], "sentiment": "positive", "summary": "Highly positive review praising laptop speed and battery life."}
```

The example is embedded directly in the user message rather than as a separate
turn, keeping the message structure simple while still guiding output format
through demonstration.

#### Format Expectations

The response must be a valid JSON object containing all four of the following
fields:

| Field        | Type             | Description                                       |
| ------------ | ---------------- | ------------------------------------------------- |
| `categories` | array of strings | High-level topic categories for the content       |
| `tags`       | array of strings | Specific keywords extracted from the content      |
| `sentiment`  | string           | One of `"positive"`, `"negative"`, or `"neutral"` |
| `summary`    | string           | A single-sentence summary of the content          |

After the model responds, the backend validates that all four required fields
are present. If any field is missing, a `ValueError` is raised before the
response is returned.

#### Failure Handling

| Failure Mode               | Response                                                                     |
| -------------------------- | ---------------------------------------------------------------------------- |
| Model returns invalid JSON | `HTTP 422` — "LLM returned invalid JSON. Try again."                         |
| Missing required field     | `HTTP 422` — raised via `ValueError` caught in the general exception handler |
| Any other exception        | `HTTP 500` — original exception message in the detail field                  |

The low temperature setting (`0.2`) is intentional: it reduces variability in
the output and makes the model more likely to adhere strictly to the requested
JSON format on every call.

---

## Lab Questions & Answers

### Lab 2

**Which database did you choose and why?**

I chose **MongoDB** because I am familiar with it and we had not been told what
data we would be housing for this project. Assuming the data would be used by
some AI model we are training, I figured that a **flexible document database**
would be a good idea — it allows the schema to evolve without requiring
migrations.

**Docker setup instructions**

While in the root of the project, run:

```bash
docker-compose up --build -d
```

This builds all three services (frontend, backend, and database) and starts them
in detached mode.

**Architecture overview**

> Frontend → Backend → DAL → Database

The frontend loads from a basic HTML/CSS/JS stack and uses JavaScript `fetch()`
calls to hit the backend API. The backend sends the data it receives from the
DAL up to the frontend, where the user is shown the data dynamically via JS. The
DAL connects the backend to the database by providing functions that abstract
all MongoDB operations.

### Lab 3

**What model did you pull?**

I pulled the `smollm2:latest` model.

**What endpoints does it expose?**

`http://localhost:12434/engines/llama.cpp/v1/chat/completions`

**What was the response to your test query?**

Docker is an open-source project that provides an environment for running
different operating systems and applications as isolated containers.

---

_Portions of this project were developed with assistance from Claude Sonnet
(Anthropic)._

### Lab 8

# Agent Feature

## Architecture (Path A)

I choose path A becaue I really wanted to get a feel for how each step worked. I
didn't want to imidiatly just in and you external tools even is that 's
realistically the most optimal way or how I will do it in the future. It was
definetly a bit tricky but I think i learned a lot from it.

## Tools

1. **find_item**: Searches existing items in the database by executing the
   `find_item` function. This allows the user to have the a natural way to
   search for items.
2. **add_items**: Creates new items in the database by executing the `add_items`
   function. this just gets the agent to create a json contained the name and
   description of an item and pushing that tot he db.
3. **predict_iris_species**: Predicts the species of an Iris flower by passing
   measurements to the internal ML model service.
4. **naturally_delete_item**: Locates and deletes an item from the database.
   This just let the user filter through serach terms to remove itmes that are
   captured by said search terms.

## Guardrails

- **Max Iterations:** The agent loop is strictly capped at 10 iterations to
  prevent infinite loops.
- **Tool Confirmation:** Before destructive actions (`add_items` or
  `naturally_delete_item`) are allowed to execute, the loop pauses, returns a
  `requires_confirmation` status, and waits for explicit user permission via the
  UI.
- **Error Handling:** All tool executions are wrapped in `try/except` blocks. If
  an API call fails, the exception string is sent back to the model so it can
  gracefully recover.
