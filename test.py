import asyncio
import asyncpg

async def run():
    conn = await asyncpg.connect(user='blue', password='Gunner0099', database='blue', host='192.168.1.27')
    values = await conn.fetch(
        'SELECT * FROM mytable WHERE id = $1',
        10,
    )
    await conn.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(run())