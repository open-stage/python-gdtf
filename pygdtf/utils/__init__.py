import pygdtf
from typing import List, Dict, Any


def getValue(dmx_value, fine=False):
    if dmx_value.byte_count == 1:
        return dmx_value.value
    f = dmx_value.value / 255.0
    msb = int(f)
    if not fine:
        return msb
    lsb = int((f - msb) * 255)
    return lsb


def get_dmx_mode_by_name(
    gdtf_profile: "pygdtf.FixtureType" = None, mode_name: str = None
) -> "pygdtf.DmxMode":
    """Find mode by name"""
    for mode in gdtf_profile.dmx_modes:
        if mode.name == mode_name:
            return mode
    return None


def get_geometry_by_name(
    gdtf_profile: "pygdtf.FixtureType" = None, geometry_name: str = None
) -> "pygdtf.Geometry":
    """Recursively find a geometry of a given name"""

    def iterate_geometries(collector):
        if collector.name == geometry_name:
            matched.append(collector)
        for g in collector.geometries:
            if g.name == geometry_name:
                matched.append(g)
            if hasattr(g, "geometries"):
                iterate_geometries(g)

    matched: List["pygdtf.Geometry"] = []
    iterate_geometries(gdtf_profile)
    if matched:
        return matched[0]

    return None


def get_geometry_by_type(
    root_geometry: "pygdtf.Geometry" = None, geometry_class: "pygdtf.Geometry" = None
) -> List["pygdtf.Geometry"]:
    """Recursively find all geometries of a given type"""

    def iterate_geometries(collector):
        for g in collector.geometries:
            if type(g) == geometry_class:
                matched.append(g)
            if hasattr(g, "geometries"):
                iterate_geometries(g)

    matched: List["pygdtf.Geometry"] = []
    iterate_geometries(root_geometry)
    return matched


def get_model_by_name(
    gdtf_profile: "pygdtf.FixtureType" = None, model_name: str = None
) -> "pygdtf.Model":
    """Find model by name"""
    for model in gdtf_profile.models:
        if model.name == model_name:
            return model

    return None


def get_channels_by_geometry(
    geometry_name: str = None, channels: List["pygdtf.DmxChannel"] = []
) -> List["pygdtf.DmxChannel"]:
    """Find channels for a given geometry"""
    matched: List["pygdtf.DmxChannel"] = []
    for channel in channels:
        if channel.geometry == geometry_name:
            matched.append(channel)

    return matched


def get_address_by_break(
    dmx_breaks: List["pygdtf.Break"] = [], value: int = 1
) -> "pygdtf.DmxAddress":
    """Return DMX address for a given DMX break"""
    for item in dmx_breaks:
        if item.dmx_break == value:
            return item.dmx_offset
    return None


def get_channels_for_geometry(
    gdtf_profile: "pygdtf.FixtureType" = None,
    geometry: "pygdtf.Geometry" = None,
    dmx_channels: List["pygdtf.DmxChannel"] = [],
    channel_list: List[Any] = [],
) -> List[Any]:
    """Get all channels for the device, recursively, starting from root geometry"""
    name = geometry.name

    if isinstance(geometry, pygdtf.GeometryReference):
        name = geometry.geometry

    for channel in get_channels_by_geometry(name, dmx_channels):
        # Reference dmx break overwrite is handled by get_dmx_channels, maybe it
        # could/should be handled here?
        channel_list.append((channel, geometry))
    if hasattr(geometry, "geometries"):
        for sub_geometry in geometry.geometries:
            channel_list = get_channels_for_geometry(
                gdtf_profile, sub_geometry, dmx_channels, channel_list
            )
    return channel_list


def get_virtual_channels(
    gdtf_profile: "pygdtf.FixtureType" = None, mode: str = None
) -> List["Dict"]:
    """Returns virtual channels"""

    dmx_mode = None
    dmx_mode = get_dmx_mode_by_name(gdtf_profile, mode)
    root_geometry = get_geometry_by_name(gdtf_profile, dmx_mode.geometry)
    device_channels = get_channels_for_geometry(
        gdtf_profile, root_geometry, dmx_mode.dmx_channels, []
    )

    virtual_channels: List[Dict[Any, Any]] = []

    for channel, geometry in device_channels:
        if channel.offset is None:
            virtual_channels.append(
                {
                    "id": str(
                        channel.logical_channels[0].channel_functions[0].attribute
                    ),
                    "default": getValue(
                        channel.logical_channels[0].channel_functions[0].default
                    ),
                    "geometry": geometry.name,
                    "channel_functions": channel.logical_channels[0].channel_functions,
                }
            )
    return virtual_channels


