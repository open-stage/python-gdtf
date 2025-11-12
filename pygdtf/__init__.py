# MIT License
#
# Copyright (C) 2020 Hugo Aboud, Jack Page, vanous
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

import datetime
import zipfile
from typing import Dict, List, Optional, Union
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from .base_node import BaseNode
from .dmxbreak import *
from .geometries import *
from .macro import *
from .properties import *
from .protocols import *
from .revisions import *
from .utils import *
from .value import *  # type: ignore

__version__ = "1.3.1"

# Standard predefined colour spaces: R, G, B, W-P
COLOR_SPACE_SRGB = ColorSpaceDefinition(
    ColorCIE(0.6400, 0.3300, 0.2126),
    ColorCIE(0.3000, 0.6000, 0.7152),
    ColorCIE(0.1500, 0.0600, 0.0722),
    ColorCIE(0.3127, 0.3290, 1.0000),
)
COLOR_SPACE_PROPHOTO = ColorSpaceDefinition(
    ColorCIE(0.7347, 0.2653),
    ColorCIE(0.1596, 0.8404),
    ColorCIE(0.0366, 0.0001),
    ColorCIE(0.3457, 0.3585),
)
COLOR_SPACE_ANSI = ColorSpaceDefinition(
    ColorCIE(0.7347, 0.2653),
    ColorCIE(0.1596, 0.8404),
    ColorCIE(0.0366, 0.001),
    ColorCIE(0.4254, 0.4044),
)


def _find_root(pkg: "zipfile.ZipFile") -> "ElementTree.Element":
    """Given a GDTF zip archive, find the FixtureType of the corresponding
    description.xml file."""

    with pkg.open("description.xml", "r") as f:
        description_str = f.read().decode("utf-8")
        if description_str[-1] == "\x00":  # this should not happen, but...
            description_str = description_str[:-1]
    try:
        return ElementTree.fromstring(description_str)
    except Exception as e:
        return ElementTree.fromstring(
            """<GDTF DataVersion='1.0'>
                <FixtureType
                  Manufacturer='PyGDTF'
                  Name='Original File Had Broken XML'
                  ShortName='Broken XML'
                  LongName='Original File Had Broken XML'
                  Description='Original File Had Broken XML'
                  FixtureTypeID='8EAC5323-C63A-4C21-96CF-5DBF4AF049B6'
                  RefFT=''
                  Thumbnail=''>
                </FixtureType>
            </GDTF>"""
        )


