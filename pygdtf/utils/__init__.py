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

import copy
import datetime
from typing import Any, Dict, List, Optional

import pygdtf


def _get_channels_by_geometry(
    geometry_name: Optional[str] = None, channels: List["pygdtf.DmxChannel"] = []
) -> List["pygdtf.DmxChannel"]:
    """Find channels for a given geometry"""
    matched: List["pygdtf.DmxChannel"] = []
    for channel in channels:
        if channel.geometry == geometry_name:
            matched.append(channel)

    return matched


def _get_address_by_break(
    dmx_breaks: List["pygdtf.Break"] = [], value: int = 1, overwrite=False
) -> Optional["pygdtf.DmxAddress"]:
    """Return DMX address for a given DMX break"""
    if overwrite:
        return dmx_breaks[-1].dmx_offset
    for item in dmx_breaks:
        if item.dmx_break == value:
            return item.dmx_offset
    return None


def _get_channels_for_geometry(
    gdtf_profile: Optional["pygdtf.FixtureType"] = None,
    geometry: Optional["pygdtf.Geometry"] = None,
    dmx_channels: List["pygdtf.DmxChannel"] = [],
    channel_list: List[Any] = [],
) -> List[Any]:
    """Get all channels for the device, recursively, starting from root geometry"""
    if geometry is None:
        return []
    name = geometry.name

    if isinstance(geometry, pygdtf.GeometryReference):
        name = geometry.geometry

    for channel in _get_channels_by_geometry(name, dmx_channels):
        new_channel = None
        if isinstance(geometry, pygdtf.GeometryReference):
            new_channel = copy.deepcopy(channel)
            new_channel.geometry = geometry.name
            if channel.dmx_break == "Overwrite":
                channel.overwrite = True
                if len(geometry.breaks):
                    new_channel.dmx_break = geometry.breaks[
                        -1
                    ].dmx_break  # overwrite break is always the last one
                else:
                    new_channel.dmx_break = 1

        if channel.dmx_break == "Overwrite":
            # This only happens in an incorrect GDTF file
            # as Overwrite can only be on Referenced geometry
            new_channel = copy.deepcopy(channel)
            new_channel.dmx_break = 1

        channel_list.append((new_channel or channel, geometry))
    if hasattr(geometry, "geometries"):
        for sub_geometry in geometry.geometries:
            channel_list = _get_channels_for_geometry(
                gdtf_profile, sub_geometry, dmx_channels, channel_list
            )
    return channel_list


def get_virtual_channels(
    gdtf_profile: Optional["pygdtf.FixtureType"] = None,
    mode: Optional[str] = None,
    dmx_mode: Optional["pygdtf.DmxMode"] = None,
) -> List["Dict"]:
    """Returns virtual channels"""

    if gdtf_profile is None:
        return []

    if dmx_mode is None:
        dmx_mode = gdtf_profile.dmx_modes.get_mode_by_name(mode)

    if dmx_mode is None:
        return []

    root_geometry = gdtf_profile.geometries.get_geometry_by_name(dmx_mode.geometry)
    device_channels = _get_channels_for_geometry(
        gdtf_profile, root_geometry, dmx_mode._dmx_channels, []
    )

    virtual_channels: List[Dict[Any, Any]] = []

    for channel, geometry in device_channels:
        if channel.offset is not None:
            continue
        virtual_channels.append(channel)
    return virtual_channels


def get_dmx_channels(
    gdtf_profile: Optional["pygdtf.FixtureType"] = None,
    mode: Optional[str] = None,
    dmx_mode: Optional["pygdtf.DmxMode"] = None,
) -> List["Dict"]:
    """Returns list of arrays, each array is one DMX Break,
    with DMX channels, defaults, geometries"""

    if gdtf_profile is None:
        return []

    if dmx_mode is None:
        dmx_mode = gdtf_profile.dmx_modes.get_mode_by_name(mode)

    if dmx_mode is None:
        return []

    root_geometry = gdtf_profile.geometries.get_geometry_by_name(dmx_mode.geometry)
    if root_geometry is None:
        if len(gdtf_profile.geometries) == 1:
            root_geometry = gdtf_profile.geometries[0]

    # get a flat list of all channels and their linked geometries

    device_channels = _get_channels_for_geometry(
        gdtf_profile, root_geometry, dmx_mode._dmx_channels, []
    )

    dmx_channels: List[Any] = []

    for channel, geometry in device_channels:  # process the flat list:
        if channel.offset is None:  # skip virtual channels
            continue
        channel_break = channel.dmx_break

        if len(dmx_channels) < channel_break:
            # create sublist for each group of dmx breaks,
            # add amount of lists minus already existing lists:
            dmx_channels = dmx_channels + [[]] * (channel_break - len(dmx_channels))

        # get list of channels of a particular break:
        break_addition = 0

        if hasattr(geometry, "breaks"):
            # a dmx offset defined in a geometry defines how much this channel is offset from it's actual address
            dmx_offset = _get_address_by_break(
                geometry.breaks, channel_break, channel.overwrite
            )
            if dmx_offset is not None:
                break_addition = dmx_offset.address - 1  # here is also off by one
                channel = copy.deepcopy(channel)

        _offsets = [0, 0, 0, 0]  # coarse, fine, ultra, uber

        for i, offset in enumerate(channel.offset):
            _offsets[i] = offset + break_addition
            channel.offset[i] = _offsets[i]

        offset_coarse, offset_fine, offset_ultra, offset_uber = _offsets

        max_offset = max([offset_coarse, offset_fine, offset_ultra, offset_uber])

        break_channels = dmx_channels[channel_break - 1]  # off by one in list indexing

        if len(break_channels) < max_offset:
            break_channels = break_channels + [None] * (
                max_offset - len(break_channels)
            )
        break_channels[offset_coarse - 1] = channel

        dmx_channels[channel_break - 1] = break_channels

    # If the second (and more) break addresses follow the previous break addresses,
    # there might be some empty placeholder dmx channel objects. Remove them now:

    for index, break_list in enumerate(dmx_channels):
        dmx_channels[index] = [channel for channel in break_list if channel is not None]

    # This returns multiple lists of channel arrays. Each list is for one DMX Break, these
    # can be patched onto different DMX addresses. Or, these lists can be flatten into one
    # DMX footprint this way:
    # [channel for break_channels in dmx_channels for channel in break_channels]
    # Here, we should return the list of arrays, so the consumer can decide how to process it.
    return dmx_channels


