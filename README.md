# python-gdtf

Python library for [General Device Type Format](https://gdtf-share.com/)

GDTF specification as per https://gdtf.eu/gdtf/prologue/introduction/

See source code for documentation. Naming conventions, in general, are
identical to that on the GDTF developer wiki, except CamelCase is replaced with
underscore_delimiters.

## Credits

Originally [created](https://github.com/jackdpage/python-gdtf) by [Jack
Page](https://github.com/jackdpage). Forked to
[Open-Stage](https://github.com/open-stage), used for example by
[BlenderDMX](https://github.com/open-stage/blender-dmx).

## Installation

To install latest master from this git repository, run pip:

```bash
python -m pip install https://codeload.github.com/open-stage/python-gdtf/zip/refs/heads/master
```

## Usage

```python
import pygdtf
gdtf_fixture = pygdtf.FixtureType("gdtf_file.gdtf")
```

See [BlenderDMX](https://github.com/open-stage/blender-dmx) and
[tests](https://github.com/open-stage/python-gdtf/tree/master/tests) for
reference implementation.

## Usage principles

- do not presume that plain layout of DMX Channels in a DMX Mode is defining
  the DMX footprint of the device. Geometry references are (frequently) used to
  re-use parts of the device. This means that a channel(s) defined once can be
  multiplied, over several times duplicated geometry (tree).

- do not use geometry names for anything related to function of the geometry
  (yoke, pan, tilt, head), use attached GDTF attributes ("Pan", "Tilt")

- only Beam or Camera geometry types are currently used special types of
  geometry. Other types (Axis...) are not really relevant as even Normal
  geometry can have for example "Pan" GDTF attribute attached, to indicate
  movement.

## Status

- GDTF 1.1 with some small portions of GDTF 1.2 being included

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