class FixtureType:
    def __init__(self, path=None, dsc_file: Optional[str] = None):
        self._package = None
        self._root = None
        if path is not None:
            self._package = zipfile.ZipFile(path, "r")
        if self._package is not None:
            self._gdtf = _find_root(self._package)
            self._root = self._gdtf.find("FixtureType")
        elif dsc_file is not None:
            self._gdtf = ElementTree.parse(dsc_file).getroot()
            self._root = self._gdtf.find("FixtureType")
        if self._root is not None:
            self._read_xml()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._package is not None:
            self._package.close()

    def _read_xml(self):
        self.data_version = self._gdtf.get("DataVersion", 1.2)
        self.name = self._root.get("Name")
        self.short_name = self._root.get("ShortName")
        self.long_name = self._root.get("LongName")
        self.manufacturer = self._root.get("Manufacturer")
        self.description = self._root.get("Description")
        self.fixture_type_id = self._root.get("FixtureTypeID")
        self.thumbnail = self._root.get("Thumbnail", "").encode("utf-8").decode("cp437")
        self.thumbnails = Thumbnails(xml_node=self._root, fixture_type=self)
        self.ref_ft = self._root.get("RefFT")
        # For each attribute, we first check for the existence of the collect node
        # If such a node doesn't exist, then none of the children will exist and
        # the corresponding attribute for this class can be set to empty. Failing
        # to do this would result in AttributeError if we try to, for example, run
        # a findall on a non-existent collect

        attribute_definitions = self._root.find("AttributeDefinitions")

        if attribute_definitions is not None:
            activation_collect = attribute_definitions.find("ActivationGroups")
            if activation_collect is not None:
                self.activation_groups = [
                    ActivationGroup(xml_node=i)
                    for i in activation_collect.findall("ActivationGroup")
                ]
            else:
                self.activation_groups = []

            feature_collect = attribute_definitions.find("FeatureGroups")
            if feature_collect is not None:
                self.feature_groups = [
                    FeatureGroup(xml_node=i)
                    for i in feature_collect.findall("FeatureGroup")
                ]
            else:
                self.feature_groups = []
            attribute_collect = attribute_definitions.find("Attributes")
            if attribute_collect is not None:
                self.attributes = [
                    Attribute(xml_node=i)
                    for i in attribute_collect.findall("Attribute")
                ]
            else:
                self.attributes = []

        wheel_collect = self._root.find("Wheels")
        if wheel_collect is not None:
            self.wheels = [Wheel(xml_node=i) for i in wheel_collect.findall("Wheel")]
        else:
            self.wheels = []

        physical_descriptions_node = self._root.find("PhysicalDescriptions")

        if physical_descriptions_node is not None:
            emitter_collect = physical_descriptions_node.find("Emitters")
            if emitter_collect is not None:
                self.emitters = [
                    Emitter(xml_node=i) for i in emitter_collect.findall("Emitter")
                ]
            else:
                self.emitters = []

            filter_collect = physical_descriptions_node.find("Filters")
            if filter_collect is not None:
                self.filters = [
                    Filter(xml_node=i) for i in filter_collect.findall("Filter")
                ]
            else:
                self.filters = []

            color_space = physical_descriptions_node.find("ColorSpace")
            if color_space is not None:
                self.color_space = ColorSpace(xml_node=color_space)
            else:
                # The default color space is sRGB if nothing else is defined
                self.color_space = ColorSpace(mode=ColorSpaceMode("sRGB"))

            gamut_collect = physical_descriptions_node.find("Gamuts")
            if gamut_collect is not None:
                self.gamuts = [
                    Gamut(xml_node=i) for i in gamut_collect.findall("Gamut")
                ]
            else:
                self.gamuts = []

            profiles_collect = physical_descriptions_node.find("DMXProfiles")
            if profiles_collect is not None:
                self.dmx_profiles = [
                    DmxProfile(xml_node=i)
                    for i in profiles_collect.findall("DMXProfile")
                ]
            else:
                self.dmx_profiles = []

            cri_collect = physical_descriptions_node.find("CRIs")
            if cri_collect is not None:
                self.cri_groups = [
                    CriGroup(xml_node=i) for i in cri_collect.findall("CRIGroup")
                ]
            else:
                self.cri_groups = []

            properties = physical_descriptions_node.find("Properties")
            if properties is not None:
                self.properties = Properties(xml_node=properties)
            else:
                self.properties = Properties()

        self.models = Models()
        model_collect = self._root.find("Models")
        if model_collect is not None:
            self.models = Models(
                [Model(xml_node=i) for i in model_collect.findall("Model")]
            )
        for model in self.models:
            if self._package is not None:
                if f"models/gltf/{model.file.name}.glb" in self._package.namelist():
                    model.file.extension = "glb"
                    model.file.crc = self._package.getinfo(
                        f"models/gltf/{model.file.name}.glb"
                    ).CRC
                elif f"models/3ds/{model.file.name}.3ds" in self._package.namelist():
                    model.file.extension = "3ds"
                    model.file.crc = self._package.getinfo(
                        f"models/3ds/{model.file.name}.3ds"
                    ).CRC

        self.geometries = Geometries()
        geometry_collect = self._root.find("Geometries")
        if geometry_collect is not None:
            for i in geometry_collect.findall("Geometry"):
                self.geometries.append(
                    Geometry(xml_node=i, xml_parent=geometry_collect)
                )
            for i in geometry_collect.findall("Axis"):
                self.geometries.append(
                    GeometryAxis(xml_node=i, xml_parent=geometry_collect)
                )
            for i in geometry_collect.findall("FilterBeam"):
                self.geometries.append(
                    GeometryFilterBeam(xml_node=i, xml_parent=geometry_collect)
                )
            for i in geometry_collect.findall("FilterColor"):
                self.geometries.append(
                    GeometryFilterColor(xml_node=i, xml_parent=geometry_collect)
                )
            for i in geometry_collect.findall("FilterGobo"):
                self.geometries.append(
                    GeometryFilterGobo(xml_node=i, xml_parent=geometry_collect)
                )
            for i in geometry_collect.findall("FilterShaper"):
                self.geometries.append(
                    GeometryFilterShaper(xml_node=i, xml_parent=geometry_collect)
                )
            for i in geometry_collect.findall("MediaServerMaster"):
                self.geometries.append(
                    GeometryMediaServerMaster(xml_node=i, xml_parent=geometry_collect)
                )
            for i in geometry_collect.findall("MediaServerLayer"):
                self.geometries.append(
                    GeometryMediaServerLayer(xml_node=i, xml_parent=geometry_collect)
                )
            for i in geometry_collect.findall("MediaServerCamera"):
                self.geometries.append(
                    GeometryMediaServerCamera(xml_node=i, xml_parent=geometry_collect)
                )
            for i in geometry_collect.findall("Inventory"):
                self.geometries.append(
                    GeometryInventory(xml_node=i, xml_parent=geometry_collect)
                )
            for i in geometry_collect.findall("Beam"):
                self.geometries.append(
                    GeometryBeam(xml_node=i, xml_parent=geometry_collect)
                )
            for i in geometry_collect.findall("WiringObject"):
                self.geometries.append(
                    GeometryWiringObject(xml_node=i, xml_parent=geometry_collect)
                )
            for i in geometry_collect.findall("GeometryReference"):
                self.geometries.append(
                    GeometryReference(xml_node=i, xml_parent=geometry_collect)
                )
            for i in geometry_collect.findall("Laser"):
                self.geometries.append(
                    GeometryLaser(xml_node=i, xml_parent=geometry_collect)
                )
            for i in geometry_collect.findall("Support"):
                self.geometries.append(
                    GeometrySupport(xml_node=i, xml_parent=geometry_collect)
                )
            for i in geometry_collect.findall("Structure"):
                self.geometries.append(
                    GeometryStructure(xml_node=i, xml_parent=geometry_collect)
                )
            for i in geometry_collect.findall("Display"):
                self.geometries.append(
                    GeometryDisplay(xml_node=i, xml_parent=geometry_collect)
                )
            for i in geometry_collect.findall("Magnet"):
                self.geometries.append(
                    GeometryMagnet(xml_node=i, xml_parent=geometry_collect)
                )

        dmx_mode_collect = self._root.find("DMXModes")
        if dmx_mode_collect is not None:
            self.dmx_modes = DmxModes(
                [
                    DmxMode(xml_node=i, fixture_type=self)
                    for i in dmx_mode_collect.findall("DMXMode")
                ]
            )
        else:
            self.dmx_modes = DmxModes()

        if not len(self.dmx_modes):
            self.dmx_modes.append(DmxMode(name="Default"))

        # some files are broken and have no link to geometry from dmx mode
        for mode in self.dmx_modes:
            if mode.geometry is None:
                if self.geometries:
                    mode.geometry = self.geometries[0].name

        revision_collect = self._root.find("Revisions")
        if revision_collect is not None:
            self.revisions = Revisions(
                [Revision(xml_node=i) for i in revision_collect.findall("Revision")]
            )
        else:
            self.revisions = Revisions()

        self.protocols = []
        protocols_collect = self._root.find("Protocols")
        if protocols_collect is not None:
            for i in protocols_collect.findall("FTRDM"):
                self.protocols.append(Rdm(xml_node=i))
            for i in protocols_collect.findall("Art-Net"):
                self.protocols.append(ArtNet(xml_node=i))
            for i in protocols_collect.findall("sACN"):
                self.protocols.append(Sacn(xml_node=i))
            for i in protocols_collect.findall("PosiStageNet"):
                self.protocols.append(PosiStageNet(xml_node=i))
            for i in protocols_collect.findall("OpenSoundControl"):
                self.protocols.append(OpenSoundControl(xml_node=i))
            for i in protocols_collect.findall("CITP"):
                self.protocols.append(Citp(xml_node=i))


class Thumbnails(BaseNode):
    def __init__(
        self,
        png: Optional["Resource"] = None,
        svg: Optional["Resource"] = None,
        fixture_type: Optional["FixtureType"] = None,
        *args,
        **kwargs,
    ):
        self.png = png
        self.svg = svg
        self.fixture_type = fixture_type
        super().__init__(*args, **kwargs)

        if self.fixture_type is not None and self.fixture_type._package is not None:
            if (
                self.png is not None
                and f"{self.png.name}.png" in self.fixture_type._package.namelist()
            ):
                self.png.extension = "png"
                self.png.crc = self.fixture_type._package.getinfo(
                    f"{self.png.name}.png"
                ).CRC
            else:
                self.png = None

            if (
                self.svg is not None
                and f"{self.svg.name}.svg" in self.fixture_type._package.namelist()
            ):
                self.svg.extension = "svg"
                self.svg.crc = self.fixture_type._package.getinfo(
                    f"{self.svg.name}.svg"
                ).CRC
            else:
                self.svg = None

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        name = xml_node.attrib.get("Thumbnail", "")
        self.png = Resource(name=name)
        self.svg = Resource(name=name)