def _create_break_channel(offset, channel, geometry, offset_index):
    return {
        "dmx": offset,
        "offset": channel.offset,
        "attribute": "+" * offset_index + str(channel.logical_channels[0].attribute),
        "default": channel.default.get_value(fine=offset_index > 0),
        "highlight": channel.highlight.get_value()
        if channel.highlight is not None
        else None,
        "geometry": geometry.name,
        "break": channel.dmx_break,
        "parent_name": geometry.parent_name,
    }


def get_used_geometries(
    gdtf_profile: Optional["pygdtf.FixtureType"] = None,
) -> List[str]:
    """Return list of geometries, used in geometry trees"""

    geometries_list: List[str] = []

    if gdtf_profile is None:
        return []

    for mode in gdtf_profile.dmx_modes:
        geometry = gdtf_profile.geometries.get_geometry_by_name(mode.geometry)
        geometries_list = _get_geometries_for_geometry(
            gdtf_profile, geometry, geometries_list
        )
    geometries_list = list(set(geometries_list))
    return geometries_list


def _get_geometries_for_geometry(
    gdtf_profile: Optional["pygdtf.FixtureType"] = None,
    geometry: Optional["pygdtf.Geometry"] = None,
    geometries_list: List[str] = [],
) -> List[str]:
    if gdtf_profile is None:
        return []

    if geometry is None:
        return []

    geometries_list.append(geometry.__class__.__name__)

    if isinstance(geometry, pygdtf.GeometryReference):
        if geometry.geometry:
            ref_geometry = gdtf_profile.geometries.get_geometry_by_name(
                geometry.geometry
            )
            geometries_list = _get_geometries_for_geometry(
                gdtf_profile, ref_geometry, geometries_list
            )

    if hasattr(geometry, "geometries"):
        if geometry.geometries:
            for sub_geometry in geometry.geometries:
                geometries_list = _get_geometries_for_geometry(
                    gdtf_profile, sub_geometry, geometries_list
                )
    return geometries_list


def get_beam_geometries_for_mode(
    gdtf_profile: Optional["pygdtf.FixtureType"] = None, mode_name: Optional[str] = None
):
    # TODO: refactor into get geometry by type, but starting from a DMX mode

    if gdtf_profile is None:
        return []

    dmx_mode = gdtf_profile.dmx_modes.get_mode_by_name(mode_name)

    if dmx_mode is not None:
        root_geometry = gdtf_profile.geometries.get_geometry_by_name(dmx_mode.geometry)
        return get_beam_geometries(gdtf_profile, root_geometry, [])


def get_beam_geometries(
    gdtf_profile: Optional["pygdtf.FixtureType"] = None,
    geometry: Optional["pygdtf.Geometry"] = None,
    geometry_list: List[Any] = [],
) -> List[Any]:
    """Get beam geometries"""

    if gdtf_profile is None or geometry is None:
        return []

    if isinstance(geometry, pygdtf.GeometryBeam):
        geometry_list.append(geometry)

    if isinstance(geometry, pygdtf.GeometryReference):
        if geometry.geometry is not None:
            geometry_list = get_beam_geometries(
                gdtf_profile,
                gdtf_profile.geometries.get_geometry_by_name(geometry.geometry),
                geometry_list,
            )

    if hasattr(geometry, "geometries"):
        for sub_geometry in geometry.geometries:
            geometry_list = get_beam_geometries(
                gdtf_profile, sub_geometry, geometry_list
            )
    return geometry_list


