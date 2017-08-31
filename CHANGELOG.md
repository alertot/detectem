Change Log
==========

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

Unreleased
----------

0.6.0 - 2017-08-31
------------------
### Added
- Options to set Splash timeout
- Detect software on inline scripts
- Support for custom plugins
- A from_url field to the output metadata

### Changed
- Better error handling
- Do not run JS matchers when site uses Content Security Policy
- Disable loading images on Splash
- Use names when listing hints
- Sort detected plugins by name and version
- Remove duplicated plugins from detection results

0.5.2 - 2017-03-24
------------------
### Changed
- Refactor of result types
- Blacklist in HAR results
- Output improvement

0.5.1 - 2017-03-23
------------------
### Added
- Concept of hints
- Documentation about modular matchers
- Two Joomla plugins

### Changed
- Plugin interface to make it more flexible

0.5.0 - 2017-03-20
------------------
### Added
- Concept of indicators
- Documentation about modular matchers

### Fixed
- Tests

0.4.5 - 2017-03-15
------------------

0.4.4 - 2017-03-15
------------------

### Fixed
- Header detection

0.4.3 - 2017-03-15
------------------
### Added
- Documentation for the project
- MooTools plugins
- Add modular plugins support
- Angular.js plugin

### Changed
- Improved add_new_plugin to be easy to create a plugin
- Refactored core components

0.4.2 - 2017-02-13
------------------
### Added
- A new plugin
- Javascript support through LUA script
- Tests for new javascript feature
- New d3.js plugin

### Changed
- Replace spaces by dash in plugin names
- contact-form-7 location

### Fixed
- Tests

0.4.1 - 2017-02-13
------------------
### Added
- jquery_migrate plugin
- Better error handling

0.4.0 - 2017-02-12
------------------
### Added
- Plugin metadata
- Javascript support through LUA script
- Tests for new javascript feature
- New d3.js plugin

### Changed
- Updated requirements file

0.3.0 - 2016-12-27
------------------
### Added
- Web service
- Support to configure Splash from environment variables

0.2.0 - 2016-12-21
------------------
### Added
- Some new plugins

### Changed
- Updated to use docker 2.0 library
- Improved docker decorator

0.1.3 - 2016-11-18
------------------
### Added
- Some new plugins

### Changed
- Updated add_new_plugin script with latest changes

### Fixed
- Response body decoding

0.1.2 - 2016-11-16
------------------
### Added
- Some attributes to Plugin interface
- Some new plugins
- Script to create plugins faster

### Fixed
- jQuery plugin

0.1.1 - 2016-11-15
------------------
### Fixed
- Travis setup and setup.py

0.1.0 - 2016-11-15
------------------
### Added
- Initial version
