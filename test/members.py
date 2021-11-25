import asyncio
from SlyYTDAPI import *

async def main():
    yt = YouTubeData_WithMembers(open('api_key.txt').read())

    members = await yt.get_my_members()

    for member in members:
        print(member.channel_name)

asyncio.run(main())