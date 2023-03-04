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

To install from git, run pip:
```python
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

## Status

- GDTF 1.1


## Development

- to format, use `black` where possible, but leave method lines longer for
  readability
- to test, use `pytest`
