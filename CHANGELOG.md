### Changelog

#### 1.2.6

* Make physical\_from/\_to a PhysicalValue object with properties
* To get physical values, use physical\_from.value and physical\_to.value

#### Version 1.2.5

* Handle parsing of incorrect DmxValue values
* Return default FixtureType if ElementTree.fromstring fails on malformed XML

#### Version 1.2.4

* Handle Highlight parsing when "none" is incorrectly supplied

#### Version 1.2.3

* Add ChannelSet physical values processing
* Set undefined WheelSlotIndex as 0 not as 1
* Improve Resource parsing

#### Version 1.2.0

Adjustments to the previous re-work, affecting the following:

- Revisions:
    - fixture\_type.revisions now returns Revisions()
    - added method as\_dict
    - sorted is now reversed by default
- DmxMode:
    - dmx\_breaks\_count has been replaced by dmx\_breaks which contains channel
      count and the break value
- DmxChannels:
    - added as\_dict to by\_breaks

#### Version 1.1.0

Big changes to make the library to return proper structures by default without
having to use the .utils package. See more details below.

##### New additions:

* Context manager:

    * The FixtureType can now also be used as a context manager.

    ```python
    with pygdtf.FixtureType("fixture.gdtf") as gdtf_fixture:
        print(gdtf_fixture.name)
    ````

    The original behavior is still possible:

    ```python
    gdtf_fixture = pygdtf.FixtureType("/tmp/spiider.gdtf")
    print(gdtf_fixture.name)
    # make sure to close the zip file which got open...
    gdtf_fixture._package.close()
    ```

* Calculating DMX To in Channel Functions and Channel Sets

    * ChannelFunctions and ChannelSets in GDTF files only provide DMX From, to
      ensure that user created data does not have gaps/overlaps. Pygdtf now
      calculates the DMX To values for convenience.

* DMX Channel default and attribute fields

    * DMX Channel still has `default` field in pygdtf, which has been
      deprecated in GDTF 1.2 by a link to the Initial Channel Function and a
      default value there.  The `default` field in DMX Channel is THE default
      value as provided by the Initial Channel Function, for convenience.

    * Same with the `attribute` field, which for convenience is provided from
      the first Logical Channel.

* Output data as dict

    * DMX Modes, Channels, Logical Channels, Channel Functions, Channel Sets
      now have as\_dict method to provide dictionary based output to interop
      with javascript and so on. The as\_dict methods are not 100% complete,
      more fields are to be added over time.

* LogicalChannels in dictionary structure

    * Previous .utils methods skipped LogicalChannels completely, these are now added.

##### Big compatibility changes:

* Generally, the .utils should not be needed and should not be used anymore
  (with some exceptions), most methods have been moved as class methods of the
  main parser.

* ⚠️  List of DMX Channels provided by dmx\_mode.dmx\_channels is now a
  complete list of all DMX channels calculated by obtaining DMX channels
  for geometries, Geometry References and so on, no need to use the .utils
  methods anymore.

* ⚠️  The list of channels as dictionaries can be obtained by
  dmx\_mode.dmx\_channels.as\_dict(), the "id" has been renamed to
  "attribute".  DMX Channel now contains Logical Channels and then Channel
  Functions. The as\_dict() is now also in dmx\_modes, dmx\_mode,
  dmx\_channels and so on.

* ⚠️  Many of the .utils package methods have been moved directly to the
  main part of pygdtf. External usage of methods from .utils should not be
  needed anymore.

* Migration steps, instead of the .utils methods, use the default parser
  provided methods:

##### .utils.get\_dmx\_modes\_info

```python
modes_info = gdtf_fixture.dmx_modes.as_dict()

```

##### .utils.get\_geometry\_by\_name

```python
gdtf_fixture.geometries.get_geometry_by_name("geometry name")
```

##### .utils.get\_geometry\_by\_type

```python
#this is a static method and requires a root_geometry
gdtf_fixture.geometries.get_geometry_by_type(geometry_root, geometry_type)
```

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
