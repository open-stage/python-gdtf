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

# get info about DMX Modes:
pygdtf.utils.get_dmx_modes_info(gdtf_fixture)

[{'mode_id': 0,
  'mode_name': 'Default',
  'mode_dmx_channel_count': 5,
  'mode_virtual_channel_count': 0}]

# get list of DMX channels with geometries, channels functions for a DMX Mode named "Default"
pygdtf.utils.get_dmx_channels(gdtf_fixture, "Default")

[
    [
        {'dmx': 1, 'id': 'Dimmer', 'offset': [
                1
            ], 'default': 0, 'highlight': 255, 'geometry': 'Beam', 'break': 1, 'channel_functions': [
                {'name': 'Dimmer', 'attribute': 'Dimmer', 'real_fade': 0.0, 'physical_to': 1.0, 'physical_from': 0.0, 'channel_sets': ['Closed', '', 'Open'
                    ]
                }
            ]
        },
        {'dmx': 2, 'id': 'ColorAdd_R', 'offset': [
                2
            ], 'default': 0, 'highlight': 255, 'geometry': 'Beam', 'break': 1, 'channel_functions': [
                {'name': 'ColorAdd_R', 'attribute': 'ColorAdd_R', 'real_fade': 0.0, 'physical_to': 1.0, 'physical_from': 0.0, 'channel_sets': ['Min', '', 'Max'
                    ]
                }
            ]
        },
        {'dmx': 3, 'id': 'ColorAdd_G', 'offset': [
                3
            ], 'default': 0, 'highlight': 255, 'geometry': 'Beam', 'break': 1, 'channel_functions': [
                {'name': 'ColorAdd_G', 'attribute': 'ColorAdd_G', 'real_fade': 0.0, 'physical_to': 1.0, 'physical_from': 0.0, 'channel_sets': ['Min', '', 'Max'
                    ]
                }
            ]
        },
        {'dmx': 4, 'id': 'ColorAdd_B', 'offset': [
                4
            ], 'default': 0, 'highlight': 255, 'geometry': 'Beam', 'break': 1, 'channel_functions': [
                {'name': 'ColorAdd_B', 'attribute': 'ColorAdd_B', 'real_fade': 0.0, 'physical_to': 1.0, 'physical_from': 0.0, 'channel_sets': ['Min', '', 'Max'
                    ]
                }
            ]
        },
        {'dmx': 5, 'id': 'ColorAdd_W', 'offset': [
                5
            ], 'default': 0, 'highlight': None, 'geometry': 'Beam', 'break': 1, 'channel_functions': [
                {'name': 'ColorAdd_W', 'attribute': 'ColorAdd_W', 'real_fade': 0.0, 'physical_to': 1.0, 'physical_from': 0.0, 'channel_sets': ['Min', '', 'Max'
                    ]
                }
            ]
        }
    ]
]

#you can get the full info with channels and with channel functions at once:
pygdtf.utils.get_dmx_modes_info(gdtf_fixture, include_channels=True, include_channel_functions=True)
```

See [BlenderDMX](https://github.com/open-stage/blender-dmx) and
[tests](https://github.com/open-stage/python-gdtf/tree/master/tests) for
reference implementation and usage examples.

## Usage principles

- for list of channels, use `pygdtf.utils.get_dmx_channels` as per example
  above, do not presume that plain layout of DMX Channels in a DMX Mode is
  defining the DMX footprint of the device. Geometry references are
  (frequently) used to re-use parts of the device. This means that a channel(s)
  defined once can be multiplied, over several times duplicated geometry
  (tree).

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
