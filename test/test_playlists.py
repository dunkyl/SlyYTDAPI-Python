from SlyYTDAPI import *

async def test_playlists():
    yt = YouTubeData(open('./test/api_key.txt').read())

    seattle_mariners_soundtrack = \
        await yt.get_playlist_videos('PLoACd69cZBKexixB0sl5a8oLsa-DhlW7m')

    for video in seattle_mariners_soundtrack:
        print(video.title)

    assert len(seattle_mariners_soundtrack) > 0