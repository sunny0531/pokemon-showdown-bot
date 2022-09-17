from main_rewrite import Client
import asyncio
# client = Client("", "") #username, password
client = Client("")  # username


async def main():
    global client
    await client.connect()
    await client.parse()

loop = asyncio.get_event_loop()
res = loop.run_until_complete(main())
