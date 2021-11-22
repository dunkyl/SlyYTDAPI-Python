# SlyYTDAPI: YouTube Data API

> 🚧 **This library is an early work in progress! Breaking changes may be frequent.**

> 🐍 For Python 3.10+

No-boilerplate, async YouTube Data API access. 😋

```py
pip install slyytdapi
```

This library does not have full coverage.
All methods are read-only.
Currently, the following topics are supported:

* Videos
* Channels
* Comment threads
* Video search
* Channel members (requires approval from YouTube)

---

Example usage:

```py
import asyncio
from SlyYTDAPI import *

async def main():
    # don't forget to keep your secrets secret!
    yt = YouTubeData(open('api_key.txt').read())

    my_video = await yt.video('dQw4w9WgXcQ')
    print(F"Check this out!\n{my_video.link()}")

    # KISS
    recent_comments = await my_video.comments(limit=10)

    # or opt in to generators
    print('\n---\n'.join([
        F"{c.author} > {c.body}
        async for c in my_video.comments(limit=10)
    ]))
    
asyncio.run(main())
```
