from fastapi import FastAPI
from pydantic import BaseModel
from bson import ObjectId
import requests
import redis
import json
app = FastAPI()

from pymongo.mongo_client import MongoClient
uri = "mongodb://localhost:27017/"

client = MongoClient(uri)

# Database and collection
db = client.fastapi
collection = db.data

# Define a Pydantic model for the data in your collection
class Item(BaseModel):
    name: str
    description: str

# Routes
@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI and MongoDB example!"}

@app.get("/items/")
async def read_items():
    items = list(collection.find())
    for item in items:
        item["_id"] = str(item["_id"])  # Convert ObjectId to string
    return items

@app.post("/items/")
async def create_item(item: Item):
    result = collection.insert_one(item.dict())
    return {"_id": str(result.inserted_id)}

@app.get("/items/{item_id}")
async def read_item(item_id: str):
    item = collection.find_one({"_id": ObjectId(item_id)})
    if item:
        item["_id"] = str(item["_id"])  # Convert ObjectId to string
        return item
    return {"error": "Item not found"}


rd = redis.Redis(host="localhost", port=6379, db=0)

@app.get("/country/{country}")
def read_fish(country: str):
    cache = rd.get(country)
    if cache:
        print("Cache hit")
        return json.loads(cache)
    else:
        print("Cache Miss")
        r = requests.get(f"https://restcountries.com/v3.1/name/{country}")
        # print(r.status_code)
        # print(r.text)
        rd.set(country, r.text)
        return r.json()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)