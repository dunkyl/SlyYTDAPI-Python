import os
from SlyYTDAPI import *
test_dir = os.path.dirname(__file__)
async def test_search():
    yt = YouTubeData(open(F'{test_dir}/api_key.txt').read())

    search_results = await yt.search_videos('gangnam style', limit=5)

    for video in search_results:
        print(F"{video.title} by {video.channel_name}")

    assert len(search_results) == 5