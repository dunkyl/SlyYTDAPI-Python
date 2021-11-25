import asyncio
from SlyYTDAPI import *

async def main():
    # don't forget to keep your secrets secret!
    yt = YouTubeData_WithMembers(open('api_key.txt').read())

    members = await yt.get_my_members()

    
    
asyncio.run(main())