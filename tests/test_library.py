# MIT License
#
# Copyright (C) 2023 vanous
#
# This file is part of pygdtf.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from pathlib import Path
import json


def test_version(gdtf_fixture):
    """GDTF version should be 1.2"""

    assert gdtf_fixture.data_version == "1.2"


def test_name(gdtf_fixture):
    """Name of the fixture should be as defined"""

    assert gdtf_fixture.name == "LED PAR 64 RGBW"


def test_dmx_channel_count(gdtf_fixture, pygdtf_module):
    """DMX mode name should be Default, channel count should be 5"""

    for mode in gdtf_fixture.dmx_modes:
        assert mode.name == "Default"
        assert mode.dmx_channels_count == 5


def test_modes_info_as_dict(pygdtf_module):
    """Test mode info on complex devices"""

    test_files = ["test1", "test2"]

    for test_file in test_files:
        test_fixture_test_file = Path(
            Path(__file__).parents[0], f"{test_file}.xml"
        ).as_posix()
        test_fixture_result_file = Path(Path(__file__).parents[0], f"{test_file}.json")

        fixture = pygdtf_module.FixtureType(dsc_file=test_fixture_test_file)

        modes_info = fixture.dmx_modes.as_dict()
        print("fixture", fixture.name)

        for mode in modes_info:
            print(mode["name"], mode["dmx_channels_count"])

        # This is here to capture test data next time if needed
        # with open(f"tests/{test_file}.json", "w") as f:
        #    json.dump(modes_info, f)

        with open(test_fixture_result_file) as f:
            test_result = json.load(f)

        # dmx mode

        for item in [
            "name",
            "dmx_channels_count",
            "virtual_channels_count",
            "dmx_breaks",
        ]:
            assert modes_info[0][item] == test_result[0][item]

        # dmx channel

        for item in ["dmx", "offset", "attribute", "default", "geometry", "break"]:
            assert (
                modes_info[0]["dmx_channels"][0][item]
                == test_result[0]["dmx_channels"][0][item]
            )

        # logical channel
        for item in ["attribute"]:
            assert (
                modes_info[0]["dmx_channels"][0]["logical_channels"][0][item]
                == test_result[0]["dmx_channels"][0]["logical_channels"][0][item]
            )
        # channel function
        for item in ["name", "attribute", "dmx_from", "dmx_to"]:
            assert (
                modes_info[0]["dmx_channels"][0]["logical_channels"][0][
                    "channel_functions"
                ][0][item]
                == test_result[0]["dmx_channels"][0]["logical_channels"][0][
                    "channel_functions"
                ][0][item]
            )
        # channel set
        for item in ["name", "dmx_from", "dmx_to"]:
            assert (
                modes_info[0]["dmx_channels"][0]["logical_channels"][0][
                    "channel_functions"
                ][0]["channel_sets"][0][item]
                == test_result[0]["dmx_channels"][0]["logical_channels"][0][
                    "channel_functions"
                ][0]["channel_sets"][0][item]
            )

        # whole thing
        assert modes_info == test_result
