from mongoDAL import MongoDAL
from bson.objectid import ObjectId
import requests
from typing import Literal

AGENT_TOOLS = [
    {
        "name": "add_items",
        "description": "Adds items to the database",
        "input_schema": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"}
                        },
                        "required": ["name"]
                    }
                }
            },
            "required": ["items"]
        }
    },
    {
        "name": "find_item",
        "description": "Finds items in the database",
        "input_schema": {
            "type": "object",
            "properties": {
                "search_term": {
                    "type": "string",
                    "description": "The exact name, keyword, or description to search for"
                }
            },
            "required": ["search_term"]
        }
    },
    {
        "name": "predict_iris_species",
        "description": "Predicts the species of an Iris flower based on its measurements",
        "input_schema": {
            "type": "object",
            "properties": {
                "sepal_length": {"type": "number"},
                "sepal_width": {"type": "number"},
                "petal_length": {"type": "number"},
                "petal_width": {"type": "number"}
            },
            "required": ["sepal_length", "sepal_width", "petal_length", "petal_width"]
        }
    },
    {
        "name": "naturally_delete_item",
        "description": "Deletes all items matching any of the provided search terms. Pass multiple terms to catch variations, synonyms, or a list the user specified.",
        "input_schema": {
            "type": "object",
            "properties": {
                "search_terms": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "One or more keywords. Each term is searched independently; all matching items across all terms are deleted."
                }
            },
            "required": ["search_terms"]
        }
    }
]

def add_items(items: list[dict[str, any]]):
    """Adds items to the database"""
    for item in items:
        item_to_insert = dict(item)
        if "_id" in item_to_insert:
            item_to_insert["_id"] = ObjectId(item_to_insert["_id"])
        MongoDAL().create_item(item_to_insert)

def find_item(search_term: str):
    found = MongoDAL().search_items(search_term)
    return found

 
# predict_iris_species
def predict_iris_species(sepal_length: float, sepal_width: float, petal_length: float, petal_width: float) -> str:
    """
    Predicts the species of an Iris flower and saves the result as an item.
    """
    try:
        response = requests.post(
            "http://model-service:8001/predict",
            json={"features": [sepal_length, sepal_width, petal_length, petal_width]}
        )
        if response.status_code != 200:
            return f"Model service returned status {response.status_code}"
        result = response.json()
        prediction = result.get("prediction", "Unknown")
        confidence = result.get("confidence", 0) * 100
        item = {
            "name": prediction,
            "description": f"This is an {prediction} predicted with {confidence:.1f}% confidence."
        }
        MongoDAL().create_item(item)
        return f"Predicted {prediction} with {confidence:.1f}% confidence. Item saved to database."
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to the model service."
    except Exception as e:
        return f"Error calling prediction service: {e}"


# delete_item
def naturally_delete_item(search_terms: list[str]):
    """
    Searches for items matching each term in the list and deletes all matches.
    Deduplicates so the same item is not deleted twice even if it matches
    multiple terms.
    """
    dal = MongoDAL()
    seen_ids = set()
    items_to_delete = []

    for term in search_terms:
        for item in dal.search_items(term):
            if item["id"] not in seen_ids:
                seen_ids.add(item["id"])
                items_to_delete.append(item)

    if not items_to_delete:
        return f"No items found matching any of: {', '.join(search_terms)}"

    deleted_names = []
    for item in items_to_delete:
        dal.delete_item(item["id"])
        deleted_names.append(item["name"])

    return f"Successfully deleted: {', '.join(deleted_names)}."