def get_dmx_channels(
    gdtf_profile: "pygdtf.FixtureType" = None, mode: str = None
) -> List["Dict"]:
    """Returns list of arrays, each array is one DMX Break,
    with DMX channels, defaults, geometries"""

    dmx_mode = None
    dmx_mode = get_dmx_mode_by_name(gdtf_profile, mode)
    root_geometry = get_geometry_by_name(gdtf_profile, dmx_mode.geometry)

    # get a flat list of all channels and their linked geometries

    device_channels = get_channels_for_geometry(
        gdtf_profile, root_geometry, dmx_mode.dmx_channels, []
    )

    dmx_channels: List[Any] = []

    for channel, geometry in device_channels:  # process the flat list:
        if channel.offset is None:  # skip virtual channels
            continue
        channel_break = channel.dmx_break
        if channel.dmx_break == "Overwrite":
            channel_break = geometry.breaks[0].dmx_break

        if len(dmx_channels) < channel_break:
            # create sublist for each group of dmx breaks,
            # add amount of lists minus already existing lists:
            dmx_channels = dmx_channels + [[]] * (channel_break - len(dmx_channels))

        # get list of channels of a particular break:
        break_channels = dmx_channels[channel_break - 1]  # off by one...

        break_addition = 0

        if hasattr(geometry, "breaks"):
            # a dmx address offset defines how much this channel is offset from it's actual address
            dmx_offset = get_address_by_break(geometry.breaks, channel_break)
            if dmx_offset is not None:
                break_addition = dmx_offset.address - 1  # here is also off by one

        # TODO: rework below to support ultra and uber
        offset_coarse = channel.offset[0] + break_addition
        offset_fine = 0

        if len(channel.offset) > 1:
            offset_fine = channel.offset[1] + break_addition

        max_offset = max([offset_coarse, offset_fine])

        if len(break_channels) < max_offset:
            # print(len(break_channels), break_channels)
            break_channels = break_channels + [
                {"dmx": "", "id": "", "default": 0, "geometry": "", "break": ""}
            ] * (max_offset - len(break_channels))

        break_channels[offset_coarse - 1] = {
            "dmx": offset_coarse,
            "id": str(channel.logical_channels[0].channel_functions[0].attribute),
            "default": getValue(
                channel.logical_channels[0].channel_functions[0].default
            ),
            "geometry": geometry.name,
            "break": channel_break,
            "channel_functions": channel.logical_channels[0].channel_functions,
        }
        if offset_fine > 0:
            break_channels[offset_fine - 1] = {
                "dmx": offset_fine,
                "id": "+"
                + str(channel.logical_channels[0].channel_functions[0].attribute),
                "default": getValue(
                    channel.logical_channels[0].channel_functions[0].default, True
                ),
                "geometry": geometry.name,
                "break": channel_break,
                "channel_functions": channel.logical_channels[0].channel_functions,
            }
        dmx_channels[channel_break - 1] = break_channels

    # If the second (and more) break addresses follow the previous break addresses,
    # there might be some empty placeholder dmx channel objects. Remove them now:

    for index, break_list in enumerate(dmx_channels):
        dmx_channels[index] = [
            channel for channel in break_list if channel.get("id", "") != ""
        ]

    # This returns multiple lists of channel arrays. Each list is for one DMX Break, these
    # can be patched onto different DMX addresses. Or, these lists can be flatten into one
    # DMX footprint this way:
    # [channel for break_channels in dmx_channels for channel in break_channels]
    # Here, we should return the list of arrays, so the consumer can decide how to process it.
    return dmx_channels


def get_dmx_modes_info(gdtf_profile: "pygdtf.FixtureType" = None):
    dmx_mode_list = []

    for idx, mode in enumerate(gdtf_profile.dmx_modes):
        mode_id = idx
        mode_name = mode.name
        dmx_channels = get_dmx_channels(gdtf_profile, mode_name)
        dmx_channels_flattened = [
            channel for break_channels in dmx_channels for channel in break_channels
        ]
        mode_virtual_channel_count = get_virtual_channels(gdtf_profile, mode_name)
        dmx_mode_list.append(
            {
                "mode_id": mode_id,
                "mode_name": mode_name,
                "mode_dmx_channel_count": len(dmx_channels_flattened),
                "mode_virtual_channel_count": len(mode_virtual_channel_count),
            }
        )
    return dmx_mode_list


def get_beam_geometries_for_mode(
    gdtf_profile: "pygdtf.FixtureType" = None, mode_name: str = None
):
    # TODO: refactor into get geometry by type, but starting from a DMX mode
    dmx_mode = get_dmx_mode_by_name(gdtf_profile, mode_name)
    root_geometry = get_geometry_by_name(gdtf_profile, dmx_mode.geometry)
    return get_beam_geometries(gdtf_profile, root_geometry, [])


def get_beam_geometries(
    gdtf_profile: "pygdtf.FixtureType" = None,
    geometry: "pygdtf.Geometry" = None,
    geometry_list: List[Any] = [],
) -> List[Any]:
    """Get beam geometries"""

    if isinstance(geometry, pygdtf.GeometryBeam):
        geometry_list.append(geometry)

    if isinstance(geometry, pygdtf.GeometryReference):
        geometry_list = get_beam_geometries(
            gdtf_profile,
            get_geometry_by_name(gdtf_profile, geometry.geometry),
            geometry_list,
        )

    if hasattr(geometry, "geometries"):
        for sub_geometry in geometry.geometries:
            geometry_list = get_beam_geometries(
                gdtf_profile, sub_geometry, geometry_list
            )
    return geometry_list


def calculate_complexity(gdtf_profile: "pygdtf.FixtureType" = None):
    """Returns complexity rating of the device based on presumed amount of work while creating it"""

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

        dmx_channels_breaks = pygdtf.utils.get_dmx_channels(gdtf_profile, mode.name)
        virtual_channels_breaks = pygdtf.utils.get_virtual_channels(
            gdtf_profile, mode.name
        )
        flattened_channels = [
            channel
            for break_channels in dmx_channels_breaks
            for channel in break_channels
        ]
        dmx_channels_count += len(flattened_channels)
        virtual_channels_count += len(virtual_channels_breaks)
        channel_functions = [
            function
            for channel in flattened_channels
            for function in channel.get("channel_functions", [])
        ]

        channel_functions_count += len(channel_functions)
        physical_from_to = 0
        for channel_function in channel_functions:
            channel_sets_count += len(channel_function.channel_sets)
            if channel_function.real_fade != 0:
                real_fade_count += 1
            if channel_function.physical_to != 0:
                physical_from_to += 1
            if channel_function.physical_from != 0:
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
