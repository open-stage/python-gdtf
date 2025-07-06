# MIT License
#
# Copyright (C) 2025 vanous
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

import json

# import pygal
from pathlib import Path


def find_set(ch_f, dmx_value):
    for ch_s in ch_f.channel_sets:
        if ch_s.dmx_from.value <= dmx_value <= ch_s.dmx_to.value:
            return ch_s


def calc_values(selected_function, pygdtf_module):
    print(selected_function.name)
    x = []
    y = []
    z = []
    for dmx_value in range(
        selected_function.dmx_from.value,
        selected_function.dmx_to.value + 1,
    ):
        ch_set = find_set(selected_function, dmx_value)
        f_phys = pygdtf_module.dmx_to_physical(dmx_value, selected_function)
        if ch_set.physical_from.source.value == "Set":
            # find surrounding sets
            ...

        if ch_set:
            phys = pygdtf_module.dmx_to_physical(dmx_value, ch_set)
        else:
            phys = f_phys

        x.append(dmx_value)
        y.append(phys)
        z.append(f_phys)

    # fig = pygal.XY()
    # fig.x_title = "DMX Values"
    # fig.y_title = "Physical Values"
    # fig.add("Ch. Function", [(a, b) for a, b in zip(x, z)])
    # fig.add("Ch. Set", [(a, b) for a, b in zip(x, y)])
    # fig.render_to_file(f"/tmp/{selected_function.name}.svg")
    return x, y, z


def test_get_physical(gdtf_fixture, pygdtf_module):
    """Test get physical values"""

    dmx_mode = gdtf_fixture.dmx_modes[0]
    dmx_channels = dmx_mode.dmx_channels
    all_values = {}
    for dmx_channel in dmx_channels:
        if dmx_channel not in all_values:
            all_values[dmx_channel.name] = {}
        for logical_channel in dmx_channel.logical_channels:
            if logical_channel not in all_values[dmx_channel.name]:
                all_values[dmx_channel.name][logical_channel.attribute.str_link] = {}
            for channel_function in logical_channel.channel_functions:
                if (
                    channel_function
                    not in all_values[dmx_channel.name][
                        logical_channel.attribute.str_link
                    ]
                ):
                    all_values[dmx_channel.name][logical_channel.attribute.str_link][
                        channel_function.name
                    ] = {}
                print("processing", channel_function.name)
                dmx, ch_set, ch_fnc = calc_values(channel_function, pygdtf_module)
                all_values[dmx_channel.name][logical_channel.attribute.str_link][
                    channel_function.name
                ]["dmx"] = dmx
                all_values[dmx_channel.name][logical_channel.attribute.str_link][
                    channel_function.name
                ]["set"] = ch_set
                all_values[dmx_channel.name][logical_channel.attribute.str_link][
                    channel_function.name
                ]["function"] = ch_fnc
    # save new values
    # with open(f"tests/physical_values.json", "w") as f:
    #    json.dump(all_values, f)

    with open(f"tests/physical_values.json", "r") as f:
        saved_values = json.load(f)
    assert saved_values == all_values
