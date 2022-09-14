####################################################################
# NOTE: This file is now deprecated. Please use the new db.py file #
####################################################################
import motor.motor_asyncio
import os
from dotenv import load_dotenv

load_dotenv()
client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_URI")) # One username and password on the github is now deleted and new database was created

db = client.mail