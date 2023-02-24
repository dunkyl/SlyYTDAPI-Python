# Changelog

## [Unreleased]

### Changed
- Updated SlyAPI
- `YouTubeData_WithMembers` constructor now takes only `OAuth2` 
- `YouTubeData` and `YouTubeData_WithMembers` should no longer be awaited
- `Part`, `PrivacyStatus`, `SafeSearch`, `Order`, and `CommentOrder` are now plain enums
- Many methods now take `T|set[T]` for enum parameters