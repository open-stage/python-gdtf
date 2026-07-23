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

# A FilterMeasurement never carries LuminousIntensity in valid GDTF (gdtf.xsd:
# FilterMeasurement declares Physical, Transmission and InterpolationTo only -
# LuminousIntensity is not a permitted attribute there, unlike on
# EmitterMeasurement where it is required). Round-tripping a fixture whose
# Filter/Measurement never had LuminousIntensity must not invent one.
_DSC_XML = """<?xml version="1.0" encoding="UTF-8"?>
<GDTF DataVersion="1.2">
  <FixtureType Name="Test" ShortName="Test" LongName="Test" Manufacturer="Test"
    Description="Test" FixtureTypeID="00000000-0000-0000-0000-000000000000"
    Thumbnail="" ThumbnailOffsetX="0" ThumbnailOffsetY="0" RefFT="" CanHaveChildren="No">
    <AttributeDefinitions>
      <ActivationGroups/>
      <FeatureGroups>
        <FeatureGroup Name="Dimmer" Pretty="Dimmer">
          <Feature Name="Dimmer"/>
        </FeatureGroup>
      </FeatureGroups>
      <Attributes>
        <Attribute Name="Dimmer" Pretty="Dim" Feature="Dimmer.Dimmer" PhysicalUnit="None"/>
      </Attributes>
    </AttributeDefinitions>
    <Wheels/>
    <PhysicalDescriptions>
      <ColorSpace Mode="sRGB"/>
      <AdditionalColorSpaces/>
      <Gamuts/>
      <Filters>
        <Filter Name="ND Filter">
          <Measurement Physical="0.000000" Transmission="80.000000"/>
        </Filter>
      </Filters>
      <Emitters>
        <Emitter Name="LED White">
          <Measurement Physical="0.000000" LuminousIntensity="50.000000"/>
        </Emitter>
      </Emitters>
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
            <LogicalChannel Attribute="Dimmer">
              <ChannelFunction Name="Dimmer" Attribute="Dimmer" Default="0/1"/>
            </LogicalChannel>
          </DMXChannel>
        </DMXChannels>
      </DMXMode>
    </DMXModes>
  </FixtureType>
</GDTF>
"""


def test_filter_measurement_roundtrip_omits_luminous_intensity(tmp_path: Path):
    dsc_file = tmp_path / "description.xml"
    dsc_file.write_text(_DSC_XML, encoding="utf-8")

    with pygdtf.FixtureType(dsc_file=str(dsc_file)) as fixture:
        writer = pygdtf.FixtureTypeWriter(fixture)
        output = tmp_path / "roundtrip.xml"
        writer.write_gdtf(output)

    root = ElementTree.fromstring(output.read_bytes())

    filter_measurement = root.find(
        "./FixtureType/PhysicalDescriptions/Filters/Filter/Measurement"
    )
    assert filter_measurement is not None
    assert "LuminousIntensity" not in filter_measurement.attrib

    emitter_measurement = root.find(
        "./FixtureType/PhysicalDescriptions/Emitters/Emitter/Measurement"
    )
    assert emitter_measurement is not None
    assert emitter_measurement.attrib.get("LuminousIntensity") == "50.000000"
