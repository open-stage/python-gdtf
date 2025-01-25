### Changelog

#### Version 1.0.5

* Library:
    * Add Protocols
    * Add Geometry types: Support, Structure, Display, Magnet
    * Add CRC to file properties
    * Add Thumbnails object (allows to get png and svg thumbnails)
    * Allow to parse description xml directly from an XML file
    * Add default value to DataVersion
    * Link geometry to DMX Mode geometry if link is missing
    * Add Default DMX Mode if missing
    * Add default LogicalChannel and ChannelFunction if missing
    * Convert some RDM codes to int, fix name 
    * Improve Revision date parsing, return as multiple types
    * Change conditionals due to changes in xml.etree (removing the walrus operator)
    * Fix 3DS CRC and extension detection
    * Fix NodeLinks in default LogicalChannels and ChannelFunctions
* Utilities:
    * Allow to (not) include channel functions with channels
    * Rework get dmx channels function to include ChannelFunctions data as dicts
    * Add Get Used Geometries utility function
    * Allow to (not)flatten dmx channels
    * Improve getting DMX Break of GeometryReferences
    * Add get_sorted_revisions utility function
* Packaging, testing, CI/CD:
    * Add python 3.13 and 3.14, including beta to actions
    * Add test for complexity calculation
    * Add ruff test for formatted code
    * Add tests to ensure correct dmx modes/channels processing
    * Improve code and typing to pass mypy --no-strict-optional
    * Convert to pyproject.toml
    * Use uv for python, dependencies, build, publishing

#### Version 1.0.4

* Handle faulty XML files with extra null byte
* Add Laser geometry
* Handle encoded thumbnail file names
* Do not return fixture type when requesting a geometry
* Add additional BeamTypes
* Make channels optional in get_dmx_modes_info
* Add python dev versions to tests
* Improved channel/function defaults, added highlights

#### Version 1.0.3
* First release under Open-Stage organization
    * add CI/CD pytest testing + mypy
* Separating helper methods into utils
    * support Geometry References
    * complexity calculation
    * support Virtual Channels
* Additional supported objects
    * DataVersion, MediaServerCamera, Inventory
    * Wiring Object, DMX Break Overwrite, Geometry Reference
    * MediaServerLayer, MediaServerMaster
* Many additional improvements and fixes 
    * more type hints
    * default values to ColorCIE
    * handle missing data (thumbnails, models)
    * add extension to models
    * added 1.1 PrimitiveTypes

#### Version 1.0.2
* Last release to pypi.org from the original author

#### Version 0.1.0
* First release to pypi.org
