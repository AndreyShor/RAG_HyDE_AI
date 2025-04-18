import json
from pathlib import Path
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
profiles = client["db_main"]["profiles"]

#current path 

personName = "alice"

FileName = personName + ".json"

currenntDirectPath = Path(__file__).parent

pathToFile = currenntDirectPath / FileName

data = json.loads(Path(pathToFile).read_text())
data["_id"] = personName                        # stable key

profiles.update_one({"_id": personName}, {"$set": data}, upsert=True)
print("done!")
