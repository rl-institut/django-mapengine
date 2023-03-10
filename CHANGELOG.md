# Changelog
All notable changes to this project will be documented in this file.

The format is inspired from [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and the versioning aim to respect [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

Here is a template for new release sections

## [0.2.0] - 2023-02-22
### Added
- hooks for parameters, energysystem and model

## [0.1.0] - 2023-01-01
### Added
- oemof ES can be built using datapackages
- energysystem build can be adapted using user parameters
- energysystem can be simulated within multiprocess
- results from simulation are stored in database
- simulation is not re-run in case of already existing results in DB
- calculations from (oemoflex, in future oemof.tabular) can be made
- calculations are stored in database and can be restored