def calculate_complexity(gdtf_profile: Optional["pygdtf.FixtureType"] = None):
    """Returns complexity rating of the device based on presumed amount of work while creating it"""

    if gdtf_profile is None:
        return

    if gdtf_profile._package is None:
        return

    thumbnails_count = 0
    thumbnails_count += (
        1 if f"{gdtf_profile.thumbnail}.svg" in gdtf_profile._package.namelist() else 0
    )
    thumbnails_count += (
        1 if f"{gdtf_profile.thumbnail}.png" in gdtf_profile._package.namelist() else 0
    )
    wheels_count = len(gdtf_profile.wheels)
    gobos_count = len(
        [
            slot
            for wheel in gdtf_profile.wheels
            for slot in wheel.wheel_slots
            if slot.media_file_name.name is not None
        ]
    )
    facets_count = len(
        [
            facet
            for wheel in gdtf_profile.wheels
            for slot in wheel.wheel_slots
            if len(slot.facets)
            for facet in slot.facets
        ]
    )
    slot_count = sum([len(wheel.wheel_slots) for wheel in gdtf_profile.wheels])
    models_count = len(gdtf_profile.models)
    emitters_count = len(gdtf_profile.emitters)
    filters_measurements_count = len(
        [
            point
            for filter in gdtf_profile.filters
            for measurement in filter.measurements
            for point in measurement.measurement_points
        ]
    )
    emitters_measurements_count = len(
        [
            point
            for emitter in gdtf_profile.emitters
            for measurement in emitter.measurements
            for point in measurement.measurement_points
        ]
    )
    filters_count = len(gdtf_profile.filters)
    modes_count = len(gdtf_profile.dmx_modes)
    geometry_trees_count = 0
    dmx_channels_count = 0
    virtual_channels_count = 0
    channel_functions_count = 0
    channel_sets_count = 0
    real_fade_count = 0
    geometries = []
    physical_from_to = 0

    for mode in gdtf_profile.dmx_modes:
        if mode.geometry not in geometries:
            geometry_trees_count += 1
            geometries.append(mode.geometry)

        flattened_channels = mode.dmx_channels.as_dict()

        dmx_channels_count += mode.dmx_channels_count
        virtual_channels_count += mode.virtual_channels_count
        channel_functions = [
            function
            for channel in flattened_channels
            for logical_channel in channel.get("logical_channels", [])
            for function in logical_channel.get("channel_functions", [])
        ]

        channel_functions_count += len(channel_functions)
        physical_from_to = 0
        for channel_function in channel_functions:
            channel_sets_count += len(channel_function.get("channel_sets", 0))
            if channel_function.get("real_fade", 0) != 0:
                real_fade_count += 1
            if channel_function.get("physical_to", 0) != 0:
                physical_from_to += 1
            if channel_function.get("physical_from", 0) != 0:
                physical_from_to += 1

    data = (
        ("Wheels", wheels_count, 5),
        ("Thumbnails", thumbnails_count, 5),
        ("Gobo images", gobos_count, 5),
        ("Prism Facets", facets_count, 5),
        ("Wheel slots", slot_count, 4),
        ("3D Models", models_count, 3),
        ("Geometry trees", geometry_trees_count, 5),
        ("Emitters", emitters_count, 5),
        ("Filters", filters_count, 5),
        ("Emitter measurements", emitters_measurements_count, 1),
        ("Filter measurements", filters_measurements_count, 1),
        ("DMX Modes", modes_count, 5),
        ("DMX Channels", dmx_channels_count, 2),
        ("Virtual Channels", virtual_channels_count, 2),
        ("Channel Functions", channel_functions_count, 4),
        ("Channel Sets", channel_sets_count, 1),
        ("Real Fade values", real_fade_count, 6),
        ("Physical from to values", physical_from_to, 6),
    )
    total_complexity = 0
    data_out = ""
    for name, value, complexity in data:
        total_complexity += complexity * value
        data_out += f"{name}: {value}\n"
    # return total_complexity
    return {"total": total_complexity, "data": data_out}


def parse_date(date_string):
    try:
        return datetime.datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return datetime.datetime(1970, 1, 1, 1, 0, 0)


def dmx_to_physical(
    dmx_value,
    channel_element=None,
    dmx_from=None,
    dmx_to=None,
    physical_from=None,
    physical_to=None,
):
    if channel_element is not None:
        dmx_from = channel_element.dmx_from.value
        dmx_to = channel_element.dmx_to.value
        physical_from = channel_element.physical_from.value
        physical_to = channel_element.physical_to.value

    dmx_range = dmx_to - dmx_from
    if dmx_range == 0:
        return physical_from

    if ((dmx_from - dmx_to) + physical_from) == 0:
        return (dmx_from - dmx_from) * (physical_to - physical_from)

    return (dmx_value - dmx_from) * (physical_to - physical_from) / (
        dmx_to - dmx_from
    ) + physical_from


def get_int(string, default):
    try:
        return int(string)
    except ValueError:
        return default
