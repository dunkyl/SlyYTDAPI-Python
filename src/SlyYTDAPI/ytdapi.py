import re
from datetime import datetime
from dataclasses import dataclass
from typing import Generic, TypeVar, Any
from SlyAPI import *

SCOPES_ROOT = 'https://www.googleapis.com/auth/youtube'

class Scope(EnumParam):
    READONLY     = F"{SCOPES_ROOT}.readonly"
    MEMBERS      = F"{SCOPES_ROOT}.channel-memberships.creator"

class Part(EnumParam):
    ID           = 'id'             # quota cost: 0
    DETAILS      = 'contentDetails' # quota cost: 2
    SNIPPET      = 'snippet'        # quota cost: 2
    STATUS       = 'status'         # quota cost: 2
    STATISTICS   = 'statistics'     # quota cost: 2
    REPLIES      = 'replies'        # quota cost: 2
    # ...

class PrivacyStatus(EnumParam):
    PRIVATE      = 'private'
    UNLISTED     = 'unlisted'
    PUBLIC       = 'public'

class SafeSearch(EnumParam):
    SAFE         = 'strict'
    MODERATE     = 'moderate'
    UNSAFE       = 'none'

class Order(EnumParam):
    DATE         = 'date'
    LIKES        = 'rating'
    RELEVANCE    = 'relevance'
    ALPHABETICAL = 'title'
    VIEWS        = 'viewCount'

class CommentOrder(EnumParam):
    RELEVANCE    = 'relevance'
    TIME         = 'time'

ISO8601_PERIOD = re.compile(r'P(\d+)?T(?:(\d{1,2})H)?(?:(\d{1,2})M)?(\d{1,2})S')

def yt_date(date: str) -> datetime:
    return datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')

W = TypeVar('W')
T = TypeVar('T')

