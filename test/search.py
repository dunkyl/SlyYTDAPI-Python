import asyncio
from SlyYTDAPI import *

async def main():
    yt = YouTubeData_WithMembers(open('api_key.txt').read())

    search_results = await yt.search_videos('gangnam style', limit=5)

    for video in search_results:
        print(F"{video.title} by {video.channel_name}")

asyncio.run(main())