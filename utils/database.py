##############################################################################################
# NOTE: This file will be updated a lot in the future so please make sure to stay up to date #
##############################################################################################
import motor.motor_asyncio
import os
from dotenv import load_dotenv

load_dotenv()
client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_URI")) # One username and password on the github is now deleted and new database was created

async def check_db():
 try:
    print(await client.server_info())
 except Exception:
        print("Unable to connect to the server.")

db = client.mail