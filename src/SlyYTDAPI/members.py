'''
YouTube Members Endpoints for the Data API v3
https://developers.google.com/youtube/v3/docs/members
'''
from datetime import datetime
from enum import Enum
from typing import Any, TypedDict, cast
from SlyAPI.oauth2 import OAuth2
from SlyAPI import *
from SlyAPI.web import JsonMap, ParamsDict
from .ytdapi import YouTubeData, Part, yt_date

class _MembersPollResponse(TypedDict):
    kind: str
    etag: str
    nextPageToken: str
    pageInfo: dict[str, int]
    items: list[dict[str, Any]]

class _MembersLevelsResponse(TypedDict):
    kind: str
    etag: str
    items: list[dict[str, Any]]

class MembersMode(Enum):
    ALL_CURRENT = 'all_current'
    UPDATES = 'updates'

class MemberLevel:
    # part: id
    id: str
    # part: snippet
    name: str

    def __init__(self, source: JsonMap):
        match source:
            case { # from /membershipsLevels endpoint
                'id': str(id),
                'snippet': {
                    'levelDetails': {
                        'displayName': str(name)
                    } } }:
                self.id = id
                self.name = name
            case { # as part of Member resource
                'highestAccessibleLevel': str(id),
                'highestAccessibleLevelDisplayName': str(name)
            }:
                self.id = id
                self.name = name
            case _:
                raise ValueError(f'Invalid source: {source}')

class Membership:
    # part: snippet
    channel_id: str
    channel_name: str
    profile_image_url: str
    level: MemberLevel
    since: datetime
    total_months: int
    since_at_level: datetime
    total_months_at_level: int

    def __init__(self, source: dict[str, Any]):

        snippet = source['snippet']
        self.channel_id = snippet['memberDetails']['channelId']
        self.channel_name = snippet['memberDetails']['displayName']
        self.profile_image_url = snippet['memberDetails']['profileImageUrl']
        self.level= MemberLevel(snippet['membershipsDetails'])
        self.since = yt_date(snippet['membershipsDuration']['memberSince'])
        self.total_months = snippet['membershipsDuration']['memberTotalDurationMonths']
        self.since_at_level = yt_date(snippet['membershipsDurationAtLevel']['memberSince'])
        self.total_months_at_level = snippet['membershipsDurationAtLevel']['memberTotalDurationMonths']
        
class YouTubeData_WithMembers(YouTubeData):

    _next_page: str|None = None

    def __init__(self, auth: OAuth2) -> None:
        super().__init__(auth)
    
    def get_my_members(self,
        level_id: str|None=None,
        member_channel_ids: list[str]|None=None,
        limit: int|None=None) -> AsyncTrans[Membership]:
        if member_channel_ids is not None and len(member_channel_ids) > 100:
            raise ValueError('Cannot fetch more than 100 specific members.')
        mode = MembersMode.ALL_CURRENT
        params: ParamsDict = {
            'part': Part.SNIPPET,
            'mode': mode,
            'hasAccessToLevel': level_id,
            'filterByMemberChannelId': ','.join(member_channel_ids or []),
            'maxResults': 1000 if limit is None else min(1000, limit)
        }
        return self.paginated(
            '/members', params, limit
            ).map(Membership)
    
    async def _members_poll(self, pageToken: str|None) -> _MembersPollResponse:
        params: ParamsDict = {
            'part': Part.SNIPPET,
            'membersMode': MembersMode.UPDATES,
            'pageToken': pageToken
        }
        return cast(_MembersPollResponse, await self.get_json('/members', params))
    
    async def _memberships_levels(self, parts: Part|set[Part]) -> _MembersLevelsResponse:
        params = { 'part': parts.intersection({Part.ID, Part.SNIPPET}) }
        return cast(_MembersLevelsResponse, await self.get_json('/membershipsLevels', params))

    async def poll_new_members(self) -> list[Membership]:
        '''Polls for new members since the last call to this method.'''
        if self._next_page is None:
            # first call for 'updates' mode does not return any members
            # but it does return a nextPageToken always
            self._next_page = (await self._members_poll(None))['nextPageToken']
            return []
        else:
            response = await self._members_poll(self._next_page)
            self._next_page = response['nextPageToken']
            return [Membership(r) for r in response['items']]

    async def get_my_levels(self) -> list[MemberLevel]:
        return [MemberLevel(r) for r in (await self._memberships_levels({Part.ID,Part.SNIPPET}))['items']]