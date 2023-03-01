import sys, asyncio, inspect

from SlyYTDAPI.ytdapi import Scope
from SlyAPI.flow import *

async def main(args: list[str]):

    match args:
        case ['grant']:
            await grant_wizard(Scope, kind='OAuth2')
        case _: # help
            print(inspect.cleandoc("""
            SlyYTDAPI command line: tool for YouTube OAuth2.
            Usage:
                SlyYTDAPI grant
                Same as SlyAPI, but scopes are listed in a menu.
            """))

if __name__ == '__main__':
    asyncio.run(main(sys.argv[1:]))