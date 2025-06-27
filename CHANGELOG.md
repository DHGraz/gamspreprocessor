# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.2.2] - 2025-02-28

### Changed

- Bump to gamslib 0.5.0, which made subtype a SubType Enum (no longer a str).

## [0.2.1] - 2024-02-12

### Changed

- Refactored projectsplitter

## [0.2.0] - 2024-12-13

### Added

- new subcommand `multitransform`
- new subcommand `project`
  - Use `project init` to create a `project.toml` file

### Changed

- Reflect signature changes in gamslib version 0.3.0
- refactor projectsplitter.py
- impove test coverage 

## [0.2.6] - 2024-12-06

### Added

- CHANGELOG.md
- More tests

### Changed

- Extend pyproject.toml

## [0.2.7] - 2025-05-23

- Add `--exclude` option to multitransform

## [0.2.8] - 2025-

- Add an new option to configuration: 
  `general.ds_ignore_files = ['*.log',]`
- `preprocess csv create/update` now guesses `mainRessource` 
  if there is only one xml data stream besides DC.xml.








