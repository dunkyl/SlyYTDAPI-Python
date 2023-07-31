import os
from SlyYTDAPI import *

test_dir = os.path.dirname(__file__)
async def test_channels():
    yt = YouTubeData(open(F'{test_dir}/api_key.txt').read())

    channel = await yt.channel('UCy0tKL1T7wFoYcxCe0xjN6Q')

    print(channel.display_name)