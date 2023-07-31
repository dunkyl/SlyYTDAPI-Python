# Changelog

## [Unreleased]

---

## [0.3.0] - 2023-07-30

Since the last release, YouTube introduced a new username system.
It is important to note that `Comment` in most cases does **not** have the @username of the commenter, and it must instead be retrieved using `YouTubeData.channels` (for many channels at once) or `YouTubeData.channel` (for just one channel at a time).

Commenters are still uniquely identified by `Comment.author_channel_id`.

### Changed
- Reflect YouTube changes to usernames
    - `Channel.name` renamed to `Channel.display_name`
    - `Comment.author_name` renamed to `Comment.author_display_name`
    - `Channel.custom_url` renamed `Channel.at_username` and is never None
    - deprecated properties to access these by their old name

### Fixed
- `Channel.created_at` deserialization format now accepts seconds fraction
- `YouTubeData.channels` no longer bad request when using >50 channel IDs

## [0.2.0] - 2023-03-01

### Changed
- `YouTubeData_WithMembers.get_my_levels` does not accept a parts parameter and always uses ID and SNIPPET
- Updated for SlyAPI 0.4.3
- `YouTubeData_WithMembers` constructor now takes only `OAuth2` 
- `YouTubeData` and `YouTubeData_WithMembers` should no longer be awaited
- `Part`, `PrivacyStatus`, `SafeSearch`, `Order`, and `CommentOrder` are now plain enums
- Many methods now take `T|set[T]` for enum parameters

## [0.1.3] - 2022-02-26

### Changed
- Updated for SlyAPI 0.2.4

## [0.1.2] - 2022-02-23

### Changed
- Updated for SlyAPI 0.2.0

## [0.1.1] - 2022-02-13

### Fixed
- `YouTubeData` constructor
- `Video.link()` if video came from search results

## [0.1.0] - 2021-11-24

### Changed
- Updated for SlyAPI 0.1.0

## [0.0.3] - 2021-11-22

Initial release.