class ActivationGroup(BaseNode):
    def __init__(self, name: Optional[str] = None, *args, **kwargs):
        self.name = name
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.name = xml_node.attrib.get("Name")


class FeatureGroup(BaseNode):
    def __init__(
        self,
        name: Optional[str] = None,
        pretty: Optional[str] = None,
        features: Optional[List["Feature"]] = None,
        *args,
        **kwargs,
    ):
        self.name = name
        self.pretty = pretty
        if features is not None:
            self.features = features
        else:
            self.features = []
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.name = xml_node.attrib.get("Name")
        self.pretty = xml_node.attrib.get("Pretty")
        self.features = [Feature(xml_node=i) for i in xml_node.findall("Feature")]


class Feature(BaseNode):
    def __init__(self, name: Optional[str] = None, *args, **kwargs):
        self.name = name
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.name = xml_node.attrib.get("Name")


class Attribute(BaseNode):
    def __init__(
        self,
        name: Optional[str] = None,
        pretty: Optional[str] = None,
        activation_group: Optional["NodeLink"] = None,
        feature: Optional["NodeLink"] = None,
        main_attribute: Optional["NodeLink"] = None,
        physical_unit: "PhysicalUnit" = PhysicalUnit(None),
        color: Optional["ColorCIE"] = None,
        subphysical_units: Optional[List["SubPhysicalUnit"]] = None,
        *args,
        **kwargs,
    ):
        self.name = name
        self.pretty = pretty
        self.activation_group = activation_group
        self.feature = feature
        self.main_attribute = main_attribute
        self.physical_unit = physical_unit
        self.color = color
        self.subphysical_units = (
            subphysical_units if subphysical_units is not None else []
        )
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.name = xml_node.attrib.get("Name")
        self.pretty = xml_node.attrib.get("Pretty")
        self.activation_group = NodeLink(
            "ActivationGroups", xml_node.attrib.get("ActivationGroup")
        )
        self.feature = NodeLink("FeatureGroups", xml_node.attrib.get("Feature"))
        self.main_attribute = NodeLink(
            "Attribute", xml_node.attrib.get("MainAttribute")
        )
        self.physical_unit = PhysicalUnit(xml_node.attrib.get("PhysicalUnit"))
        self.color = ColorCIE(str_repr=xml_node.attrib.get("Color"))
        self.subphysical_units = [
            SubPhysicalUnit(xml_node=i) for i in xml_node.findall("SubPhysicalUnit")
        ]


class SubPhysicalUnit(BaseNode):
    def __init__(
        self,
        unit_type: Optional["SubPhysicalUnitType"] = None,
        physical_unit: Optional["PhysicalUnit"] = None,
        physical_from: float = 0.0,
        physical_to: float = 1.0,
        *args,
        **kwargs,
    ):
        self.type = unit_type
        if self.type is None:
            self.type = SubPhysicalUnitType(None)

        self.physical_unit = physical_unit
        if self.physical_unit is None:
            self.physical_unit = PhysicalUnit(None)

        self.physical_from = physical_from
        self.physical_to = physical_to
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.type = SubPhysicalUnitType(xml_node.attrib.get("Type"))
        self.physical_unit = PhysicalUnit(xml_node.attrib.get("PhysicalUnit", "None"))
        self.physical_from = float(xml_node.attrib.get("PhysicalFrom", 0.0))
        self.physical_to = float(xml_node.attrib.get("PhysicalTo", 1.0))


class Wheel(BaseNode):
    def __init__(
        self,
        name: Optional[str] = None,
        wheel_slots: Optional[List["WheelSlot"]] = None,
        *args,
        **kwargs,
    ):
        self.name = name
        if wheel_slots is not None:
            self.wheel_slots = wheel_slots
        else:
            self.wheel_slots = []
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.name = xml_node.attrib.get("Name")
        self.wheel_slots = [WheelSlot(xml_node=i) for i in xml_node.findall("Slot")]


class WheelSlot(BaseNode):
    def __init__(
        self,
        name: Optional[str] = None,
        color: Optional["ColorCIE"] = None,
        whl_filter: Optional["NodeLink"] = None,
        media_file_name: Optional["Resource"] = None,
        facets: Optional[List["PrismFacet"]] = None,
        animation_system: Optional["AnimationSystem"] = None,
        *args,
        **kwargs,
    ):
        self.name = name
        self.color = color
        self.filter = whl_filter
        self.media_file_name = media_file_name
        if facets is not None:
            self.facets = facets
        else:
            self.facets = []
        self.animation_system = animation_system
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.name = xml_node.attrib.get("Name")
        self.color = ColorCIE(str_repr=xml_node.attrib.get("Color"))
        self.filter = NodeLink("FilterCollect", xml_node.attrib.get("Filter"))
        self.media_file_name = Resource(
            name=xml_node.attrib.get("MediaFileName", ""), extension="png"
        )
        self.facets = [PrismFacet(xml_node=i) for i in xml_node.findall("Facet")]
        animation_system_node = xml_node.find("AnimationSystem")
        if animation_system_node is not None:
            self.animation_system = AnimationSystem(xml_node=animation_system_node)


class PrismFacet(BaseNode):
    def __init__(
        self,
        color: Optional["ColorCIE"] = None,
        rotation: Optional["Rotation"] = None,
        *args,
        **kwargs,
    ):
        self.color = color
        self.rotation = rotation
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.color = ColorCIE(str_repr=xml_node.attrib.get("Color"))
        self.rotation = Rotation(str_repr=xml_node.attrib.get("Rotation"))


