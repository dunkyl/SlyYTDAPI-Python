import asyncio
from SlyYTDAPI import *

async def main():
    # don't forget to keep your secrets secret!
    yt = YouTubeData(open('api_key.txt').read())

    my_video = await yt.video('dQw4w9WgXcQ')
    print(F"Check this out!\n{my_video.link()}")

    # KISS
    _ = await my_video.comments(limit=10) # list[Comment]

    # or opt in to generators
    print('\n---\n'.join([
        F"{c.author_channel_id} > {c.body}"
        async for c in my_video.comments(limit=10)
    ]))

    
    
asyncio.run(main())