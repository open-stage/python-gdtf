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

import shutil
from pathlib import Path
import subprocess
import zipfile
from xml.etree import ElementTree

import pytest
import pygdtf


def test_create_minimal_gdtf_from_scratch(tmp_path: Path):
    fixture = pygdtf.FixtureType()
    fixture._gdtf = ElementTree.Element("GDTF")
    fixture._root = ElementTree.SubElement(fixture._gdtf, "FixtureType")

    fixture.data_version = "1.2"
    fixture.name = "UnitTest Fixture"
    fixture.short_name = "UTF"
    fixture.long_name = "UnitTest Fixture"
    fixture.manufacturer = "UnitTest"
    fixture.description = "Created from scratch in tests"
    fixture.fixture_type_id = "11111111-2222-3333-4444-555555555555"
    fixture.thumbnail = ""
    fixture.thumbnail_offset_x = 0
    fixture.thumbnail_offset_y = 0
    fixture.can_have_children = "No"
    fixture.ref_ft = ""

    activation_group = pygdtf.ActivationGroup(name="Intensity")
    feature_group = pygdtf.FeatureGroup(
        name="Dimmer",
        pretty="Dimmer",
        features=[pygdtf.Feature(name="Dimmer")],
    )
    dimmer_feature_link = f"{feature_group.name}.{feature_group.features[0].name}"
    dimmer_attribute = pygdtf.Attribute(
        name="Dimmer",
        pretty="Dimmer",
        activation_group=pygdtf.NodeLink("ActivationGroups", activation_group.name),
        feature=pygdtf.NodeLink("FeatureGroups", dimmer_feature_link),
        physical_unit=pygdtf.PhysicalUnit("Percent"),
    )

    fixture.activation_groups = [activation_group]
    fixture.feature_groups = [feature_group]
    fixture.attributes = [dimmer_attribute]
    fixture.color_space = pygdtf.ColorSpace(mode=pygdtf.ColorSpaceMode("sRGB"))
    base_geometry = pygdtf.Geometry(name="Base")
    fixture.geometries = pygdtf.Geometries([base_geometry])

    dimmer_function = pygdtf.ChannelFunction(
        name="Dimmer",
        attribute=pygdtf.NodeLink("Attributes", dimmer_attribute.name),
        default=pygdtf.DmxValue("0/1"),
        physical_from=pygdtf.PhysicalValue(0.0),
        physical_to=pygdtf.PhysicalValue(1.0),
    )
    dimmer_function._attr_keys = {"Default"}

    logical_channel = pygdtf.LogicalChannel(
        attribute=pygdtf.NodeLink("Attributes", dimmer_attribute.name),
        channel_functions=[dimmer_function],
    )
    dmx_channel = pygdtf.DmxChannel(
        dmx_break=1,
        offset=[1],
        logical_channels=[logical_channel],
        geometry=base_geometry.name,
        default=None,
    )
    dmx_mode = pygdtf.DmxMode(
        name="Basic",
        geometry=base_geometry.name,
        _dmx_channels=[dmx_channel],
        fixture_type=fixture,
    )
    fixture.dmx_modes = [dmx_mode]

    writer = pygdtf.FixtureTypeWriter(fixture)
    gdtf_archive = tmp_path / "scratch.gdtf"
    writer.write_gdtf(gdtf_archive)

    with zipfile.ZipFile(gdtf_archive) as archive:
        description_path = tmp_path / "description.xml"
        description_path.write_bytes(archive.read("description.xml"))

    schema_path = Path(__file__).resolve().parents[2] / "gdtf.xsd"
    schema_path = Path(__file__).resolve().parent / "gdtf.xsd"
    assert schema_path.is_file()

    if shutil.which("xmllint") is None:
        pytest.skip("xmllint not available to validate output")

    subprocess.run(
        [
            "xmllint",
            "--noout",
            "--schema",
            str(schema_path),
            str(description_path),
        ],
        check=True,
    )
