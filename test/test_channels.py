import os
from SlyYTDAPI import *

test_dir = os.path.dirname(__file__)
async def test_channels():
    yt = YouTubeData(open(F'{test_dir}/api_key.txt').read())

    channel = await yt.channel('UCy0tKL1T7wFoYcxCe0xjN6Q')

    print(channel.display_name)
    
    channel2 = await yt.channel_by_handle('@GoogleDevelopers')
    
    print(channel2.display_name)
    
    channels = await yt.channels_by_username('GoogleDevelopers')
    
    print([c.display_name for c in channels])
    
    assert len(channels) > 0