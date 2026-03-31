# MIT License
#
# Copyright (C) 2026 vanous
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

import pytest


def _iter_fixture_paths(file_path: str):
    path = Path(file_path)
    if path.is_file():
        if path.suffix.lower() == ".gdtf":
            return [path]
        return []
    if path.is_dir():
        return sorted(path.glob("*.gdtf"))
    return []


def _iter_channel_functions(fixture):
    for mode in fixture.dmx_modes:
        for dmx_channel in mode.dmx_channels:
            for logical_channel in dmx_channel.logical_channels:
                for channel_function in logical_channel.channel_functions:
                    yield mode, dmx_channel, logical_channel, channel_function


def test_mode_mastered_ranges_are_not_obviously_broken(request, pygdtf_module):
    file_path = request.config.getoption("--file-path")
    if file_path is None:
        fixture_paths = [
            Path(__file__).resolve().parent / "BlenderDMX@LED_PAR_64_RGBW@v0.3.gdtf"
        ]
    else:
        fixture_paths = _iter_fixture_paths(file_path)
    if not fixture_paths:
        pytest.skip(f"No .gdtf files found in {file_path}")

    for fixture_path in fixture_paths:
        with pygdtf_module.FixtureType(fixture_path) as fixture:
            assert fixture.dmx_modes, f"{fixture_path.name}: no DMX modes parsed"

            for (
                mode,
                dmx_channel,
                logical_channel,
                channel_function,
            ) in _iter_channel_functions(fixture):
                assert channel_function.dmx_to.value != -1, (
                    f"{fixture_path.name}: {mode.name}/{dmx_channel.geometry}/{logical_channel.attribute}/{channel_function.name} has dmx_to=-1"
                )
                assert (
                    channel_function.dmx_to.value >= channel_function.dmx_from.value
                ), (
                    f"{fixture_path.name}: {mode.name}/{dmx_channel.geometry}/{logical_channel.attribute}/{channel_function.name} has invalid function range {channel_function.dmx_from.get_value(full=True)}..{channel_function.dmx_to.get_value(full=True)}"
                )

                previous_dmx_from = None
                for channel_set in channel_function.channel_sets:
                    if previous_dmx_from is not None:
                        assert channel_set.dmx_from.value > previous_dmx_from, (
                            f"{fixture_path.name}: {mode.name}/{dmx_channel.geometry}/{logical_channel.attribute}/{channel_function.name} has non-increasing channel set starts"
                        )
                    previous_dmx_from = channel_set.dmx_from.value

                if channel_function.channel_sets:
                    last_set = channel_function.channel_sets[-1]
                    assert last_set.dmx_to.value >= last_set.dmx_from.value, (
                        f"{fixture_path.name}: {mode.name}/{dmx_channel.geometry}/{logical_channel.attribute}/{channel_function.name}/{last_set.name} has invalid last channel set range {last_set.dmx_from.get_value(full=True)}..{last_set.dmx_to.get_value(full=True)}"
                    )
