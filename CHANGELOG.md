### Changelog

#### Version 1.1.0

Big sweeping changes to make the library to return proper structures by default
without having to use the .utils package:

    * Generally, the .utils should not be needed and should not be used
      anymore, most methods have been moved as class methods of the main
      parser.

    * ⚠️  List of DMX Channels provided by dmx\_mode.dmx\_channels is now a
      complete list of all DMX channels calculated by obtaining DMX channels
      for geometries, Geometry References and so on, no need to use the .utils
      methods.

    * ⚠️  The list of channels as dictionaries can be obtained by
      dmx\_mode.dmx\_channels.as\_dicts(), the "id" has been renamed to
      "attribute".

    * ⚠️  Many of the .utils package methods have been moved directly to the
      main part of pygdtf. External usage of methods from .util should not be
      needed anymore.  The previously provided get methods can be replaced by
      snippets like below, allowing greater customization and possible less
      future code breakage.

    * Migration steps:

##### .utils.get\_dmx\_modes\_info

```python
modes_info = []

for idx, mode in enumerate(gdtf_fixture.dmx_modes):
    dmx_mode_info = {
        "mode_id": idx,
        "mode_name": mode.name,
        "mode_dmx_channel_count": mode.dmx_channels_count,
        "mode_virtual_channel_count": mode.virtual_channels_count,
        "mode_dmx_breaks_count": mode.dmx_breaks_count,
        "mode_dmx_channels": mode.dmx_channels.as_dicts(),
        "mode_virtual_channels": mode.virtual_channels.as_dicts(),
    }
    modes_info.append(dmx_mode_info)
```

##### .utils.get\_geometry\_by\_name

```python
gdtf_fixture.geometries.get_geometry_by_name("geometry name")
```

##### .utils.get\_geometry\_by\_type

```python
#this is a static method and requires a root_geometry
gdtf_fixture.geometries.get_geometry_by_type(geometry_root, geometry_type)


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
