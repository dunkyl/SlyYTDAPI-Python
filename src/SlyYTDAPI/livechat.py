"""
YouTube Live Chat Endpoints for the Data API v3
https://developers.google.com/youtube/v3/live/docs
"""
from datetime import datetime
from .ytdapi import YouTubeData, Part, yt_date

# class _LiveChatEvent: pass

class ChatEnd: pass

class ChatMessageDeleted:
    id: str

class SponsorOnlyStart: pass

class SponsorOnlyEnd: pass

class NewSponsor:
    id: str
    name: str
    channel_id: str

class SuperChat: pass

class SuperSticker: pass

class Tombstone: pass

class UserBanned: pass

class MembershipGifting: pass

class MembershipGiftReceived: pass

class TextChat:
    id: str
    # part: snippet
    author_name: str
    author_channel_id: str
    body: str
    created_at: datetime

class YouTubeDataWithLiveChat(YouTubeData):
    _next_page: str|None = None