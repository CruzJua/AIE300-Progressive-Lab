# 📦 AIE300 Progressive Lab

A full-stack **CRUD inventory management** application built with **FastAPI**, **MongoDB**, and a vanilla **HTML/CSS/JS** frontend — fully containerized with **Docker Compose**.

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

| Method   | Endpoint            | Description                      |
|----------|---------------------|----------------------------------|
| `GET`    | `/items`            | Retrieve all items               |
| `GET`    | `/items/{item_id}`  | Retrieve a specific item by ID   |
| `POST`   | `/items`            | Create a new item                |
| `PUT`    | `/items/{item_id}`  | Update an existing item by ID    |
| `DELETE` | `/items/{item_id}`  | Delete an item by ID             |

### Item Schema

```json
{
  "name": "string (required)",
  "description": "string (optional)",
  "id": "string (auto-generated)"
}
```

---

## 📁 Project Structure

```
ProgressiveLab/
├── api/
│   ├── Dockerfile          # Backend container config
│   ├── main.py             # FastAPI application & routes
│   ├── mongoDAL.py         # MongoDB Data Access Layer
│   ├── requirements.txt    # Python dependencies
│   └── .env                # Environment variables
├── frontend/
│   ├── Dockerfile          # Frontend container config (Nginx)
│   ├── index.html          # Main HTML page
│   ├── css/                # Stylesheets
│   └── js/                 # Client-side JavaScript
├── docker-compose.yml      # Multi-service orchestration
└── README.md
```

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