from ytdapi import YouTubeData, Scope, Part

class MemberLevel: pass
class Membership: pass

class YouTubeData_WithMembers(YouTubeData):
    
    def __init__(self, scope: Scope):
        super().__init__(scope)
        if not Scope.YouTubeMembers in Scope:
            raise ValueError("Access you youtube members requires the members scope.")
        # super().__init__(scope)

    async def get_channel_members(self,
        level_id: str|None=None,
        member_channel_ids: list[str]|None=None,
        parts: Part=Part.Snippet,
        limit: int|None=None):
        if member_channel_ids is not None and len(member_channel_ids) > 100:
            raise ValueError('Cannot fetch more than 100 specific members.')
        params = {
            **parts.to_dict(),
            'hasAccessToLevel': level_id,
            'member_channel_ids': ','.join(member_channel_ids or []),
            'maxResults': 1000 if limit is None else min(1000, limit)
        }
        return [Membership(r, self) for r in await self.paginated(
            self.get_json, '/members', params,
            limit = limit, page_size=1000,
        )]

    async def get_levels(self, parts: Part=Part.Snippet):
        params = parts.to_dict()
        return [MemberLevel(r, self) for r in await self.get_json('/members', params)