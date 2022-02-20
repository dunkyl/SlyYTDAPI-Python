import pytest
from SlyYTDAPI import *

@pytest.mark.skip(reason="special permissions required")
async def test_members():
    yt = await YouTubeData_WithMembers(open('api_key.txt').read())

    members = await yt.get_my_members()

    for member in members:
        print(member.channel_name)