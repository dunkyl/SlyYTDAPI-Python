import os
from SlyYTDAPI import *
test_dir = os.path.dirname(__file__)
async def test_readme():
    yt = YouTubeData(open(F'{test_dir}/api_key.txt').read())

    my_video = await yt.video('dQw4w9WgXcQ')
    print(F"Check this out!\n{my_video.link()}")

    # keep it simple
    all_comments = await my_video.comments(limit=10) # list[Comment]

    # or opt in to generators
    print('\n---\n'.join([
        F"{c.display_name} > {c.body}"
        async for c in my_video.comments(limit=10)
    ]))

    # ---

    assert len(all_comments) > 0