class AnimationSystem(BaseNode):
    def __init__(
        self,
        p1: Optional[List[float]] = None,
        p2: Optional[List[float]] = None,
        p3: Optional[List[float]] = None,
        radius: float = 0.0,
        *args,
        **kwargs,
    ):
        self.p1 = p1 if p1 is not None else []
        self.p2 = p2 if p2 is not None else []
        self.p3 = p3 if p3 is not None else []
        self.radius = radius
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        p1_str = xml_node.attrib.get("P1")
        if p1_str:
            self.p1 = [float(x.strip()) for x in p1_str.split(",")]

        p2_str = xml_node.attrib.get("P2")
        if p2_str:
            self.p2 = [float(x.strip()) for x in p2_str.split(",")]

        p3_str = xml_node.attrib.get("P3")
        if p3_str:
            self.p3 = [float(x.strip()) for x in p3_str.split(",")]

        radius_str = xml_node.attrib.get("Radius")
        if radius_str:
            self.radius = float(radius_str)


class Emitter(BaseNode):
    def __init__(
        self,
        name: Optional[str] = None,
        color: Optional["ColorCIE"] = None,
        dominant_wave_length: Optional[float] = None,
        diode_part: Optional[str] = None,
        *args,
        **kwargs,
    ):
        self.name = name
        self.color = color
        self.dominant_wave_length = dominant_wave_length
        self.diode_part = diode_part
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.name = xml_node.attrib.get("Name")
        self.color = ColorCIE(str_repr=xml_node.attrib.get("Color"))
        self.dominant_wave_length = float(xml_node.attrib.get("DominantWaveLength", 0))
        self.diode_part = xml_node.attrib.get("DiodePart")
        self.measurements = [
            Measurement(xml_node=i) for i in xml_node.findall("Measurement")
        ]


class Filter(BaseNode):
    def __init__(
        self,
        name: Optional[str] = None,
        color: Optional["ColorCIE"] = None,
        measurements: Optional[List["Measurement"]] = None,
        *args,
        **kwargs,
    ):
        self.name = name
        self.color = color
        if measurements is not None:
            self.measurements = measurements
        else:
            self.measurements = []
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.name = xml_node.attrib.get("Name")
        self.color = ColorCIE(str_repr=xml_node.attrib.get("Color"))
        self.measurements = [
            Measurement(xml_node=i) for i in xml_node.findall("Measurement")
        ]


class Measurement(BaseNode):
    def __init__(
        self,
        physical: Optional[float] = None,
        luminous_intensity: Optional[float] = None,
        transmission: Optional[float] = None,
        interpolation_to: "InterpolationTo" = InterpolationTo(None),
        *args,
        **kwargs,
    ):
        self.physical = physical
        self.luminous_intensity = luminous_intensity
        self.transmission = transmission
        self.interpolation_to = interpolation_to
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.physical = float(xml_node.attrib.get("Physical", 0))
        self.luminous_intensity = float(xml_node.attrib.get("LuminousIntensity", 0))
        self.transmission = float(xml_node.attrib.get("Transmission", 0))
        self.interpolation_to = InterpolationTo(xml_node.attrib.get("InterpolationTo"))
        self.measurement_points = [
            MeasurementPoint(xml_node=i) for i in xml_node.findall("MeasurementPoint")
        ]


class MeasurementPoint(BaseNode):
    def __init__(
        self,
        wave_length: Optional[float] = None,
        energy: Optional[float] = None,
        *args,
        **kwargs,
    ):
        self.wave_length = wave_length
        self.energy = energy
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.wave_length = float(xml_node.attrib.get("WaveLength", 0))
        self.energy = float(xml_node.attrib.get("Energy", 0))


class ColorSpace(BaseNode):
    def __init__(
        self,
        mode: "ColorSpaceMode" = ColorSpaceMode(None),
        definition: Optional["ColorSpaceDefinition"] = None,
        *args,
        **kwargs,
    ):
        self.mode = mode
        if definition is not None:
            self.definition = definition
        else:
            self._match_definition()
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.mode = ColorSpaceMode(xml_node.attrib.get("Mode"))
        if str(self.mode) == "Custom":
            self.red = ColorCIE(str_repr=xml_node.attrib.get("Red"))
            self.green = ColorCIE(str_repr=xml_node.attrib.get("Green"))
            self.blue = ColorCIE(str_repr=xml_node.attrib.get("Blue"))
            self.white_point = ColorCIE(str_repr=xml_node.attrib.get("WhitePoint"))
        else:
            self._match_definition()

    def _match_definition(self):
        # Match the name of the color space mode with a color space definition,
        # this will only work for sRGB, ProPhoto and ANSI modes
        if self.mode is None or str(self.mode) == "Custom":
            return
        elif str(self.mode) == "sRGB":
            self.definition = COLOR_SPACE_SRGB
        elif str(self.mode) == "ProPhoto":
            self.definition = COLOR_SPACE_PROPHOTO
        elif str(self.mode) == "ANSI":
            self.definition = COLOR_SPACE_ANSI


class Point(BaseNode):
    def __init__(
        self,
        dmx_percentage: float = 0.0,
        cfc0: float = 0.0,
        cfc1: float = 0.0,
        cfc2: float = 0.0,
        cfc3: float = 0.0,
        *args,
        **kwargs,
    ):
        self.dmx_percentage = dmx_percentage
        self.cfc0 = cfc0
        self.cfc1 = cfc1
        self.cfc2 = cfc2
        self.cfc3 = cfc3
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.dmx_percentage = float(xml_node.attrib.get("DMXPercentage", 0.0))
        self.cfc0 = float(xml_node.attrib.get("CFC0", 0.0))
        self.cfc1 = float(xml_node.attrib.get("CFC1", 0.0))
        self.cfc2 = float(xml_node.attrib.get("CFC2", 0.0))
        self.cfc3 = float(xml_node.attrib.get("CFC3", 0.0))


class DmxProfile(BaseNode):
    def __init__(
        self,
        name: Optional[str] = None,
        points: Optional[List["Point"]] = None,
        *args,
        **kwargs,
    ):
        self.name = name
        self.points = points if points is not None else []
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.name = xml_node.attrib.get("Name")
        self.points = [Point(xml_node=i) for i in xml_node.findall("Point")]


class Gamut(BaseNode):
    def __init__(
        self,
        name: Optional[str] = None,
        points: Optional[List["ColorCIE"]] = None,
        *args,
        **kwargs,
    ):
        self.name = name
        self.points = points if points is not None else []
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.name = xml_node.attrib.get("Name")
        points_str = xml_node.attrib.get("Points")
        if points_str:
            points_arr = points_str.split(";")
            for p in points_arr:
                self.points.append(ColorCIE(str_repr=p))


