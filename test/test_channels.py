import os
from SlyYTDAPI import *

test_dir = os.path.dirname(__file__)
async def test_channels():
    yt = YouTubeData(open(F'{test_dir}/api_key.txt').read())

    channel = await yt.channel('UCy0tKL1T7wFoYcxCe0xjN6Q')
    channel_ = await yt.channel_by_url('https://www.youtube.com/channel/UCy0tKL1T7wFoYcxCe0xjN6Q')
    assert channel.id == channel_.id

    print(channel.display_name)
    
    channel2 = await yt.channel_by_handle('@GoogleDevelopers')
    channel2_ = await yt.channel_by_url('https://www.youtube.com/@googledevelopers')
    assert channel2.id == channel2_.id
    
    print(channel2.display_name)
    
    channel3 = await yt.channel_by_username('GoogleDevelopers')
    channel3_ = await yt.channel_by_url('https://www.youtube.com/c/googledevelopers')
    assert channel2.id == channel2_.id
    
    print(channel3.display_name)