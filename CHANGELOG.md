### Changelog

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
