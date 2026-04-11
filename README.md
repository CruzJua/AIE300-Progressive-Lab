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
