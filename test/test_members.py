import pytest, os
from SlyYTDAPI import *
test_dir = os.path.dirname(__file__)
@pytest.mark.skip(reason="special permissions required")
async def test_members():
    auth = OAuth2(F'{test_dir}/app.json', F'{test_dir}/user.json')
    yt = YouTubeData_WithMembers(auth)

    members = await yt.get_my_members()

    for member in members:
        print(member.channel_name)