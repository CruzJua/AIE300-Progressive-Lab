import os
import sys
# Get the absolute path of the directory containing this script (testFiles)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory (api)
parent_dir = os.path.dirname(current_dir)
# Add the parent directory to Python's module search path
sys.path.append(parent_dir)
from mongoDAL import MongoDAL

def run_demo():
    dal = MongoDAL()
    
    # 1. Insert some test items if they don't exist
    test_items = [
        {"name": "Python Book", "description": "A comprehensive guide to learning Python coding."},
        {"name": "Apple MacBook Pro", "description": "Powerful laptop with Apple Silicon chip."},
        {"name": "Database Design Guide", "description": "Learn SQL and MongoDB fundamentals."},
        {"name": "Smart Thermostat", "description": "Control your home temperature with smart python scripts."}
    ]
    
    print("--- Inserting test items ---")
    for item in test_items:
        # Check if item name already exists to avoid duplicates
        existing = dal.search_items(item["name"])
        if not existing:
            inserted_id = dal.create_item(item)
            print(f"Inserted '{item['name']}' with ID: {inserted_id}")
        else:
            print(f"'{item['name']}' already exists.")
            
    # 2. Perform search queries
    search_keywords = ["python", "apple", "design"]
    
    for kw in search_keywords:
        print(f"\n--- Searching for: '{kw}' ---")
        results = dal.search_items(kw)
        if results:
            for item in results:
                print(f"Found: Name='{item.get('name')}', Description='{item.get('description')}' (ID: {item.get('id')})")
        else:
            print("No items found matching the keyword.")

if __name__ == "__main__":
    run_demo()