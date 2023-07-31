import os
from SlyYTDAPI import *
test_dir = os.path.dirname(__file__)
async def test_playlists():
    yt = YouTubeData(open(F'{test_dir}/api_key.txt').read())

    seattle_mariners_soundtrack = \
        await yt.get_playlist_videos('PLoACd69cZBKexixB0sl5a8oLsa-DhlW7m')

    for video in seattle_mariners_soundtrack:
        print(video.title)

    assert len(seattle_mariners_soundtrack) > 0