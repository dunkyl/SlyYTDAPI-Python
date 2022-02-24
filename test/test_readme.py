from SlyYTDAPI import *

async def test_readme():
    yt = await YouTubeData(open('./test/api_key.txt').read())

    my_video = await yt.video('dQw4w9WgXcQ')
    print(F"Check this out!\n{my_video.link()}")

    # keep it simple
    _ = await my_video.comments(limit=10) # list[Comment]

    # or opt in to generators
    print('\n---\n'.join([
        F"{c.author_name} > {c.body}"
        async for c in my_video.comments(limit=10)
    ]))
