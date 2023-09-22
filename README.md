# python-gdtf

Python library for [General Device Type Format](https://gdtf-share.com/)

GDTF specification as per https://gdtf.eu/gdtf/prologue/introduction/

See source code for documentation. Naming conventions, in general, are
identical to that on the GDTF, CamelCase is replaced with
underscore_delimiters.

## Credits

Originally [created](https://github.com/jackdpage/python-gdtf) by [Jack
Page](https://github.com/jackdpage). Forked to
[Open-Stage](https://github.com/open-stage), used for example by
[BlenderDMX](https://github.com/open-stage/blender-dmx).

[Source code](https://github.com/open-stage/python-gdtf)

[PyPi page](https://pypi.org/project/pygdtf/)

[![Pytest](https://github.com/open-stage/python-gdtf/actions/workflows/run-tests.yaml/badge.svg)](https://github.com/open-stage/python-gdtf/actions/workflows/run-tests.yaml)

[![Check links in markdown](https://github.com/open-stage/python-gdtf/actions/workflows/check-links.yaml/badge.svg)](https://github.com/open-stage/python-gdtf/actions/workflows/check-links.yaml)

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

# get info about DMX Modes:
pygdtf.utils.get_dmx_modes_info(gdtf_fixture)

# [{'mode_id': 0,
#  'mode_name': 'Default',
#  'mode_dmx_channel_count': 5,
#  'mode_virtual_channel_count': 0}]

# get list of DMX channels with geometries, channels functions
pygdtf.utils.get_dmx_channels(gdtf_fixture, "Default")

# [[{'dmx': 1,
#   'id': 'Dimmer',
#   'default': 0,
#   'geometry': 'Beam',
#   'break': 1,
#   'channel_functions': [<pygdtf.ChannelFunction at 0x7f122435c8b0>]},
#  {'dmx': 2,
#   'id': 'ColorAdd_R',
#   'default': 255,
#   'geometry': 'Beam',
#   'break': 1,
#   'channel_functions': [<pygdtf.ChannelFunction at 0x7f122435e860>]},
#  {'dmx': 3,
#   'id': 'ColorAdd_G',
#   'default': 255,
#   'geometry': 'Beam',
#   'break': 1,
#   'channel_functions': [<pygdtf.ChannelFunction at 0x7f122435f0d0>]},
#  {'dmx': 4,
#   'id': 'ColorAdd_B',
#   'default': 255,
#   'geometry': 'Beam',
#   'break': 1,
#   'channel_functions': [<pygdtf.ChannelFunction at 0x7f1224e56c20>]},
#  {'dmx': 5,
#   'id': 'ColorAdd_W',
#   'default': 0,
#   'geometry': 'Beam',
#   'break': 1,
#   'channel_functions': [<pygdtf.ChannelFunction at 0x7f122435fdf0>]}]]

```

See [BlenderDMX](https://github.com/open-stage/blender-dmx) and
[tests](https://github.com/open-stage/python-gdtf/tree/master/tests) for
reference implementation.

## Usage principles

- for list of channels, use `pygdtf.utils.get_dmx_channels` as per example
  above, do not presume that plain layout of DMX Channels in a DMX Mode is
  defining the DMX footprint of the device. Geometry references are
  (frequently) used to re-use parts of the device. This means that a channel(s)
  defined once can be multiplied, over several times duplicated geometry
  (tree).

- do not use geometry names for anything related to function of the geometry
  (yoke, pan, tilt, head), use attached GDTF attributes ("Pan", "Tilt")

- only Beam, Camera and Wiring geometry types are currently used special types of
  geometry. Other types (Axis...) are not really relevant as even Normal
  geometry can have for example "Pan" GDTF attribute attached, to indicate
  movement.

## Status

- GDTF 1.1 with some portions of GDTF 1.2 being included

## Development

PRs appreciated.

### Typing

* At this point, the `--no-strict-optional` is needed for mypy tests to pass:

```bash
mypy pygdtf/*py  --pretty  --no-strict-optional
```
### Format

- to format, use [black](https://github.com/psf/black))

### Testing

- to test, run: `pytest`
- to test typing with mypy run pytest:

```bash
pytest --mypy -m mypy pygdtf/*py
```
