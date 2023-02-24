from datetime import datetime
from enum import Enum
from typing import Any
from SlyAPI.oauth2 import OAuth2
from SlyAPI import *
from SlyAPI.web import JsonMap
from .ytdapi import YouTubeData, Part, yt_date

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
            case {
                'id': str(id),
                'snippet': {
                    'levelDetails': {
                        'displayName': str(name)
                    } } }:
                self.id = id
                self.name = name
            case {
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
        parts: Part|set[Part]=Part.SNIPPET,
        limit: int|None=None) -> AsyncTrans[Membership]:
        if member_channel_ids is not None and len(member_channel_ids) > 100:
            raise ValueError('Cannot fetch more than 100 specific members.')
        mode = MembersMode.ALL_CURRENT
        params = {
            'part': parts,
            'mode': mode,
            'hasAccessToLevel': level_id,
            'filterByMemberChannelId': ','.join(member_channel_ids or []),
            'maxResults': 1000 if limit is None else min(1000, limit)
        }
        return self.paginated(
            '/members', params, limit
            ).map(Membership)

    async def poll_new_members(self) -> list[Membership]:
        '''Polls for new members since the last call to this method.'''
        if self._next_page is None:
            # TODO: this doesn't seem right, please review
            self._next_page = (await self.get_json('/members'))['nextPageToken']
            return []
        else:
            params = {
                'part': Part.SNIPPET,
                'membersMode': MembersMode.UPDATES,
                'pageToken': self._next_page
            }
            response = await self.get_json('/members', params)
            self._next_page = response['nextPageToken']
            return [Membership(r) for r in response['items']]

    async def get_my_levels(self, parts: Part|set[Part]={Part.ID,Part.SNIPPET}) -> list[MemberLevel]:
        params = { 'part': parts }
        levels = await self.get_json('/membershipsLevels', params)
        return [MemberLevel(r) for r in levels['items']]