from dataclasses import dataclass, asdict
import inspect
import re
from enum import Enum
from datetime import datetime, timezone
from typing import TypeVar, Any
from warnings import warn
from SlyAPI import *
from SlyAPI.web import ParamsDict
from SlyAPI.webapi import is_dataclass_instance

SCOPES_ROOT = 'https://www.googleapis.com/auth/youtube'

RE_CHANNEL_URL = re.compile(r'^(?:https?:)?\/\/?(?:www\.|m\.)(?:youtube\.com)\/(?:c\/(?P<username>[a-zA-Z0-9\-_]+)|@(?P<handle>[a-zA-Z0-9\-_]+)|channel\/(?P<id>UC[a-zA-Z0-9\-_]+))')

class Scope:
    READONLY     = F"{SCOPES_ROOT}.readonly"
    MEMBERS      = F"{SCOPES_ROOT}.channel-memberships.creator"

class Part(Enum):
    ID                      = 'id'
    DETAILS                 = 'contentDetails'
    SNIPPET                 = 'snippet'
    STATUS                  = 'status'
    STATISTICS              = 'statistics'
    REPLIES                 = 'replies'
    LOCALIZATIONS           = 'localizations'
    EMBED                   = 'player'
    LIVESTREAM_DETAILS      = 'liveStreamingDetails'
    TOPIC_CATEGORIES        = 'topicDetails'
    RECORDING_DETAILS       = 'recordingDetails'
    
    # only if authorized by channel owner
    FILE_DETAILS            = 'fileDetails'
    PROCESSING_DETAILS      = 'processingDetails'

    @staticmethod
    def ALL_PUBLIC():
        return {
            Part.DETAILS,
            Part.SNIPPET,
            Part.STATUS,
            Part.STATISTICS,
            Part.LOCALIZATIONS,
            Part.EMBED,
            Part.LIVESTREAM_DETAILS,
            Part.TOPIC_CATEGORIES,
            Part.RECORDING_DETAILS,
        }
    
    def intersection(self, other: 'set[Part]'):
        return {self}

class PrivacyStatus(Enum):
    PRIVATE      = 'private'
    UNLISTED     = 'unlisted'
    PUBLIC       = 'public'

class ProcessingStatus(Enum):
    FAILED       = 'failed'
    PROCESSING   = 'processing'
    SUCCEEDED    = 'succeeded'
    TERMINATED   = 'terminated'

class SafeSearch(Enum):
    SAFE         = 'strict'
    MODERATE     = 'moderate'
    UNSAFE       = 'none'

class Order(Enum):
    DATE         = 'date'
    LIKES        = 'rating'
    RELEVANCE    = 'relevance'
    ALPHABETICAL = 'title'
    VIEWS        = 'viewCount'

class CommentOrder(Enum):
    RELEVANCE    = 'relevance'
    TIME         = 'time'

ISO8601_PERIOD = re.compile(r'P(?:(\d+)D)?(?:T(?:(\d{1,2})H)?(?:(\d{1,2})M)?(?:(\d{1,2})S)?)?')

def yt_date(date: str) -> datetime:
    if date.endswith('Z'):
        try:
            return datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError:
            return datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
    else:
        return datetime.fromisoformat(date)
    
def yt_date_or_none(date: str|None) -> datetime|None:
    if date is not None:
        return yt_date(date)
    else:
        return None

W = TypeVar('W')
T = TypeVar('T')

