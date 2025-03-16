# python-gdtf

Python library for [General Device Type Format](https://gdtf-share.com/)

GDTF specification as per https://gdtf.eu/gdtf/prologue/introduction/

See source code for documentation. Naming conventions, in general, are
identical to that on the GDTF, CamelCase is replaced with
underscore_delimiters.

## Credits

Originally [created](https://github.com/jackdpage/python-gdtf) by [Jack
Page](https://github.com/jackdpage). Friendly forked to
[Open-Stage](https://github.com/open-stage) by
[vanous](https://github.com/vanous). We continue publishing to pypi under the
same [pygdtf](https://pypi.org/project/pygdtf/) name with Jack's permission.

Used for example by [BlenderDMX](https://github.com/open-stage/blender-dmx).

[Source code](https://github.com/open-stage/python-gdtf)

[PyPi page](https://pypi.org/project/pygdtf/)

[![Pytest](https://github.com/open-stage/python-gdtf/actions/workflows/run-tests.yaml/badge.svg)](https://github.com/open-stage/python-gdtf/actions/workflows/run-tests.yaml)

[![Check links in markdown](https://github.com/open-stage/python-gdtf/actions/workflows/check-links.yaml/badge.svg)](https://github.com/open-stage/python-gdtf/actions/workflows/check-links.yaml)

## Important changes

### Version 1.1.0

⚠️  List of DMX Channels provided by dmx\_mode.dmx\_channels is now a complete
list of all DMX channels calculated by obtaining DMX channels for geometries,
Geometry References and so on, no need to use the .utils methods.

⚠️  The list of channels as dictionaries can be obtained by
dmx\_mode.dmx\_channels.as\_dicts(), the "id" has been renamed to "attribute".

⚠️  Many of the .utils package methods have been moved directly to the main part
of pygdtf. External usage of methods from .util should not be needed anymore.
The previously provided get methods can be replaced by snippets like below,
allowing greater customization and possible less future code breakage:

#### .utils.get\_dmx\_modes\_info

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

#### .utils.get\_geometry\_by\_name

```python
gdtf_fixture.geometries.get_geometry_by_name("geometry name")
```

#### .utils.get\_geometry\_by\_type

```python
#this is a static method and requires a root_geometry
gdtf_fixture.geometries.get_geometry_by_type(geometry_root, geometry_type)

```
## Installation

```bash
pip install pygdtf
```

To install latest version from this git repository, run pip:

```bash
python -m pip install https://codeload.github.com/open-stage/python-gdtf/zip/refs/heads/master
```

## Usage

```python
# import
import pygdtf

# parse a GDTF file
gdtf_fixture = pygdtf.FixtureType("BlenderDMX@LED_PAR_64_RGBW@v0.3.gdtf")

# one can also parse just a description.xml file during development or testing
gdtf_fixture = pygdtf.FixtureType(dsc_file="description.xml")

# now access things like DMX modes, channels and so on
# get DMX Mode name
gdtf_fixture.dmx_modes[0].name
'Mode 1 - Standard 16 - bit'

# get number of DMX channels
gdtf_fixture.dmx_modes[0].dmx_channels_count
39

# get number of Virtual channels
gdtf_fixture.dmx_modes[0].virtual_channels_count
0

# get number of DMX breaks
gdtf_fixture.dmx_modes[0].dmx_breaks_count
1

# get DMX channels as objects gdtf_fixture.dmx_modes[0].dmx_channels
<pygdtf.DmxChannel object at 0x7f789c63bb60>, <pygdtf.DmxChannel object at
0x7f789c375590>, <pygdtf.DmxChannel object at 0x7f789c375a90>,...

# get DMX channels as dict
gdtf_fixture.dmx_modes[0].dmx_channels.as_dicts()

[[{'dmx': 1, 'offset': [1, 2], 'id': 'Pan', 'default': 128, 'highlight': None,
'geometry': 'Yoke', 'break': 1, 'parent_name': 'Base', 'channel_functions':
[{'name': 'Pan', 'attribute': 'Pan', 'dmx_from': 0, 'dmx_to': 255, 'default':
128, 'real_fade': 1.833, 'physical_to': 270.0, 'physical_from': -270.0,
'channel_sets': ['', 'Center', '']}, ...

# see the source code for more methods
```

See [BlenderDMX](https://github.com/open-stage/blender-dmx) and
[tests](https://github.com/open-stage/python-gdtf/tree/master/tests) for
reference implementation and usage examples.

## Usage principles

- do not use geometry names for anything related to function of the geometry
  (yoke, pan, tilt, head), use attached GDTF attributes ("Pan", "Tilt") to know
  what functions should the geometry perform

## Status

- Many GDTF 1.2 features have been implemented
- Some GDTF 1.1 features have been kept in

## Development

PRs appreciated. You can use [uv](https://docs.astral.sh/uv/) to get the
project setup by running:

```bash
uv sync
```

### Typing

- We try to type the main library as well as the utils module, to test run:

```bash
mypy pygdtf/**py  --pretty
```

### Format

- To format, use [black](https://github.com/psf/black) or
  [ruff](https://docs.astral.sh/ruff/)

### Testing

- to test, run: `pytest`
- to test typing with mypy run pytest:

```bash
pytest --mypy -m mypy pygdtf/**py
```
