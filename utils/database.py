########################################################################
# NOTE: This file will be deleted as we move to a db that is sql based #
########################################################################
from pymongo import MongoClient
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI")) # One username and password on the github is now deleted and new database was created

db = client.mail