def get_dict_path(d: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key not in d:
            return None
        d = d[key]
    return d
    
class Comment:
    id: str
    # part: snippet
    author_display_name: str
    author_channel_id: str
    body: str
    created_at: datetime
    # part: replies
    replies: list['Comment']|None

    @property
    def author_name(self):
        warn("author_name is deprecated, please use author_display_name")
        return self.author_display_name

    def __init__(self, source: dict[str, Any]):
        # case of top-level comment
        if tlc := source.get('snippet', {}).get('topLevelComment'):
            replies: list[Any] = source.get('replies', {}).get('comments', [])
            self.replies = [Comment(r) for r in replies]
            source = tlc
            
        self.id = source['id']
        if snippet := source.get('snippet'):
            self.author_display_name = snippet['authorDisplayName']
            self.author_channel_id = snippet['authorChannelId']['value']
            self.body = snippet['textDisplay']
            self.created_at = yt_date(snippet['publishedAt'])
        
@dataclass
class EmbedInfo:
    embedHtml: str
    embedHeight: int
    embedWidth: int

@dataclass
class ContentDetails:
    duration: int
    is_licensed: bool
    blocked_in: list[str]
    allowed_in: list[str]
    rating: dict[str, str]
    dimension: str
    definition: str
    caption: str
    projection: str | None

@dataclass
class StatusDetails:
    privacy: PrivacyStatus
    upload_status: str
    failure_reason: str | None
    rejection_reason: str | None
    license: str
    is_embeddable: bool
    has_viewable_stats: bool
    is_made_for_kids: bool
    # only if authorized by channel owner
    self_declared_made_for_kids: bool | None

@dataclass
class VideoPublicStatistics:
    view_count: int
    like_count: int | None
    comment_count: int | None

@dataclass
class FileDetails:
    @dataclass
    class VideoStream:
        width: int
        height: int
        framerate: float
        aspect_ratio: float
        codec: str
        bitrate: int
        rotation: str
        vendor: str
    videoStreams: list[VideoStream]

    @dataclass
    class AudioStream:
        channels_count: int
        codec: str
        bitrate: str
        vendor: str
    audioStreams: list[AudioStream]

    name: str
    bytes: int
    type: str
    container: str
    duration_milliseconds: int
    bitrate: int
    created_at: datetime | None


@dataclass
class LivestreamDetails:
    # only available after stream starts
    viewers: int | None
    started_at: datetime | None
    # only available after stream ends
    ended_at: datetime | None

    scheduled_start: datetime
    scheduled_end: datetime | None
    chat_id: str
    
@dataclass
class ProcessingDetails:
    status: ProcessingStatus
    parts_total: int | None
    parts_processed: int | None
    milliseconds_remaining: int | None
    failureReason: str | None

@dataclass
class VideoLocalization:
    title: str
    description: str

class Video:
    _youtube: 'YouTubeData'
    id: str

    # part: snippet
    title: str
    description: str
    published_at: datetime
    channel_id: str
    channel_name: str
    tags: list[str]
    is_livestream: bool
    default_audio_language: str | None = None
    thumbnails: list[str] | None = None
    localized_title: str | None = None
    localized_description: str | None = None

    # part: contentDetails
    duration: int | None = None
    content_details: ContentDetails | None = None

    # part: status
    privacy: PrivacyStatus | None = None
    status_details: StatusDetails | None = None

    # part: statistics
    view_count: int | None = None
    like_count: int | None = None

    # dislike_count: int ## rest in peace
    comment_count: int | None = None

    # part: liveStreamingDetails
    livestream_details: LivestreamDetails | None = None
    
    # part: topicDetails
    topic_categories: list[str] | None = None
    
    # part: localizations
    localizations: dict[str, VideoLocalization] | None = None
    
    # part: recordingDetails
    recorded_at: datetime | None = None

    # part: fileDetails
    file_details: FileDetails | None = None

    # part: processingDetails
    processing_details: ProcessingDetails | None = None
    
    def to_dict(self) -> dict[str, Any]:
        """
        Returns a dictionary representation of the Video object.
        """
        # TODO: Revisit with SlySerialize if TypeForm is introduced
        # https://discuss.python.org/t/typeform-spelling-for-a-type-annotation-object-at-runtime/51435
        json = {
            name: asdict(member) if is_dataclass_instance(member) else member
            for name, member in inspect.getmembers(self)
            if not name.startswith('_')
                and not inspect.isfunction(member)
                and not inspect.ismethod(member)
        }
        if 'localizations' in json:
            json['localizations'] = {
                k: asdict(v) for k, v in json['localizations'].items()
            }
        return json

    def __init__(self, source: dict[str, Any], yt: 'YouTubeData'):
        self._youtube = yt
        match source['id']:
            case str():
                self.id = source['id']
            case dict(): # case for video search result object
                self.id = source['id']['videoId']
            case _:
                raise ValueError("Video expects source id to be a string or dict")
        
        if snippet := source.get('snippet'):
            self.title = snippet.get('title')
            self.description = snippet.get('description')
            self.published_at = yt_date(snippet.get('publishedAt'))
            self.channel_id = snippet.get('channelId')
            self.channel_name = snippet.get('channelTitle')
            self.tags = snippet.get('tags', [])
            self.is_livestream = snippet.get('liveBroadcastContent') == 'live'
            self.default_audio_language = snippet.get('defaultAudioLanguage')

            self.thumbnails = [x.get("url") for x in snippet.get("thumbnails", {}).values()]
            self.localized_title = snippet.get("localized", {}).get("title")
            self.localized_description = snippet.get("localized", {}).get("description")
            
        if source.get('kind') == 'youtube#playlistItem':
            self.id = source.get('contentDetails', {}).get('videoId')
        elif contentDetails := source.get('contentDetails'):
            
            m = ISO8601_PERIOD.match(contentDetails.get('duration'))
            if m:
                days, hours, minutes, seconds = (int(g) if g else 0 for g in m.groups())
                self.duration = days * 24 * 60 * 60 + hours * 60 * 60 + minutes * 60 + seconds
            else:
                raise ValueError(F"Unknown duration format: {contentDetails['duration']}")
            self.content_details = ContentDetails(
                self.duration,
                contentDetails.get('licensedContent'),
                contentDetails.get("regionRestriction", {}).get("blocked", []),
                contentDetails.get("regionRestriction", {}).get("allowed", []),
                contentDetails.get("contentRating", {}),
                contentDetails.get("dimension"),
                contentDetails.get("definition"),
                contentDetails.get("caption"),
                contentDetails.get("projection")
            )

        if status := source.get('status'):
            self.privacy = status.get('privacyStatus')
            self.status_details = StatusDetails(
                status.get('privacyStatus'),
                status.get('uploadStatus'),
                status.get('failureReason'),
                status.get('rejectionReason'),
                status.get('license'),
                status.get('embeddable'),
                status.get('publicStatsViewable'),
                status.get('madeForKids'),
                status.get('selfDeclaredMadeForKids')
            )

        if statistics := source.get('statistics'):
            self.view_count = int(statistics.get('viewCount'))
            if statistics.get('likeCount'): # may be hidden
                self.like_count = int(statistics.get('likeCount'))
            if statistics.get('commentCount'): # may be disabled
                self.comment_count = int(statistics.get('commentCount'))

        if stream := source.get('liveStreamingDetails'):
            self.livestream_details = LivestreamDetails(
                stream.get('concurrentViewers'),
                yt_date_or_none(stream.get('actualStartTime')),
                yt_date_or_none(stream.get('actualEndTime')),
                yt_date(stream.get('scheduledStartTime')),
                yt_date_or_none(stream.get('scheduledEndTime')),
                stream.get('activeLiveChatId')
            )

        if topic_details := source.get('topicDetails'):
            self.topic_categories = topic_details.get('topicCategories', None)

        if recording_details := source.get('recordingDetails'):
            self.recorded_at = yt_date_or_none(recording_details.get('recordingDate'))

        if fileDetails := source.get('fileDetails'):
            self.file_details = FileDetails(
                [FileDetails.VideoStream(
                    v.get('widthPixels'), v.get('heightPixels'), v.get('frameRateFps'),
                    v.get('aspectRatio'), v.get('codec'), v.get('bitrateBps'),
                    v.get('rotation'), v.get('vendor')
                    ) for v in fileDetails.get('videoStreams')],
                [FileDetails.AudioStream(
                    a.get('channelCount'), a.get('codec'), a.get('bitrateBps'), a.get('vendor')
                    ) for a in fileDetails.get('audioStreams')],
                fileDetails.get('fileName'),
                fileDetails.get('fileSize'),
                fileDetails.get('fileType'),
                fileDetails.get('container'),
                fileDetails.get('durationMs'),
                fileDetails.get('bitrateBps'),
                yt_date_or_none(fileDetails.get('creationTime')),
            )

        if processingDetails := source.get('processingDetails'):
            self.processing_details = ProcessingDetails(
                processingDetails.get('processingStatus'),
                processingDetails.get('processingProgress', {}).get('partsTotal'),
                processingDetails.get('processingProgress', {}).get('partsProcessed'),
                processingDetails.get('processingProgress', {}).get('timeLeftMs'),
                processingDetails.get('processingFailureReason'),
            )
            
        if localizations := source.get('localizations'):
            self.localizations = {
                k: VideoLocalization(**v) for k, v in localizations.items()
            }

    def link(self, short: bool = False) -> str:
        if not short:
            return F"https://www.youtube.com/watch?v={self.id}"
        else:
            return F"https://youtu.be/{self.id}"

    def comments(self, limit: int | None = 100) -> AsyncLazy[Comment]:
        return self._youtube.comments(self.id, limit=limit)

    async def channel(self) -> 'Channel':
        return await self._youtube.channel(self.channel_id)

class Playlist:
    _youtube: 'YouTubeData'
    id: str

    def __init__(self, id: str, yt: 'YouTubeData'):
        self._youtube = yt
        self.id = id

    def link(self) -> str:
        return F"https://www.youtube.com/playlist?list={self.id}"

class Channel:
    _youtube: 'YouTubeData'
    id: str

    # part: snippet
    display_name: str
    description: str
    created_at: datetime
    at_username: str
    profile_image_url: str|None = None

    # part: contentDetails
    uploads_playlist: Playlist

    # part: statistics
    view_count: int
    subscriber_count: int
    video_count: int

    @property
    def custom_url(self):
        warn("custom_url is deprecated, please use at_username")
        return self.at_username

    
    @property
    def name(self):
        warn("name is deprecated, please use display_name")
        return self.display_name

    def __init__(self, source: dict[str, Any], yt: 'YouTubeData'):
        self._youtube = yt

        self.id = source['id']
        if snippet := source.get('snippet'):
            self.display_name = snippet['title']
            self.description = snippet['description']
            self.created_at = yt_date(snippet['publishedAt'])
            self.profile_image_url = snippet.get('thumbnails', {}).get('default', {}).get('url')
            self.at_username = snippet.get('customUrl')

        if details := source.get('contentDetails'):
            self.uploads_playlist = Playlist(details['relatedPlaylists']['uploads'], yt)

        if stats := source.get('statistics'):
            self.view_count = int(stats['viewCount'])
            self.subscriber_count = int(stats['subscriberCount'])
            self.video_count = int(stats['videoCount'])

    def link(self) -> str:
        if self.at_username:
            return F"https://www.youtube.com/c/{self.at_username}"
        else:
            return F"https://www.youtube.com/channels/{self.id}"

    async def update(self):
        new = await self._youtube.channel(self.id)
        self.__dict__.update(new.__dict__)

    def videos(self, limit: int|None=None, mine: bool|None=None) -> AsyncLazy[Video]:
        return self._youtube.search_videos(channel_id=self.id, limit=limit, mine=mine)

class YouTubeData(WebAPI):
    base_url = 'https://www.googleapis.com/youtube/v3'

    def __init__(self, app_or_api_key: str|OAuth2|UrlApiKey) -> None:
        match app_or_api_key:
            case str():
                auth = UrlApiKey('key', app_or_api_key)
            case _:
                auth = app_or_api_key
        super().__init__(auth)

    async def my_channel(self, parts: Part=Part.SNIPPET) -> Channel:
        return (await self._channels_list(mine=True, parts=parts, limit=1))[0]

    async def channels(self, channel_ids: list[str], parts: Part) -> list[Channel]:
        return await self._channels_list(channel_ids=channel_ids, parts=parts)

    async def channel(self, channel_id: str, parts: Part=Part.SNIPPET) -> Channel:
        return (await self._channels_list(channel_ids=[channel_id], parts=parts))[0]
    
    async def channel_by_handle(self, handle: str, parts: Part=Part.SNIPPET) -> Channel:
        return (await self._channels_list(handle=handle, parts=parts))[0]
    
    async def channel_by_username(self, username: str, parts: Part=Part.SNIPPET) -> Channel:
        return (await self._channels_list(username=username, parts=parts))[0]
    
    async def channel_by_url(self, url: str, parts: Part=Part.SNIPPET) -> Channel:
        m = RE_CHANNEL_URL.match(url)
        if not m:
            raise ValueError(F"unrecognized channel URL format: {url}")
        if username := m.group('username'):
            return await self.channel_by_username(username, parts)
        elif handle := m.group('handle'):
            return await self.channel_by_handle(handle, parts)
        elif id := m.group('id'):
            return await self.channel(id, parts)

    def _channels_list(self,
        channel_ids: list[str]|None=None,
        handle: str|None=None,
        username: str|None=None,
        mine: bool=False,
        my_managed: bool=False,
        parts: Part|set[Part]=Part.SNIPPET,
        limit: int|None=None) -> AsyncLazy[Channel]:
        maxResults = min(50, limit) if limit else None # per-page limit
        allowed = {
            # TODO: auditDetails, brandingSettings, contentOwnerDetails
            Part.DETAILS,
            Part.ID,
            Part.LOCALIZATIONS,
            Part.SNIPPET,
            Part.STATISTICS,
            Part.STATUS,
            Part.TOPIC_CATEGORIES
        }
        params: ParamsDict = { 'part': parts.intersection(allowed), 'maxResults': maxResults }
        if channel_ids:
            channel_ids = list(set(channel_ids or [])) # deduplicate IDs
            channels_chunks50 = [
                channel_ids[i: i + 50] for i in range(0, len(channel_ids), 50)
            ]
            async def page_chunks():
                for ids in channels_chunks50:
                    p = params | { 'id': ','.join(ids) }
                    async for c in self.paginated('/channels', p, limit):
                        yield c
            return AsyncLazy(page_chunks()).map(lambda r: Channel(r, self))
        else:
            if mine:
                filter = { 'mine': True }
            elif my_managed:
                filter = {'managedByMe': True}
            elif username or handle:
                filter = { 'forHandle': handle, 'forUsername': username }
            else:
                raise ValueError("One of `mine`, `my_managed`, `handle`, or `username` must be specified")
            return self.paginated(
                '/channels', params | filter, limit
                ).map(lambda r: Channel(r, self))

    def videos(self,
        video_ids: list[str],
        parts: Part|set[Part]={Part.ID,Part.SNIPPET}) -> AsyncLazy[Video]:
        parts = parts.intersection(Part.ALL_PUBLIC())
        async def x():
            current = 0
            while current < len(video_ids):
                params: ParamsDict = {
                    'part': parts,
                    'id': ','.join(video_ids[current:current+50]),
                    'maxResults': 50
                }
                async for v in self.paginated(
                    '/videos', params, None
                    ).map(lambda r: Video(r, self)):
                    yield v
                current += 50
        return AsyncLazy(x())

    async def video(self, id: str, parts: Part|set[Part]={Part.ID,Part.SNIPPET}) -> Video:
        return (await self.videos([id], parts))[0]

    def get_playlist_videos(self,
        playlist_id: str, 
        parts: Part|set[Part]={Part.SNIPPET, Part.DETAILS},
        limit: int|None=None) -> AsyncLazy[Video]:
        params: ParamsDict = {
            'part': parts.intersection(
                {Part.ID, Part.SNIPPET, Part.STATUS, Part.DETAILS}),
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
        mine: bool|None=None, # authorized user's channel (via OAuth2)
        order: Order=Order.RELEVANCE,
        safeSearch: SafeSearch=SafeSearch.MODERATE,
        limit: int|None=50) -> AsyncLazy[Video]:
        '''Search for videos matching the search parameters.
        Defaults to 50 most relevant results.
        The `after` parameter is inclusive, so include a small offset for only
        videos published strictly after.
        The `mine` parameter can be used instead of `channel_id` if authorized
        by the channel owner via OAuth2.
        '''
        params: ParamsDict = {
            'part': Part.SNIPPET,
            'safeSearch': safeSearch,
            'order': order,
            'type': 'video',
            'q': query,
            'channelId': channel_id,
            'forMine': mine,
            'publishedAfter': after.astimezone(timezone.utc).isoformat("T")[:-6] + "Z" if after else None,
            'publishedBefore': before.astimezone(timezone.utc).isoformat("T")[:-6] + "Z" if before else None,
            'maxResults': min(50, limit) if limit else None,
        }

        return self.paginated(
            '/search', params, limit
            ).map(lambda r: Video(r, self))

    def comments(self,
        video_id: str,
        query: str|None=None,
        parts: Part|set[Part]={Part.SNIPPET,Part.REPLIES},
        order: CommentOrder=CommentOrder.TIME,
        limit: int|None=None) -> AsyncLazy[Comment]:
        params: ParamsDict = {
            'part': parts.intersection({Part.ID, Part.REPLIES, Part.SNIPPET}),
            'commentOrder': order,
            'searchTerms': query,
            'videoId': video_id,
            'maxResults': min(100, limit) if limit else None,
        }
        return self.paginated(
            '/commentThreads', params, limit
            ) .map(Comment)
    
