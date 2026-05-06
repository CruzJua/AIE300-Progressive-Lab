# 📦 AIE300 Progressive Lab

A full-stack **CRUD inventory management** application built with **FastAPI**, **MongoDB**, and a vanilla **HTML/CSS/JS** frontend — fully containerized with **Docker Compose**.

Also features an **Iris species classifier** — a PyTorch neural network trained on the classic Iris dataset and served via a REST endpoint, with predictions displayed directly in the UI.

---

## 🚀 Quick Start

### Prerequisites

- [Docker](https://www.docker.com/get-started) & Docker Compose installed

### Run with Docker Compose

```bash
docker-compose up --build -d
```

| Service  | URL                          |
|----------|------------------------------|
| Frontend | http://localhost              |
| Backend  | http://localhost:8000        |
| API Docs | http://localhost:8000/docs   |
| MongoDB  | `mongodb://localhost:27017`  |

### Stop the App

```bash
docker-compose down
```

---

## 🛠️ Local Development (without Docker)

### 1. Install Dependencies

```bash
cd api
pip install -r requirements.txt
```

### 2. Start the API Server

```bash
uvicorn main:app --reload
```

The server will be available at `http://localhost:8000`.

---

## 📡 API Endpoints

### Items (CRUD)

| Method   | Endpoint            | Description                      |
|----------|---------------------|----------------------------------|
| `GET`    | `/items`            | Retrieve all items               |
| `GET`    | `/items/{item_id}`  | Retrieve a specific item by ID   |
| `POST`   | `/items`            | Create a new item                |
| `PUT`    | `/items/{item_id}`  | Update an existing item by ID    |
| `DELETE` | `/items/{item_id}`  | Delete an item by ID             |

#### Item Schema

```json
{
  "name": "string (required)",
  "description": "string (optional)",
  "id": "string (auto-generated)"
}
```

### ML Model (Iris Classifier)

| Method | Endpoint   | Description                                      |
|--------|------------|--------------------------------------------------|
| `POST` | `/predict` | Classify an Iris flower and return a confidence score |

#### Prediction Request

```json
{
  "features": [5.1, 3.5, 1.4, 0.2]
}
```

> Fields are `[sepal_length, sepal_width, petal_length, petal_width]` in centimeters.

#### Prediction Response

```json
{
  "prediction": "Iris-setosa",
  "confidence": 0.98
}
```

---

## 📁 Project Structure

```
ProgressiveLab/
├── api/
│   ├── Dockerfile          # Backend container config
│   ├── main.py             # FastAPI application & routes (items + /predict)
│   ├── mongoDAL.py         # MongoDB Data Access Layer
│   ├── pytorch_basics.py   # SimpleClassifier model definition & training script
│   ├── model.pth           # Saved Iris classifier weights (torch.save)
│   ├── requirements.txt    # Python dependencies
│   └── .env                # Environment variables
├── frontend/
│   ├── Dockerfile          # Frontend container config (Nginx)
│   ├── index.html          # Main HTML page (items + Iris prediction form)
│   ├── css/                # Stylesheets
│   └── js/                 # Client-side JavaScript
├── docker-compose.yml      # Multi-service orchestration
└── README.md
```

---

## 🤖 Iris Classification Model

The app includes a feed-forward neural network trained on the [Iris dataset](https://scikit-learn.org/stable/auto_examples/datasets/plot_iris_dataset.html) to classify flowers into one of three species:

- **Iris-setosa**
- **Iris-versicolor**
- **Iris-virginica**

### Architecture

| Layer   | Details                        |
|---------|--------------------------------|
| Input   | 4 features (sepal/petal dims)  |
| Hidden  | Linear(4 → 16) + ReLU         |
| Output  | Linear(16 → 3) — 3 classes    |

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

The updated `model.pth` will be picked up automatically on the next container restart.

---

## 📝 Lab 2 — Questions & Answers

### Which database did you choose and why?

I chose **MongoDB** because I am familiar with it and we have not been told what data we are planning to house for this project. Assuming the data will be used by some AI model we are training, I figured that a **flexible document database** would be a good idea — it allows the schema to evolve without requiring migrations.

### Docker setup instructions

While in the root of the project, run:

```bash
docker-compose up --build -d
```

This builds all three services (frontend, backend, and database) and starts them in detached mode.

### Architecture overview

> **Frontend → Backend → DAL → Database**

The frontend loads from a basic HTML/CSS/JS stack and uses JavaScript `fetch()` calls to hit the backend API. The backend sends the data it receives from the DAL up to the frontend, where the user is shown the data dynamically via JS. The DAL connects the backend to the database by providing functions that abstract all MongoDB operations.