def get_dict_path(d: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key not in d:
            return None
        d = d[key]
    return d
    
@dataclass
class APIObj(Generic[W]):
    _service: W

    def __init__(self, service: W):
        self._service = service

class Comment:
    id: str
    # part: snippet
    author_name: str
    author_channel_id: str
    body: str
    created_at: datetime
    # part: replies
    replies: list['Comment']|None

    def __init__(self, source: dict[str, Any]):
        # case of top-level comment
        if tlc := source.get('snippet', {}).get('topLevelComment'):
            replies: list[Any] = source.get('replies', {}).get('comments', [])
            self.replies = [Comment(r) for r in replies]
            source = tlc
            
        self.id = source['id']
        if snippet := source.get('snippet'):
            self.author_name = snippet['authorDisplayName']
            self.author_channel_id = snippet['authorChannelId']['value']
            self.body = snippet['textDisplay']
            self.created_at = yt_date(snippet['publishedAt'])
        


class Video(APIObj['YouTubeData']):
    id: str

    # part: snippet
    title: str
    description: str
    published_at: datetime
    channel_id: str
    channel_name: str
    tags: list[str]
    is_livestream: bool

    # part: contentDetails
    duration: int

    # part: status
    privacy: PrivacyStatus

    # part: statistics
    view_count: int
    like_count: int

    # dislike_count: int ## rest in peace
    comment_count: int

    def __init__(self, source: dict[str, Any], service: 'YouTubeData'):
        super().__init__(service)
        match source['id']:
            case str():
                self.id = source['id']
            case dict(): # case for video search result object
                self.id = source['id']['videoId']
            case _:
                raise ValueError("Video expects source id to be a string or dict")
        
        if snippet := source.get('snippet'):
            self.title = snippet['title']
            self.description = snippet['description']
            self.published_at = yt_date(snippet['publishedAt'])
            self.channel_id = snippet['channelId']
            self.channel_name = snippet['channelTitle']
            self.tags = snippet.get('tags', [])
            self.is_livestream = snippet.get('liveBroadcastContent') == 'live'
        if contentDetails := source.get('contentDetails'):
            m = ISO8601_PERIOD.match(contentDetails['duration'])
            if m:
                days, hours, minutes, seconds = (int(g) if g else 0 for g in m.groups())
                self.duration = days * 24 * 60 * 60 + hours * 60 * 60 + minutes * 60 + seconds
            else:
                raise ValueError(F"Unknown duration format: {contentDetails['duration']}")
        if status := source.get('status'):
            self.privacy = status['privacyStatus']


    def link(self, short: bool = False) -> str:
        if not short:
            return F"https://www.youtube.com/watch?v={self.id}"
        else:
            return F"https://youtu.be/{self.id}"

    def comments(self, limit: int | None = 100) -> AsyncTrans[Comment]:
        return self._service.comments(self.id, limit=limit)

    async def channel(self) -> 'Channel':
        return await self._service.channel(self.channel_id)

class Playlist(APIObj['YouTubeData']):
    id: str

    def __init__(self, id: str, service: 'YouTubeData'):
        super().__init__(service)
        self.id = id

    def link(self) -> str:
        return F"https://www.youtube.com/playlist?list={self.id}"

class Channel(APIObj['YouTubeData']):
    id: str

    # part: snippet
    name: str
    description: str
    created_at: datetime
    profile_image_url: str|None = None
    custom_url: str|None = None

    # part: contentDetails
    uploads_playlist: Playlist

    # part: statistics
    view_count: int
    subscriber_count: int
    video_count: int

    def __init__(self, source: dict[str, Any], service: 'YouTubeData'):
        super().__init__(service)

        self.id = source['id']
        if snippet := source.get('snippet'):
            self.name = snippet['title']
            self.description = snippet['description']
            self.created_at = yt_date(snippet['publishedAt'])
            self.profile_image_url = snippet.get('thumbnails', {}).get('default', {}).get('url')
            self.custom_url = snippet.get('customUrl')

        if details := source.get('contentDetails'):
            self.uploads_playlist = Playlist(details['relatedPlaylists']['uploads'], service)

        if stats := source.get('statistics'):
            self.view_count = int(stats['viewCount'])
            self.subscriber_count = int(stats['subscriberCount'])
            self.video_count = int(stats['videoCount'])

    def link(self) -> str:
        if self.custom_url:
            return F"https://www.youtube.com/c/{self.custom_url}"
        else:
            return F"https://www.youtube.com/channels/{self.id}"

    async def update(self):
        new = await self._service.channel(self.id)
        self.__dict__.update(new.__dict__)

    def videos(self, limit: int|None=None, mine: bool|None=None) -> AsyncTrans[Video]:
        return self._service.search_videos(channel_id=self.id, limit=limit, mine=mine)

class YouTubeData(WebAPI):
    base_url = 'https://www.googleapis.com/youtube/v3'

    def __init__(self, app_or_api_key: str|OAuth2, user: str | OAuth2User | None = None, scope: Scope=Scope.READONLY):
        if isinstance(user, str):
            user = OAuth2User(user)

        match app_or_api_key:
            case str() if app_or_api_key.endswith('.json'):
                auth = OAuth2(app_or_api_key, user)
            case str():
                auth = APIKey('key', app_or_api_key)
            case _:
                auth = app_or_api_key
        super().__init__(auth)
        if not isinstance(auth, APIKey):
            auth.verify_scope(str(scope))

    async def my_channel(self, parts: Part=Part.SNIPPET) -> Channel:
        return (await self._channels_list(mine=True, parts=parts, limit=1))[0]

    async def channels(self, channel_ids: list[str], parts: Part) -> list[Channel]:
        return await self._channels_list(channel_ids=channel_ids, parts=parts)

    async def channel(self, channel_id: str, parts: Part=Part.SNIPPET) -> Channel:
        return (await self._channels_list(channel_ids=[channel_id], parts=parts))[0]

    def _channels_list(self,
        channel_ids: list[str]|None=None,
        mine: bool=False,
        parts: Part=Part.SNIPPET,
        limit: int|None=None) -> AsyncTrans[Channel]:
        if mine==bool(channel_ids):
            raise ValueError("Must specify exactly one of channel id or mine in channel list query")
        params = {
            **parts.to_dict(),
            'mine': mine if mine else None,
            'id': ','.join(channel_ids) if channel_ids else None,
            'maxResults': min(50, limit) if limit else None,
        }
        return self.paginated(
            '/channels', params, limit
            ).map(lambda r: Channel(r, self))

    def videos(self,
        video_ids: list[str],
        parts: Part=Part.ID+Part.SNIPPET) -> AsyncTrans[Video]:
        params = {
            **parts.to_dict(),
            'id': ','.join(video_ids),
        }
        return self.paginated(
            '/videos', params, None
            ).map(lambda r: Video(r, self))

    async def video(self, id: str, parts: Part=Part.ID+Part.SNIPPET) -> Video:
        return (await self.videos([id], parts))[0]

    def get_playlist_videos(self,
        playlist_id: str, 
        parts: Part=Part.SNIPPET,
        limit: int|None=None) -> AsyncTrans[Video]:
        params = {
            **parts.to_dict(),
            'playlistId': playlist_id,
            'maxResults': min(50, limit) if limit else None,
        }
        return self.paginated(
            '/playlistItems', params, limit
            ).map(lambda r: Video(r, self))

    def search_videos(self,
        query: str|None=None,
        channel_id: str|None=None,
        after: datetime|None=None,
        before: datetime|None=None,
        mine: bool|None=None,
        order: Order=Order.RELEVANCE,
        safeSearch: SafeSearch=SafeSearch.MODERATE,
        parts: Part=Part.SNIPPET,
        limit: int|None=50) -> AsyncTrans[Video]:
        params = {
            **(parts+safeSearch+order).to_dict(),
            'type': 'video',
            'q': query,
            'channelId': channel_id,
            'forMine': mine,
            'publishedAfter': after.isoformat("T") + "Z" if after else None,
            'publishedBefore': before.isoformat("T") + "Z" if before else None,
            'maxResults': min(50, limit) if limit else None,
        }

        return self.paginated(
            '/search', params, limit
            ).map(lambda r: Video(r, self))

    def comments(self,
        video_id: str,
        query: str|None=None,
        parts: Part=Part.SNIPPET+Part.REPLIES,
        order: CommentOrder=CommentOrder.TIME,
        limit: int|None=None) -> AsyncTrans[Comment]:
        params = {
            **(parts+order).to_dict(),
            'searchTerms': query,
            'videoId': video_id,
            'maxResults': min(100, limit) if limit else None,
        }
        return self.paginated(
            '/commentThreads', params, limit
            ) .map(Comment)
    