# ![sly logo](https://raw.githubusercontent.com/dunkyl/SlyMeta/main/sly%20logo.svg) Sly YouTube Data API for Python

> 🚧 **This library is an early work in progress! Breaking changes may be frequent.**

> 🐍 For Python 3.10+

No-boilerplate, async and typed YouTube Data API access. 😋

```shell
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

For collecting statistics about your own channel using the YouTube analytics API, see [YTAAPI](https://github.com/dunkyl/SlyPyYTAAPI).

---

Example usage:

```python
import asyncio
from SlyYTDAPI import *

async def main():
    # don't forget to keep your secrets secret!
    yt = await YouTubeData(open('api_key.txt').read())

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
