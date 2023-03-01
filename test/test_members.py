import pytest
from SlyYTDAPI import *

@pytest.mark.skip(reason="special permissions required")
async def test_members():
    auth = OAuth2('test/app.json', 'test/user.json')
    yt = YouTubeData_WithMembers(auth)

    members = await yt.get_my_members()

    for member in members:
        print(member.channel_name)