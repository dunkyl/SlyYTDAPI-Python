# ![sly logo](https://raw.githubusercontent.com/dunkyl/SlyMeta/main/sly%20logo.svg) Sly YouTube Data API for Python

<!-- elevator begin -->

> 🚧 **This library is an early work in progress! Breaking changes may be frequent.**

> 🐍 For Python 3.10+

<p style="text-align: center;">
  No-boilerplate, async, typed access to YouTube Data API 😋
</p>

```shell
pip install slyytdapi
```

This library does not have full coverage.
All methods are read-only.
Currently, the following topics are supported:

* Videos & Playlists
* Channels
* Comment threads
* Video search
* Channel members (requires approval from YouTube)

For collecting statistics about your own channel using the YouTube analytics API, see [YTAAPI](https://github.com/dunkyl/SlyYTAAPI-Python).

<!-- elevator end -->

---

Example usage:

```python
import asyncio
from SlyYTDAPI import *

async def main():
    # don't forget to keep your secrets secret!
    yt = YouTubeData(open('api_key.txt').read())

    my_video = await yt.video('dQw4w9WgXcQ')
    print(F"Check this out!\n{my_video.link()}")

    # keep it simple
    _ = await my_video.comments(limit=10) # list[Comment]

    # or opt in to generators
    print('\n---\n'.join([
        F"{c.author_name} > {c.body}"
        async for c in my_video.comments(limit=10)
    ]))
    
asyncio.run(main())
```

---

Access to YouTube Data API is free is limited by a quota. See YouTube's [determine quota cost](https://developers.google.com/youtube/v3/determine_quota_cost) article for more information.

If you are using OAuth2 instead of an API Key, a CLI is provided to grant credentials to yourself:

```sh
# WINDOWS
py -m SlyYTDAPI grant
# MacOS or Linux
python3 -m SlyYTDAPI grant
```

Both methods require a Google Cloud Console account and project credentials.
Please see https://docs.dunkyl.net/SlyAPI-Python/tutorial/oauth2.html for more information.
