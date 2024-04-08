# Changelog
All notable changes to this project will be documented in this file.

The format is inspired from [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and the versioning aim to respect [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

Here is a template for new release sections

## [Unreleased]
### Added
- initial cluster docs

## [1.4.0] - 2024-03-26
### Added
- error message if region zoom level does not work with distill zoom level

### Changed
- layers are activated by their full name, not beginning of name; cluster activation is adapted

## [1.3.0] - 2024-03-20
### Changed
- env names for distilling and tileservice

### Fixed
- min/max zoom in map setup
- distill offset factor

## [1.2.2] - 2024-03-19
### Fixed
- distilled sources for layers referencing region MVTs

## [1.2.1] - 2024-03-19
### Fixed
- range-key-dict dependency

## [1.2.0] - 2024-03-19 (BROKEN)
### Fixed
- distilling

## [1.1.0] - 2024-03-14
### Added
- error message for missing layer style
- layers reuse other sources and source layers if model managers match

### Changed
- remove unnecessary model reference in ModelLayer class and Legend

## [1.0.0] - 2024-03-07
### Added
- clean layer activation

### Changed
- removed legacy layer handling

## [0.19.0] - 2024-03-04
### Changed
- remove colorbrewer dependency and implement colors locally

## [0.18.3] - 2024-03-01
### Fixed
- popups above choropleths

## [0.18.2] - 2024-02-20
### Fixed
- version check at image loading

## [0.18.1] - 2024-02-20
### Fixed
- distill refactoring

## [0.18.0] - 2024-02-20
### Fixed
- map image loading for maplibre version > 2.4.0

## [0.17.0] - 2024-02-20
### Fixed
- remove upper constraint for django-environ dependency

## [0.16.0] - 2024-02-12
### Fixed
- prevent empty popup on double-clicking a layer

## [0.15.0] - 2024-02-02
### Changed
- make basemap optional

## [0.14.0] - 2024-02-02
### Added
- toggle legend visibility on choropleth (de)activation

## [0.13.2] - 2023-08-23
### Fixed
- map store initialization

## [0.13.1] - 2023-07-13
### Fixed
- choropleth legend unit brackets

## [0.13.0] - 2023-07-05
### Added
- cluster properties to forward model attributes to map engine

## [0.12.0] - 2023-06-27
### Changed
- layer ordering; cluster layers are shown on top of other layers

## [0.11.0] - 2023-06-15
### Changed
- chart creation function must be declared by project app

### Fixed
- chart errors in popups

## [0.10.0] - 2023-06-12
### Changed
- chart options are taken from backend; no frontend modifications

### Fixed
- no choropleths set in settings

## [0.9.0] - 2023-06-09
### Added
- title and unit for choropleths in legend

## [0.8.0] - 2023-05-02
### Added
- default choropleth config

## [0.7.0] - 2023-04-27
### Added
- popup template

## [0.6.0] - 2023-04-27
### Added
- map state information is send for popups and choropleths

## [0.5.0] - 2023-04-26
### Changed
- lower and upper bounds for numbers in legend

## [0.4.2] - 2023-03-30
### Fixed
- map urls for projects using i18n patterns

## [0.4.1] - 2023-03-24
### Fixed
- choropleth legend

## [0.4.0] - 2023-03-24
### Changed
- refactored popups to work in combination with choropleths

## [0.3.0] - 2023-03-24
### Added
- layer style lookup to utils and legend layer

### Changed
- refactored choroplehts

## [0.2.0] - 2023-03-23
### Added
- sources, layers and API interfaces are built from settings

## [0.1.0] - 2023-03-01
### Added
- initial running map engine