class CriGroup(BaseNode):
    def __init__(
        self,
        color_temperature: float = 6000,
        cris: Optional[List["Cri"]] = None,
        *args,
        **kwargs,
    ):
        self.color_temperature = color_temperature
        if cris is not None:
            self.cris = cris
        else:
            self.cris = []
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.color_temperature = float(xml_node.attrib.get("ColorTemperature", 6000))
        self.cris = [Cri(xml_node=i) for i in xml_node.findall("CRI")]


class Cri(BaseNode):
    def __init__(
        self, ces: "Ces" = Ces(None), color_temperature: int = 100, *args, **kwargs
    ):
        self.ces = ces
        self.color_temperature = color_temperature
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.ces = Ces(xml_node.attrib.get("CES"))
        self.color_temperature = int(xml_node.attrib.get("ColorTemperature", 100))


class Models(list):
    def get_model_by_name(self, model_name):
        for model in self:
            if model.name == model_name:
                return model

        return None


class Model(BaseNode):
    def __init__(
        self,
        name: Optional[str] = None,
        length: float = 0,
        width: float = 0,
        height: float = 0,
        primitive_type: "PrimitiveType" = PrimitiveType(None),
        file: Optional["Resource"] = None,
        *args,
        **kwargs,
    ):
        self.name = name
        self.length = length
        self.width = width
        self.height = height
        self.primitive_type = primitive_type
        self.file = file
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.name = xml_node.attrib.get("Name")
        self.length = float(xml_node.attrib.get("Length", 0))
        self.width = float(xml_node.attrib.get("Width", 0))
        self.height = float(xml_node.attrib.get("Height", 0))
        self.primitive_type = PrimitiveType(xml_node.attrib.get("PrimitiveType"))
        self.file = Resource(xml_node.attrib.get("File", ""))


class DmxChannels(list):
    def as_dict(self):
        """Returns channels as dicts"""
        return [item for dmx_channel in self for item in dmx_channel.as_dict()]

    def flattened(self):
        # use on list by breaks
        return DmxChannels(
            [channel for break_channels in self for channel in break_channels]
        )

    def by_breaks(self, as_dict=False):
        # this is to unflatten the list
        grouped = {}

        for item in self:
            key = item.dmx_break

            if key not in grouped:
                grouped[key] = []
            if as_dict:
                grouped[key] += item.as_dict()
            else:
                grouped[key].append(item)

        return DmxChannels(grouped.values())


class DmxModes(list):
    def get_mode_by_name(self, mode_name):
        for mode in self:
            if mode.name == mode_name:
                return mode
        return None

    def as_dict(self):
        all_modes = []
        for idx, mode in enumerate(self):
            mode_dict = mode.as_dict()
            mode_dict["mode_id"] = idx
            all_modes.append(mode_dict)
        return DmxModes(all_modes)


class DmxMode(BaseNode):
    def __init__(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        geometry: Optional[str] = None,
        _dmx_channels: Optional[List["DmxChannel"]] = None,
        dmx_channels: Optional[List] = None,
        dmx_channels_count: int = 0,
        dmx_breaks: Optional[List["DmxModeBreak"]] = None,
        virtual_channels: Optional[List] = None,
        virtual_channels_count: int = 0,
        relations: Optional[List["Relation"]] = None,
        ft_macros: Optional[List["Macro"]] = None,
        fixture_type: Optional["FixtureType"] = None,
        *args,
        **kwargs,
    ):
        self.name = name
        self.description = description
        self.geometry = geometry
        if _dmx_channels is not None:
            self._dmx_channels = _dmx_channels
        else:
            self._dmx_channels = DmxChannels()
        if dmx_channels is not None:
            self.dmx_channels = dmx_channels
        else:
            self.dmx_channels = DmxChannels()

        if virtual_channels is not None:
            self.virtual_channels = virtual_channels
        else:
            self.virtual_channels = DmxChannels()

        self.dmx_channels_count = dmx_channels_count
        self.virtual_channels_count = virtual_channels_count

        if dmx_breaks is not None:
            self.dmx_breaks = dmx_breaks
        else:
            self.dmx_breaks = []

        if relations is not None:
            self.relations = relations
        else:
            self.relations = []

        if ft_macros is not None:
            self.ft_macros = ft_macros
        else:
            self.ft_macros = []
        self.fixture_type = fixture_type
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.name = xml_node.attrib.get("Name")
        self.description = xml_node.attrib.get("Description", "")
        self.description = self.description.replace(
            "StringConv Failed", ""
        )  # many GDTF files show this issue
        self.geometry = xml_node.attrib.get("Geometry", None)

        dmx_channels_collect = xml_node.find("DMXChannels")
        if dmx_channels_collect is not None:
            self._dmx_channels = [
                DmxChannel(xml_node=i)
                for i in dmx_channels_collect.findall("DMXChannel")
            ]

        self._process_dmx_channels()
        if self._check_for_missing_channels():
            self._process_dmx_channels()

        relations_node = xml_node.find("Relations")
        if relations_node is not None:
            self.relations = [
                Relation(xml_node=i) for i in relations_node.findall("Relation")
            ]

        ftmacros_node = xml_node.find("FTMacros")
        if ftmacros_node is not None:
            self.ft_macros = [
                Macro(xml_node=i) for i in ftmacros_node.findall("FTMacro")
            ]

    def _process_dmx_channels(self):
        dmx_channels = get_dmx_channels(
            gdtf_profile=self.fixture_type,
            dmx_mode=self,
        )

        flattened_channels = [
            channel for break_channels in dmx_channels for channel in break_channels
        ]

        virtual_channels = get_virtual_channels(
            gdtf_profile=self.fixture_type,
            dmx_mode=self,
        )

        self.dmx_channels = DmxChannels(flattened_channels)
        self.virtual_channels = DmxChannels(virtual_channels)

        grouped_breaks: Dict[int, List[int]] = {}
        for channel in self.dmx_channels:
            key = channel.dmx_break
            if key not in grouped_breaks:
                grouped_breaks[key] = []

            if channel.offset is not None:
                grouped_breaks[key] += channel.offset

        self.dmx_breaks = [
            DmxModeBreak(dmx_break, len(set(channel_offsets)))
            for dmx_break, channel_offsets in grouped_breaks.items()
        ]

        self.dmx_channels_count = sum(
            dmx_break.channels_count for dmx_break in self.dmx_breaks
        )

        self.virtual_channels_count = len(self.virtual_channels)

    def _check_for_missing_channels(self):
        # check if channels are missing and add them
        result = False
        highest_offset = 0
        for channel in self.dmx_channels:
            if channel.offset is not None:
                if channel.offset[0] > highest_offset:
                    highest_offset = max(channel.offset)

        if len(self.dmx_channels) != highest_offset:
            # we have missing channels
            for i in range(1, highest_offset + 1):
                found = False
                for channel in self.dmx_channels:
                    if channel.offset is not None:
                        if i in channel.offset:
                            found = True
                            break
                if not found:
                    result = True
                    self._dmx_channels.append(
                        DmxChannel(
                            name="NoFeature",
                            offset=[i],
                            geometry=self.geometry,
                            attribute=NodeLink("Attributes", "NoFeature"),
                        )
                    )
        return result

    def as_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "geometry": self.geometry,
            "dmx_channels": self.dmx_channels.as_dict(),
            "dmx_channels_count": self.dmx_channels_count,
            "dmx_breaks": [dmx_break.as_dict() for dmx_break in self.dmx_breaks],
            "virtual_channels": self.virtual_channels.as_dict(),
            "virtual_channels_count": self.virtual_channels_count,
        }

    def __str__(self):
        return f"{self.name}: {self.dmx_channels_count}ch"

    def __repr__(self):
        return f"{self.name}: {self.dmx_channels_count}ch"


