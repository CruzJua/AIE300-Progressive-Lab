import os
from pymongo import MongoClient
from bson.objectid import ObjectId

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

class MongoDAL:
    def __init__(self):
        self.client = MongoClient(MONGO_URL)
        self.db = self.client["progressivelab"]
        self.items = self.db["items"]

    def _map_mongo_item(self, doc):
        if doc:
            doc["id"] = str(doc.pop("_id"))
        return doc

    def get_items(self):
        docs = list(self.items.find())
        return [self._map_mongo_item(doc) for doc in docs]

    def get_item(self, item_id: str):
        try:
            doc = self.items.find_one({"_id": ObjectId(item_id)})
            return self._map_mongo_item(doc)
        except:
            return None
    
    def search_items(self, keyword: str):
        try:
            regex_query = {"$regex": keyword, "$options": "i"}
            
            query = {
                "$or": [
                    {"name": regex_query},
                    {"description": regex_query}
                ]
            }
            
            docs = list(self.items.find(query))
            return [self._map_mongo_item(doc) for doc in docs]
        except Exception as e:
            print(f"Error searching items: {e}")
            return []

    def create_item(self, item_dict: dict) -> str:
        result = self.items.insert_one(item_dict)
        return str(result.inserted_id)

    def update_item(self, item_id: str, item_dict: dict):
        try:
            return self.items.update_one({"_id": ObjectId(item_id)}, {"$set": item_dict})
        except:
            return None

    def delete_item(self, item_id: str):
        try:
            return self.items.delete_one({"_id": ObjectId(item_id)})
        except:
            return None