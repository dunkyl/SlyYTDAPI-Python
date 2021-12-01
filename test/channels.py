import asyncio
from SlyYTDAPI import *

async def main():
    yt = await YouTubeData_WithMembers(open('api_key.txt').read())

    channel = await yt.channel('UCy0tKL1T7wFoYcxCe0xjN6Q')

    print(channel.name)

asyncio.run(main())