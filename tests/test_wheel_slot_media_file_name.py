# MIT License
#
# Copyright (C) 2026 Marvin
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
from xml.etree import ElementTree

import pygdtf

# WheelSlot._read_xml() read a missing MediaFileName as "" instead of None
# (default on xml_node.attrib.get), so to_xml() - which only checks "is this
# not None" - always wrote MediaFileName="" back out, even for slots that
# never had that attribute in the source. Harmless to the XSD (empty string
# is still a valid value) but pollutes every wheel slot on round-trip.
_DSC_XML = """<?xml version="1.0" encoding="UTF-8"?>
<GDTF DataVersion="1.2">
  <FixtureType Name="Test" ShortName="Test" LongName="Test" Manufacturer="Test"
    Description="Test" FixtureTypeID="00000000-0000-0000-0000-000000000000"
    Thumbnail="" ThumbnailOffsetX="0" ThumbnailOffsetY="0" RefFT="" CanHaveChildren="No">
    <AttributeDefinitions>
      <ActivationGroups/>
      <FeatureGroups>
        <FeatureGroup Name="Gobo" Pretty="Gobo">
          <Feature Name="Gobo"/>
        </FeatureGroup>
      </FeatureGroups>
      <Attributes>
        <Attribute Name="Gobo1" Pretty="G1" Feature="Gobo.Gobo" PhysicalUnit="None"/>
      </Attributes>
    </AttributeDefinitions>
    <Wheels>
      <Wheel Name="Gobo Wheel">
        <Slot Name="Open"/>
        <Slot Name="Gobo 1" MediaFileName="gobo01"/>
      </Wheel>
    </Wheels>
    <PhysicalDescriptions>
      <ColorSpace Mode="sRGB"/>
      <AdditionalColorSpaces/>
      <Gamuts/>
      <Filters/>
      <Emitters/>
      <DMXProfiles/>
      <CRIs/>
      <Connectors/>
      <Properties/>
    </PhysicalDescriptions>
    <Models>
      <Model Name="Base" PrimitiveType="Cube"/>
    </Models>
    <Geometries>
      <Geometry Name="Base" Model="Base"/>
    </Geometries>
    <DMXModes>
      <DMXMode Name="Default" Geometry="Base">
        <DMXChannels>
          <DMXChannel Offset="1" Geometry="Base">
            <LogicalChannel Attribute="Gobo1">
              <ChannelFunction Name="Open" Attribute="Gobo1" Default="0/1"/>
            </LogicalChannel>
          </DMXChannel>
        </DMXChannels>
      </DMXMode>
    </DMXModes>
  </FixtureType>
</GDTF>
"""


def test_wheel_slot_roundtrip_omits_empty_media_file_name(tmp_path: Path):
    dsc_file = tmp_path / "description.xml"
    dsc_file.write_text(_DSC_XML, encoding="utf-8")

    with pygdtf.FixtureType(dsc_file=str(dsc_file)) as fixture:
        writer = pygdtf.FixtureTypeWriter(fixture)
        output = tmp_path / "roundtrip.xml"
        writer.write_gdtf(output)

    root = ElementTree.fromstring(output.read_bytes())
    slots = root.findall("./FixtureType/Wheels/Wheel/Slot")
    assert len(slots) == 2

    open_slot, gobo_slot = slots
    assert open_slot.get("Name") == "Open"
    assert "MediaFileName" not in open_slot.attrib

    assert gobo_slot.get("Name") == "Gobo 1"
    assert gobo_slot.get("MediaFileName") == "gobo01"