class DmxChannel(BaseNode):
    def __init__(
        self,
        dmx_break: Union[int, str] = 1,
        offset: Optional[List[int]] = None,
        default: "DmxValue" = DmxValue("0/1"),
        attribute: Optional["NodeLink"] = None,
        # ^^^ this is technically not correct but it's a shortcut to an attribute
        # of the LogicalChannel of the Initial function
        highlight: Optional["DmxValue"] = None,
        initial_function: Optional["NodeLink"] = None,
        geometry: Optional[str] = None,
        name: Optional[str] = None,
        logical_channels: Optional[List["LogicalChannel"]] = None,
        *args,
        **kwargs,
    ):
        self.dmx_break = dmx_break
        self.offset = offset
        self.default = default
        self.attribute = attribute
        self.highlight = highlight
        self.initial_function = initial_function
        self.geometry = geometry
        self.name = name
        self.overwrite = False  # we use this during channels processing, to know if geometry reference "Overwrite" has been set

        if logical_channels is not None:
            self.logical_channels = logical_channels
        else:
            # make this invalid GDTF file valid
            self.logical_channels = [
                LogicalChannel(
                    attribute=NodeLink("Attributes", "NoFeature"),
                )
            ]
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        try:
            self.dmx_break = int(xml_node.attrib.get("DMXBreak", 1))
        except ValueError:
            self.dmx_break = "Overwrite"
        _offset = xml_node.attrib.get("Offset")
        if _offset is None or _offset == "None" or _offset == "":
            self.offset = None
        else:
            self.offset = [
                int(i)
                for i in xml_node.attrib.get("Offset", "").split(",")
                if xml_node.attrib.get("Offset")
            ]

        # obsoleted by initial function in GDTF 1.2
        self.default = DmxValue(xml_node.attrib.get("Default", "0/1"))

        highlight_node = xml_node.attrib.get("Highlight")
        if highlight_node is not None:
            highlight_value = xml_node.attrib.get("Highlight", "0/1")

            if highlight_value.lower() != "none":
                # None is a valid value for Highlight
                self.highlight = DmxValue(highlight_value)

        self.geometry = xml_node.attrib.get("Geometry")
        self.logical_channels = [
            LogicalChannel(xml_node=i) for i in xml_node.findall("LogicalChannel")
        ] or [LogicalChannel(attribute=NodeLink("Attributes", "NoFeature"))]

        self.attribute = self.logical_channels[
            0
        ].attribute  # set this as default, later parsing might overwrite it but if not, incomplete or old GDTF files will work correctly

        # get default value

        _logical_channel = self.logical_channels[0]
        self.name = f"{self.geometry}_{_logical_channel.attribute}"
        initial_function_node = xml_node.attrib.get("InitialFunction")
        if initial_function_node:
            self.initial_function = NodeLink(
                xml_node, xml_node.attrib.get("InitialFunction")
            )
            for logical_channel in self.logical_channels:
                logical_channel_name = f"{self.name}.{logical_channel.attribute}"
                for channel_function in logical_channel.channel_functions:
                    channel_function_name = (
                        f"{logical_channel_name}.{channel_function.name}"
                    )
                    if channel_function_name == str(self.initial_function):
                        self.default = channel_function.default
                        self.attribute = logical_channel.attribute

        # calculate dmx_to in channel functions
        for logical_channel in self.logical_channels:
            previous_function_dmx_from = None
            for channel_function in sorted(
                logical_channel.channel_functions,
                key=lambda channel_function: channel_function.dmx_from.value,
                reverse=True,
            ):
                if self.offset is None:
                    byte_count = channel_function.dmx_from.byte_count
                else:
                    byte_count = len(self.offset)

                if previous_function_dmx_from is None:
                    # set max value
                    channel_function.dmx_to = DmxValue("0/1")
                    channel_function.dmx_to.value = (1 << (byte_count * 8)) - 1
                    channel_function.dmx_to.byte_count = byte_count
                    previous_function_dmx_from = channel_function.dmx_from
                    if channel_function.dmx_from.value == 0:
                        # reset in case of mode masters
                        previous_function_dmx_from = None
                else:
                    # set value of the previous dmx_from -1
                    channel_function.dmx_to = copy.deepcopy(previous_function_dmx_from)
                    channel_function.dmx_to.value -= 1
                    previous_function_dmx_from = channel_function.dmx_from

                previous_set_dmx_from = None
                for channel_set in sorted(
                    channel_function.channel_sets,
                    key=lambda channel_set: channel_set.dmx_from.value,
                    reverse=True,
                ):
                    if self.offset is None:
                        byte_count = channel_set.dmx_from.byte_count
                    else:
                        byte_count = len(self.offset)

                    if previous_set_dmx_from is None:
                        # set max value
                        channel_set.dmx_to = DmxValue("0/1")
                        channel_set.dmx_to.value = channel_function.dmx_to.value
                        channel_set.dmx_to.byte_count = byte_count
                        previous_set_dmx_from = channel_set.dmx_from
                    else:
                        # set value of the previous dmx_from -1
                        channel_set.dmx_to = copy.deepcopy(previous_set_dmx_from)
                        channel_set.dmx_to.value -= 1
                        previous_set_dmx_from = channel_set.dmx_from
                    #
                    if channel_set.physical_from.value is None:
                        channel_set.physical_from = PhysicalValue(
                            dmx_to_physical(
                                channel_set.dmx_from.value,
                                channel_element=channel_function,
                            )
                        )
                        channel_set.physical_from.source = PhysicalSource("Function")

                    if channel_set.physical_to.value is None:
                        channel_set.physical_to = PhysicalValue(
                            dmx_to_physical(
                                channel_set.dmx_to.value,
                                channel_element=channel_function,
                            )
                        )
                        channel_set.physical_to.source = PhysicalSource("Function")

    def __str__(self):
        return f"{self.name} ({self.offset})"

    def __repr__(self):
        return f"{self.name} ({self.offset})"

    def as_dict(self):
        dicts_list = []
        for idx, offset_value in enumerate(self.offset or [0]):
            # offset_value 0 means this is virtual channel
            if idx == 0:  # coarse
                dicts_list.append(
                    {
                        "dmx": offset_value,
                        "offset": self.offset,
                        "attribute": self.attribute.str_link,
                        "default": self.default.get_value(),
                        "highlight": self.highlight.get_value()
                        if self.highlight is not None
                        else None,
                        "geometry": self.geometry,
                        "break": self.dmx_break,
                        "logical_channels": [
                            logical_channel.as_dict()
                            for logical_channel in self.logical_channels
                        ],
                    }
                )
            else:
                dicts_list.append(
                    {
                        "dmx": offset_value,
                        "offset": self.offset,
                        "attribute": "+" * idx + self.attribute.str_link,
                        "geometry": self.geometry,
                        "default": self.default.get_value(fine=True),
                    }
                )
        return dicts_list


