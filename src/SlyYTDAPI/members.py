from datetime import datetime
from typing import Any
from SlyAPI.oauth2 import OAuth2User
from SlyAPI import AsyncTrans, EnumParam
from .ytdapi import YouTubeData, Scope, Part, yt_date

class MembersMode(EnumParam):
    ALL_CURRENT = 'all_current'
    UPDATES = 'updates'

class MemberLevel:
    # part: id
    id: str
    # part: snippet
    name: str

    def __init__(self, source: dict[str, Any]):
        match source:
            case {'id': id, 'snippet': snippet}:
                self.id = id
                self.name = snippet['creatorChannelId']
            case {
                'highestAccessibleLevel': id,
                'highestAccessibleLevelDisplayName': name
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

    _poll_next_page_token: str|None = None
    
    async def _async_init(self, auth: str|OAuth2User, scope: Scope=Scope.MEMBERS):
        if not Scope.MEMBERS in Scope: # todo: implement 'in' for EnumParam
            raise ValueError("Access you youtube members requires the members scope.")
        await super()._async_init(auth, scope)
        

    def get_my_members(self,
        level_id: str|None=None,
        member_channel_ids: list[str]|None=None,
        parts: Part=Part.SNIPPET,
        limit: int|None=None) -> AsyncTrans[Membership]:
        if member_channel_ids is not None and len(member_channel_ids) > 100:
            raise ValueError('Cannot fetch more than 100 specific members.')
        mode = MembersMode.ALL_CURRENT
        params = {
            **(parts+mode).to_dict(),
            'hasAccessToLevel': level_id,
            'filterByMemberChannelId': ','.join(member_channel_ids or []),
            'maxResults': 1000 if limit is None else min(1000, limit)
        }
        return self.paginated(
            '/members', params, limit
            ).map(Membership)

    async def poll_new_members(self) -> list[Membership]:
        if self._poll_next_page_token is None:
            self._poll_next_page_token = (await self.get_json('/members'))['nextPageToken']
            return []
        else:
            params = {
                **(Part.SNIPPET+MembersMode.UPDATES).to_dict(),
                'pageToken': self._poll_next_page_token
            }
            response = await self.get_json('/members', params)
            self._poll_next_page_token = response['nextPageToken']
            return [Membership(r) for r in response['items']]

    async def get_my_levels(self, parts: Part=Part.ID+Part.SNIPPET) -> list[MemberLevel]:
        params = parts.to_dict()
        levels = await self.get_json('/membershipsLevels', params)
        return [MemberLevel(r) for r in levels['items']]