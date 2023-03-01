# Changelog

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