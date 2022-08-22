from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI")) # One username and password on the github is now deleted and new database was created

db = client.mail