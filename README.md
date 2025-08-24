# python-gdtf

Python library for [General Device Type Format](https://gdtf-share.com/)

GDTF specification as per https://gdtf.eu/gdtf/prologue/introduction/

See source code for documentation. Naming conventions, in general, are
identical to that on the GDTF, CamelCase is replaced with
underscore\_delimiters.

## Credits

Originally [created](https://github.com/jackdpage/python-gdtf) by [Jack
Page](https://github.com/jackdpage). Friendly forked to
[Open-Stage](https://github.com/open-stage) by
[vanous](https://github.com/vanous). We continue publishing to pypi under the
same [pygdtf](https://pypi.org/project/pygdtf/) name with Jack's permission.

This library is used for example by [BlenderDMX](https://blenderdmx.eu)
([BlenderDMX on GitHub](https://github.com/open-stage/blender-dmx)).

[GitHub Page](https://github.com/open-stage/python-gdtf), [PyPi Page](https://pypi.org/project/pygdtf/)

[![Pytest](https://github.com/open-stage/python-gdtf/actions/workflows/run-tests.yaml/badge.svg)](https://github.com/open-stage/python-gdtf/actions/workflows/run-tests.yaml)
[![Check links in markdown](https://github.com/open-stage/python-gdtf/actions/workflows/check-links.yaml/badge.svg)](https://github.com/open-stage/python-gdtf/actions/workflows/check-links.yaml)
![GitHub Tag](https://img.shields.io/github/v/tag/open-stage/python-gdtf)

## Important changes when updating from 1.0

⚠️  List of DMX Channels provided by dmx\_mode.dmx\_channels is now a complete
list of all DMX channels calculated by obtaining DMX channels for geometries,
Geometry References and so on, no need to use the .utils methods anymore.

⚠️  The list of channels as dictionaries can be obtained by
dmx\_mode.dmx\_channels.as\_dicts(), the "id" has been renamed to "attribute".
DMX Channel now contains Logical Channels and then Channel Functions. The
as\_dict() is now also in dmx\_modes, dmx\_mode, dmx\_channels and so on.

⚠️  Many of the .utils package methods have been moved directly to the main part
of pygdtf. External usage of methods from .utils should not be needed anymore.

See [CHANGELOG](https://github.com/open-stage/python-gdtf/blob/master/CHANGELOG.md) for details.

## Status

- Reading of most aspects of GDTF 1.2 (DIN SPEC 15800:2022-02) should be covered.
- Writing is currently not implemented.

## Installation

- With uv:

```bash
uv add pygdtf
```

- With pip

```bash
pip install pygdtf
```

### Latest development version (if exists on pypi.org)

```bash
uv add pygdtf --pre
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

# get total number of DMX channels
gdtf_fixture.dmx_modes[0].dmx_channels_count
39

# get number of Virtual channels
gdtf_fixture.dmx_modes[0].virtual_channels_count
0

# get DMX breaks and DMX channels count:
gdtf_fixture.dmx_modes[0].dmx_breaks[0].dmx_break
1

gdtf_fixture.dmx_modes[0].dmx_breaks[0].channels_count
39

# get DMX channels as objects gdtf_fixture.dmx_modes[0].dmx_channels
<pygdtf.DmxChannel object at 0x7f789c63bb60>, <pygdtf.DmxChannel object at
0x7f789c375590>, <pygdtf.DmxChannel object at 0x7f789c375a90>,...

# get DMX channels as dict
gdtf_fixture.dmx_modes[0].dmx_channels.as_dict()

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

## Development

PRs appreciated. You can use [uv](https://docs.astral.sh/uv/) to get the
project setup by running:

```bash
uv sync
```

### Format

- To format, use [ruff](https://docs.astral.sh/ruff/)

```bash
uv run ruff format pygdtf/*
```

### Pre-commit hooks

- You can use the pre-commit hooks

```bash
uv run pre-commit install
```

### Testing

- To test, use pytest

```bash
uv run pytest
```

- To test typing with mypy use:

```bash
uv run pytest --mypy -m mypy pygdtf/*py
```

## Citation

If you use this library in your research, publication, or software project,
please cite it as follows:

```bibtex
@software{pygdtf2025,
  title        = {pyGDTF: Python Library for General Device Type Format},
  author       = {{OpenStage}},
  year         = {2025},
  version      = {1.3.0},
  url          = {https://github.com/open-stage/python-gdtf}
}
```
