from SlyYTDAPI import *

async def test_channels():
    yt = await YouTubeData(open('./test/api_key.txt').read())

    channel = await yt.channel('UCy0tKL1T7wFoYcxCe0xjN6Q')

    print(channel.name)