class LogicalChannel(BaseNode):
    def __init__(
        self,
        attribute: Union["NodeLink", None] = NodeLink("Attributes", "NoFeature"),
        snap: "Snap" = Snap(None),
        master: "Master" = Master(None),
        mib_fade: float = 0,
        dmx_change_time_limit: float = 0,
        channel_functions: Optional[List["ChannelFunction"]] = None,
        *args,
        **kwargs,
    ):
        self.attribute = attribute
        self.snap = snap
        self.master = master
        self.mib_fade = mib_fade
        self.dmx_change_time_limit = dmx_change_time_limit
        if channel_functions is not None:
            self.channel_functions = channel_functions
        else:
            # make this invalid GDTF file valid
            self.channel_functions = [
                ChannelFunction(
                    name="NoFeature",
                    attribute=NodeLink("Attributes", "NoFeature"),
                    default=DmxValue("0/1"),
                )
            ]
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.attribute = NodeLink("Attributes", xml_node.attrib.get("Attribute"))
        self.snap = Snap(xml_node.attrib.get("Snap"))
        self.master = Master(xml_node.attrib.get("Master"))
        self.mib_fade = float(xml_node.attrib.get("MibFade", 0))
        self.dmx_change_time_limit = float(xml_node.attrib.get("DMXChangeTimeLimit", 0))
        self.channel_functions = [
            ChannelFunction(xml_node=i) for i in xml_node.findall("ChannelFunction")
        ] or [
            # make this invalid GDTF file valid
            ChannelFunction(
                attribute=NodeLink("Attributes", "NoFeature"),
                default=DmxValue("0/1"),
            )
        ]
        for index, channel_function in enumerate(self.channel_functions, start=1):
            if channel_function.name is None:
                channel_function.name = f"{channel_function.attribute} {index}"

    def __repr__(self):
        return f"{self.attribute.str_link}"

    def as_dict(self):
        return {
            "attribute": self.attribute.str_link,
            "channel_functions": [
                channel_function.as_dict()
                for channel_function in self.channel_functions
            ],
        }


