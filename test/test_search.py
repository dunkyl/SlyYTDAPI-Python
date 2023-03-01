from SlyYTDAPI import *

async def test_search():
    yt = YouTubeData(open('./test/api_key.txt').read())

    search_results = await yt.search_videos('gangnam style', limit=5)

    for video in search_results:
        print(F"{video.title} by {video.channel_name}")

    assert len(search_results) == 5