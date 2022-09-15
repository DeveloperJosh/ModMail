import asyncio
from utils.bot import main
from utils import db
if __name__ == "__main__":
   db.init()
   asyncio.run(main())