# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0]

### Added

- Support for reading from file streams - including stdin [[#2][2]]
- Support for reading from `gzip`-compressed files [[#5][5]]

### Changed

- Calling `open()` on an already-open `PafFile` will no longer raise and error, but
  returns the (unchanged) `PafFile` object it was called on.

## [0.1.3]

### Fixed

- Tags not being correctly converted to strings when converting a `PafRecord` to a
  string [[#4][4]]

## [0.1.2]

### Fixed

- handle `inf` float values ([@lucventurini](https://github.com/lucventurini))

## [0.1.1] - 2020-05-16

### Added

- This CHANGELOG file.

### Changed

- Don't rely on `poetry` to get version.

[0.1.1]: https://github.com/mbhall88/pafpy/releases/tag/0.1.1
[0.1.2]: https://github.com/mbhall88/pafpy/releases/tag/0.1.2
[0.1.3]: https://github.com/mbhall88/pafpy/releases/tag/0.1.3
[0.2.0]: https://github.com/mbhall88/pafpy/releases/tag/0.2.0
[2]: https://github.com/mbhall88/pafpy/issues/2
[4]: https://github.com/mbhall88/pafpy/issues/4
[5]: https://github.com/mbhall88/pafpy/issues/5
[Unreleased]: https://github.com/snakemake/snakefmt/compare/0.1.3...HEAD

