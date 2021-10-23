# Changelog

## [Sprint2](https://github.com/Johnlky/DC-Boxjelly/releases/tag/Sprint2)

### Added
- Added PDF report generating
- Added CSV file exporting
- Added CSV file altering (re-upload)
- Added version control to the constraints file.

### Changed
- Improvement on GUI
  - Made it more readable

### Breaking Changes
- Downgrade the python environment version from 3.9 to 3.6.
  - The development environment (pipenv) is now locked to 3.6
  - It supports both 3.6 and 3.9 as runtime environment.

### Testing
- Fix GUI testing on Python 3.6 environment.

### Docs
- Added operation manual.
- Added installation manual.
- Added necessary documents to README.

## [Sprint1](https://github.com/Johnlky/DC-Boxjelly/releases/tag/Sprint1)

### Added
- Added the storage of Job, Equipment and Run (file system).
- Added importing MEX run.
- Added MEX analysis calculation
- Added MEX analysis charts

### Testing
- Added unit tests of backend logic.
- Added automatic GUI testing.