class ChannelFunction(BaseNode):
    def __init__(
        self,
        name: Optional[str] = None,
        attribute: Union["NodeLink", None] = NodeLink("Attributes", "NoFeature"),
        original_attribute: Optional[str] = None,
        dmx_from: "DmxValue" = DmxValue("0/1"),
        dmx_to: "DmxValue" = DmxValue("0/1"),
        default: "DmxValue" = DmxValue("0/1"),
        physical_from: "PhysicalValue" = PhysicalValue(0),
        physical_to: "PhysicalValue" = PhysicalValue(1),
        real_fade: float = 0,
        real_acceleration: float = 0,
        wheel: Optional["NodeLink"] = None,
        emitter: Optional["NodeLink"] = None,
        chn_filter: Optional["NodeLink"] = None,
        color_space: Optional["NodeLink"] = None,
        gamut: Optional["NodeLink"] = None,
        dmx_profile: Optional["NodeLink"] = None,
        dmx_invert: "DmxInvert" = DmxInvert(None),
        mode_master: Optional["NodeLink"] = None,
        mode_from: "DmxValue" = DmxValue("0/1"),
        mode_to: "DmxValue" = DmxValue("0/1"),
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
        custom_name: Optional[str] = None,
        channel_sets: Optional[List["ChannelSet"]] = None,
        sub_channel_sets: Optional[List["SubChannelSet"]] = None,
        *args,
        **kwargs,
    ):
        self.name = name
        self.attribute = attribute
        self.original_attribute = original_attribute
        self.dmx_from = dmx_from
        self.dmx_to = dmx_to
        self.default = default
        self.physical_from = physical_from
        self.physical_to = physical_to
        self.real_fade = real_fade
        self.real_acceleration = real_acceleration
        self.wheel = wheel
        self.emitter = emitter
        self.filter = chn_filter
        self.color_space = color_space
        self.gamut = gamut
        self.dmx_profile = dmx_profile
        self.dmx_invert = dmx_invert
        self.mode_master = mode_master
        self.mode_from = mode_from
        self.mode_to = mode_to
        self.min_val = min_val
        self.max_val = max_val
        self.custom_name = custom_name
        if channel_sets is not None:
            self.channel_sets = channel_sets
        else:
            self.channel_sets = []
        if sub_channel_sets is not None:
            self.sub_channel_sets = sub_channel_sets
        else:
            self.sub_channel_sets = []
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.name = xml_node.attrib.get("Name")
        self.attribute = NodeLink(
            "Attributes", xml_node.attrib.get("Attribute", "NoFeature")
        )
        self.original_attribute = xml_node.attrib.get("OriginalAttribute")
        self.dmx_from = DmxValue(xml_node.attrib.get("DMXFrom", "0/1"))
        _dmx_from = copy.deepcopy(self.dmx_from)
        _dmx_from.value += 1
        self.dmx_to = _dmx_from
        self.default = DmxValue(xml_node.attrib.get("Default", "0/1"))
        self.physical_from = PhysicalValue(xml_node.attrib.get("PhysicalFrom", 0))
        self.physical_to = PhysicalValue(xml_node.attrib.get("PhysicalTo", 1))
        self.real_fade = float(xml_node.attrib.get("RealFade", 0))
        self.real_acceleration = float(xml_node.attrib.get("RealAcceleration", 0))
        self.wheel = NodeLink("WheelCollect", xml_node.attrib.get("Wheel"))
        self.emitter = NodeLink("EmitterCollect", xml_node.attrib.get("Emitter"))
        self.filter = NodeLink("FilterCollect", xml_node.attrib.get("Filter"))
        self.color_space = NodeLink(
            "PhysicalDescriptions", xml_node.attrib.get("ColorSpace")
        )
        self.gamut = NodeLink("GamutCollect", xml_node.attrib.get("Gamut"))
        self.dmx_profile = NodeLink(
            "DMXProfileCollect", xml_node.attrib.get("DMXProfile")
        )
        self.dmx_invert = DmxInvert(xml_node.attrib.get("DMXInvert"))
        self.mode_master = NodeLink("DMXChannel", xml_node.attrib.get("ModeMaster"))
        self.mode_from = DmxValue(xml_node.attrib.get("ModeFrom", "0/1"))
        self.mode_to = DmxValue(xml_node.attrib.get("ModeTo", "0/1"))
        min_val = xml_node.attrib.get("Min")
        if min_val is not None:
            self.min_val = float(min_val)
        else:
            self.min_val = self.physical_from.value
        max_val = xml_node.attrib.get("Max")
        if max_val is not None:
            self.max_val = float(max_val)
        else:
            self.max_val = self.physical_to.value
        self.custom_name = xml_node.attrib.get("CustomName")
        self.channel_sets = [
            ChannelSet(xml_node=i) for i in xml_node.findall("ChannelSet")
        ]
        self.sub_channel_sets = [
            SubChannelSet(xml_node=i) for i in xml_node.findall("SubChannelSet")
        ]

    def __str__(self):
        return f"{self.name}, {self.attribute.str_link}"

    def __repr__(self):
        return f"Name: {self.name}, Link: {self.attribute}, DMX From: {self.dmx_from}, DMX To: {self.dmx_to}, ChannelSets: {len(self.channel_sets)}"

    def as_dict(self):
        return {
            "name": self.name,
            "attribute": self.attribute.str_link,
            "dmx_from": self.dmx_from.get_value(),
            "dmx_to": self.dmx_to.get_value(),
            "default": self.default.get_value(),
            "real_fade": self.real_fade,
            "physical_to": self.physical_to.value,
            "physical_from": self.physical_from.value,
            "channel_sets": [
                channel_set.as_dict() for channel_set in self.channel_sets
            ],
            # "sub_channel_sets": [
            #    sub_channel_set.as_dict() for sub_channel_set in self.sub_channel_sets
            # ],
        }


class SubChannelSet(BaseNode):
    def __init__(
        self,
        name: Optional[str] = None,
        physical_from: float = 0.0,
        physical_to: float = 1.0,
        sub_physical_unit: Optional["NodeLink"] = None,
        dmx_profile: Optional["NodeLink"] = None,
        *args,
        **kwargs,
    ):
        self.name = name
        self.physical_from = physical_from
        self.physical_to = physical_to
        self.sub_physical_unit = sub_physical_unit
        self.dmx_profile = dmx_profile
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.name = xml_node.attrib.get("Name")
        self.physical_from = float(xml_node.attrib.get("PhysicalFrom", 0.0))
        self.physical_to = float(xml_node.attrib.get("PhysicalTo", 1.0))
        self.sub_physical_unit = NodeLink(
            "Attribute", xml_node.attrib.get("SubPhysicalUnit")
        )
        self.dmx_profile = NodeLink(
            "DMXProfileCollect", xml_node.attrib.get("DMXProfile")
        )


class ChannelSet(BaseNode):
    def __init__(
        self,
        name: Optional[str] = None,
        dmx_from: "DmxValue" = DmxValue("0/1"),
        dmx_to: "DmxValue" = DmxValue("0/1"),
        physical_from: "PhysicalValue" = PhysicalValue(None),
        physical_to: "PhysicalValue" = PhysicalValue(None),
        wheel_slot_index: int = 0,
        *args,
        **kwargs,
    ):
        self.name = name
        self.dmx_from = dmx_from
        self.dmx_to = dmx_to
        self.physical_from = physical_from
        self.physical_to = physical_to
        self.wheel_slot_index = wheel_slot_index
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.name = xml_node.attrib.get("Name")
        self.dmx_from = DmxValue(xml_node.attrib.get("DMXFrom", "0/1"))
        _dmx_from = copy.deepcopy(self.dmx_from)
        _dmx_from.value += 1
        self.dmx_to = _dmx_from
        self.physical_from = PhysicalValue(xml_node.attrib.get("PhysicalFrom", None))
        self.physical_to = PhysicalValue(xml_node.attrib.get("PhysicalTo", None))
        self.wheel_slot_index = max(0, int(xml_node.attrib.get("WheelSlotIndex", 0)))

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"Name: {self.name}, DMX From: {self.dmx_from}, DMX To: {self.dmx_to}"

    def as_dict(self):
        return {
            "name": self.name,
            "dmx_from": self.dmx_from.get_value(),
            "dmx_to": self.dmx_to.get_value(),
            "physical_from": self.physical_from.value,
            "physical_to": self.physical_to.value,
            "wheel_slot_index": self.wheel_slot_index,
        }


class Relation(BaseNode):
    def __init__(
        self,
        name: Optional[str] = None,
        master: Optional["NodeLink"] = None,
        follower: Optional["NodeLink"] = None,
        rel_type: "RelationType" = RelationType(None),
        *args,
        **kwargs,
    ):
        self.name = name
        self.master = master
        self.follower = follower
        self.type = rel_type
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.name = xml_node.attrib.get("Name")
        self.master = NodeLink("DMXMode", xml_node.attrib.get("Master"))
        self.follower = NodeLink("DMXMode", xml_node.attrib.get("Follower"))
        self.type = RelationType(xml_node.attrib.get("Type"))
