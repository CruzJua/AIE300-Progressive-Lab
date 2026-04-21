# L1 Project Kickoff

A simple FastAPI CRUD application for managing an inventory of items.

## Installation

To install the project dependencies, run the following command:

```bash
pip install -r requirements.txt
```

## Running the Server

To start the FastAPI application with live reloading, run:

```bash
uvicorn main:app --reload
```

## Available Endpoints

The following endpoints are available:

- `GET /items`: Retrieve a list of all items.
- `GET /items/{item_id}`: Retrieve a specific item by its ID.
- `POST /items`: Create a new item.
- `PUT /items/{item_id}`: Update an existing item by its ID.
- `DELETE /items/{item_id}`: Delete an item by its ID.

# Lab 2 questions

- Which database you chose and why?
    - I chose MongoDB because I am familliar with it and we have not really been told what data we are planning to house for this project. Assuming the data will be used by some AI model we are training I figured that a flexiable document database would be a good idea.
- Docker setup instructions — how to start the app with docker-compose up --build
    - While in the root of the project use the command "docker-compose up --build -d"
- Architecture diagram — ASCII art or a simple text description showing how the frontend, backend, and database fit together
    - The frontend loads from a basic html/css/js group and uses js fetches to call the backend. The backend send the data it gets from the DAL up to the frontend where the user is shown the data using js. the DAL connects the backend to the database by providing functions that communicate with the database.