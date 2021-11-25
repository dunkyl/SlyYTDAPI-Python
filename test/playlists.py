import asyncio
from SlyYTDAPI import *

async def main():
    # don't forget to keep your secrets secret!
    yt = YouTubeData(open('api_key.txt').read())

    seattle_mariners_soundtrack = \
        await yt.get_playlist_videos('PLoACd69cZBKexixB0sl5a8oLsa-DhlW7m')

    for video in seattle_mariners_soundtrack:
        print(video.title)

    
    
asyncio.run(main())