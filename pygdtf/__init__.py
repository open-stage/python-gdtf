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
from enum import Enum as pyEnum
from typing import List, Optional, Union, Dict
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from .utils import *
from .value import *  # type: ignore

__version__ = "1.2.1"

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
    return ElementTree.fromstring(description_str)


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


class BaseNode:
    def __init__(
        self,
        xml_node: Optional["Element"] = None,
        xml_parent: Optional["Element"] = None,
    ):
        if xml_node is not None:
            self._read_xml(xml_node, xml_parent)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        pass


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
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.name = xml_node.attrib.get("Name")
        self.color = ColorCIE(str_repr=xml_node.attrib.get("Color"))
        self.filter = NodeLink("FilterCollect", xml_node.attrib.get("Filter"))
        self.media_file_name = Resource(xml_node.attrib.get("MediaFileName", ""), "png")
        self.facets = [PrismFacet(xml_node=i) for i in xml_node.findall("Facet")]


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


class DmxProfile(BaseNode):
    pass


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


class Geometries(list):
    def get_geometry_by_name(self, geometry_name):
        """Operates on the while kinematic chain of the device"""

        def iterate_geometries(collector):
            if hasattr(collector, "name"):
                if collector.name == geometry_name:
                    matched.append(collector)

            iterator = collector
            if hasattr(collector, "geometries"):
                iterator = collector.geometries

            for g in iterator:
                if g.name == geometry_name:
                    matched.append(g)
                if hasattr(g, "geometries"):
                    iterate_geometries(g)

        matched = []
        iterate_geometries(self)
        if matched:
            return matched[0]

        return None

    @staticmethod
    def get_geometry_by_type(
        root_geometry: Optional["pygdtf.Geometry"] = None,
        geometry_class: Optional["pygdtf.Geometry"] = None,
    ) -> List["pygdtf.Geometry"]:
        """Recursively find all geometries of a given type. Requires a root geometry"""

        def iterate_geometries(collector):
            for g in collector.geometries:
                if type(g) is geometry_class:
                    matched.append(g)
                if hasattr(g, "geometries"):
                    iterate_geometries(g)

        matched: List["pygdtf.Geometry"] = []
        iterate_geometries(root_geometry)
        return matched


class Geometry(BaseNode):
    def __init__(
        self,
        name: Optional[str] = None,
        parent_name: Optional[str] = None,
        model: Optional[str] = None,
        position: "Matrix" = Matrix(0),
        geometries: Optional[List] = None,
        *args,
        **kwargs,
    ):
        self.name = name
        self.parent_name = parent_name
        self.model = model
        self.position = position
        if geometries is not None:
            self.geometries = geometries
        else:
            self.geometries = Geometries()
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.name = xml_node.attrib.get("Name")
        if xml_parent is not None:
            self.parent_name = xml_parent.get("Name")

        self.model = xml_node.attrib.get("Model")
        self.position = Matrix(xml_node.attrib.get("Position", 0))
        for i in xml_node.findall("Geometry"):
            self.geometries.append(Geometry(xml_node=i, xml_parent=xml_node))
        for i in xml_node.findall("Axis"):
            self.geometries.append(GeometryAxis(xml_node=i, xml_parent=xml_node))
        for i in xml_node.findall("FilterBeam"):
            self.geometries.append(GeometryFilterBeam(xml_node=i, xml_parent=xml_node))
        for i in xml_node.findall("FilterColor"):
            self.geometries.append(GeometryFilterColor(xml_node=i, xml_parent=xml_node))
        for i in xml_node.findall("FilterGobo"):
            self.geometries.append(GeometryFilterGobo(xml_node=i, xml_parent=xml_node))
        for i in xml_node.findall("FilterShaper"):
            self.geometries.append(
                GeometryFilterShaper(xml_node=i, xml_parent=xml_node)
            )
        for i in xml_node.findall("MediaServerMaster"):
            self.geometries.append(
                GeometryMediaServerMaster(xml_node=i, xml_parent=xml_node)
            )
        for i in xml_node.findall("MediaServerLayer"):
            self.geometries.append(
                GeometryMediaServerLayer(xml_node=i, xml_parent=xml_node)
            )
        for i in xml_node.findall("MediaServerCamera"):
            self.geometries.append(
                GeometryMediaServerCamera(xml_node=i, xml_parent=xml_node)
            )
        for i in xml_node.findall("Inventory"):
            self.geometries.append(GeometryInventory(xml_node=i, xml_parent=xml_node))
        for i in xml_node.findall("Beam"):
            self.geometries.append(GeometryBeam(xml_node=i, xml_parent=xml_node))
        for i in xml_node.findall("WiringObject"):
            self.geometries.append(
                GeometryWiringObject(xml_node=i, xml_parent=xml_node)
            )
        for i in xml_node.findall("GeometryReference"):
            self.geometries.append(GeometryReference(xml_node=i, xml_parent=xml_node))
        for i in xml_node.findall("Laser"):
            self.geometries.append(GeometryLaser(xml_node=i, xml_parent=xml_node))
        for i in xml_node.findall("Structure"):
            self.geometries.append(GeometryStructure(xml_node=i, xml_parent=xml_node))
        for i in xml_node.findall("Support"):
            self.geometries.append(GeometrySupport(xml_node=i, xml_parent=xml_node))
        for i in xml_node.findall("Magnet"):
            self.geometries.append(GeometryMagnet(xml_node=i, xml_parent=xml_node))
        for i in xml_node.findall("Display"):
            self.geometries.append(GeometryDisplay(xml_node=i, xml_parent=xml_node))

    def __str__(self):
        return f"{self.name} ({self.model})"


class GeometryAxis(Geometry):
    pass


class GeometryFilterBeam(Geometry):
    pass


class GeometryFilterColor(Geometry):
    pass


class GeometryFilterGobo(Geometry):
    pass


class GeometryFilterShaper(Geometry):
    pass


class GeometryMediaServerLayer(Geometry):
    pass


class GeometryMediaServerCamera(Geometry):
    pass


class GeometryMediaServerMaster(Geometry):
    pass


class GeometryDisplay(Geometry):
    def __init__(self, texture: Optional[str] = None, *args, **kwargs):
        self.texture = texture

        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        super()._read_xml(xml_node, xml_parent)
        self.texture = xml_node.attrib.get("texture")


class GeometryStructure(Geometry):
    def __init__(
        self,
        linked_geometry: Optional[str] = None,
        structure_type: StructureType = StructureType(None),
        cross_section_type: CrossSectionType = CrossSectionType(None),
        cross_section_height: float = 0,
        cross_section_wall_thickness: float = 0,
        truss_cross_section: Optional[str] = None,
        *args,
        **kwargs,
    ):
        self.linked_geometry = linked_geometry
        self.structure_type = structure_type
        self.cross_section_type = cross_section_type
        self.cross_section_height = cross_section_height
        self.cross_section_wall_thickness = cross_section_wall_thickness
        self.truss_cross_section = truss_cross_section

        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        super()._read_xml(xml_node, xml_parent)
        self.linked_geometry = xml_node.attrib.get("LinkedGeometry")
        self.structure_type = StructureType(xml_node.attrib.get("StructureType"))
        self.cross_section_type = CrossSectionType(
            xml_node.attrib.get("CrossSectionType")
        )
        self.cross_section_height = float(xml_node.attrib.get("CrossSectionHeight", 0))
        self.cross_section_wall_thickness = float(
            xml_node.attrib.get("CrossSectionWallThickness", 0)
        )
        self.truss_cross_section = xml_node.attrib.get("TrussCrossSection")


class GeometrySupport(Geometry):
    def __init__(
        self,
        support_type: SupportType = SupportType(None),
        rope_cross_section: Optional[str] = None,
        rope_offset: Vector3 = Vector3(0),
        capacity_x: float = 0,
        capacity_y: float = 0,
        capacity_z: float = 0,
        capacity_xx: float = 0,
        capacity_yy: float = 0,
        capacity_zz: float = 0,
        resistance_x: float = 0,
        resistance_y: float = 0,
        resistance_z: float = 0,
        resistance_xx: float = 0,
        resistance_yy: float = 0,
        resistance_zz: float = 0,
        *args,
        **kwargs,
    ):
        self.support_type = support_type
        self.rope_cross_section = rope_cross_section
        self.rope_offset = rope_offset
        self.capacity_x = capacity_x
        self.capacity_y = capacity_y
        self.capacity_z = capacity_z
        self.capacity_xx = capacity_xx
        self.capacity_yy = capacity_yy
        self.capacity_zz = capacity_zz
        self.resistance_x = resistance_x
        self.resistance_y = resistance_y
        self.resistance_z = resistance_z
        self.resistance_xx = resistance_xx
        self.resistance_yy = resistance_yy
        self.resistance_zz = resistance_zz

        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        super()._read_xml(xml_node, xml_parent)
        self.support_type = SupportType(xml_node.attrib.get("SupportType"))
        self.rope_cross_section = xml_node.attrib.get("RopeCrossSection")
        self.rope_offset = Vector3(xml_node.attrib.get("RopeOffset", 0))
        self.capacity_x = float(xml_node.attrib.get("CapacityX", 0))
        self.capacity_y = float(xml_node.attrib.get("CapacityY", 0))
        self.capacity_z = float(xml_node.attrib.get("CapacityZ", 0))
        self.capacity_xx = float(xml_node.attrib.get("CapacityXX", 0))
        self.capacity_yy = float(xml_node.attrib.get("CapacityYY", 0))
        self.capacity_zz = float(xml_node.attrib.get("CapacityZZ", 0))
        self.resistance_x = float(xml_node.attrib.get("ResistanceX", 0))
        self.resistance_y = float(xml_node.attrib.get("ResistanceY", 0))
        self.resistance_z = float(xml_node.attrib.get("ResistanceZ", 0))
        self.resistance_xx = float(xml_node.attrib.get("ResistanceXX", 0))
        self.resistance_yy = float(xml_node.attrib.get("ResistanceYY", 0))
        self.resistance_zz = float(xml_node.attrib.get("ResistanceZZ", 0))


class GeometryMagnet(Geometry):
    pass


class GeometryInventory(Geometry):
    def __init__(self, count: int = 1, *args, **kwargs):
        self.count = count

        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        super()._read_xml(xml_node, xml_parent)
        self.count = int(xml_node.attrib.get("Count", 1))


class GeometryBeam(Geometry):
    def __init__(
        self,
        lamp_type: "LampType" = LampType(None),
        power_consumption: float = 1000,
        luminous_flux: float = 10000,
        color_temperature: float = 6000,
        beam_angle: float = 25.0,
        field_angle: float = 25.0,
        beam_radius: float = 0.05,
        beam_type: BeamType = BeamType(None),
        color_rendering_index: int = 100,
        *args,
        **kwargs,
    ):
        self.lamp_type = lamp_type
        self.power_consumption = power_consumption
        self.luminous_flux = luminous_flux
        self.color_temperature = color_temperature
        self.beam_angle = beam_angle
        self.field_angle = field_angle
        self.beam_radius = beam_radius
        self.beam_type = beam_type
        self.color_rendering_index = color_rendering_index
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        super()._read_xml(xml_node, xml_parent)
        self.lamp_type = LampType(xml_node.attrib.get("LampType"))
        self.power_consumption = float(xml_node.attrib.get("PowerConsumption", 1000))
        self.luminous_flux = float(xml_node.attrib.get("LuminousFlux", 10000))
        self.color_temperature = float(xml_node.attrib.get("ColorTemperature", 6000))
        self.beam_angle = float(xml_node.attrib.get("BeamAngle", 25))
        self.field_angle = float(xml_node.attrib.get("FieldAngle", 25))
        self.beam_radius = float(xml_node.attrib.get("BeamRadius", 0.05))
        self.beam_type = BeamType(xml_node.attrib.get("BeamType"))
        self.color_rendering_index = int(
            xml_node.attrib.get("ColorRenderingIndex", 100)
        )


class GeometryLaser(Geometry):
    def __init__(
        self,
        color_type: "ColorType" = ColorType(None),
        color: float = 0,
        output_strength: float = 0,
        emitter: Optional["NodeLink"] = None,
        beam_diameter: float = 0,
        beam_divergence_min: float = 0,
        beam_divergence_max: float = 0,
        scan_angle_pan: float = 0,
        scan_angle_tilt: float = 0,
        scan_speed: float = 0,
        protocols: List = [],
        *args,
        **kwargs,
    ):
        self.color_type = color_type
        self.color = color
        self.output_strength = output_strength
        self.emitter = emitter
        self.beam_diameter = beam_diameter
        self.beam_divergence_min = beam_divergence_min
        self.beam_divergence_max = beam_divergence_max
        self.scan_angle_pan = scan_angle_pan
        self.scan_angle_tilt = scan_angle_tilt
        self.scan_speed = scan_speed
        self.protocols = protocols
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        super()._read_xml(xml_node, xml_parent)
        self.color_type = ColorType(xml_node.attrib.get("ColorType"))
        self.color = float(xml_node.attrib.get("Color", 530))  # Green
        self.output_strength = float(xml_node.attrib.get("OutputStrength", 1))
        self.emitter = NodeLink("EmitterCollect", xml_node.attrib.get("Emitter"))
        self.beam_diameter = float(xml_node.attrib.get("BeamDiameter", 0.005))
        self.beam_divergence_min = float(xml_node.attrib.get("BeamDivergenceMin", 0))
        self.beam_divergence_max = float(xml_node.attrib.get("BeamDivergenceMax", 0))
        self.scan_angle_pan = float(xml_node.attrib.get("ScanAnglePan", 30))
        self.scan_angle_tilt = float(xml_node.attrib.get("ScanAngleTilt", 30))
        self.scan_speed = float(xml_node.attrib.get("ScanSpeed", 0))
        self.protocols = [Protocol(xml_node=i) for i in xml_node.findall("Protocol")]


class Protocol(BaseNode):
    def __init__(
        self,
        name: Optional[str] = None,
        *args,
        **kwargs,
    ):
        self.name = name
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.name = xml_node.attrib.get("Name")

    def __str__(self):
        return f"{self.name}"


class GeometryWiringObject(Geometry):
    def __init__(
        self,
        connector_type: Optional[str] = None,
        component_type: "ComponentType" = ComponentType(None),
        signal_type: Optional[str] = None,
        pin_count: int = 0,
        electrical_payload: float = 0,
        voltage_range_max: float = 0,
        voltage_range_min: float = 0,
        frequency_range_max: float = 0,
        frequency_range_min: float = 0,
        max_payload: float = 0,
        voltage: float = 0,
        signal_layer: int = 0,
        cos_phi: float = 0,
        fuse_current: float = 0,
        fuse_rating: "FuseRating" = FuseRating(None),
        orientation: "Orientation" = Orientation(None),
        wire_group: Optional[str] = None,
        *args,
        **kwargs,
    ):
        self.connector_type = connector_type
        self.component_type = component_type
        self.signal_type = signal_type
        self.pin_count = pin_count
        self.electrical_payload = electrical_payload
        self.voltage_range_max = voltage_range_max
        self.voltage_range_min = voltage_range_min
        self.frequency_range_min = frequency_range_min
        self.frequency_range_max = frequency_range_max
        self.max_payload = max_payload
        self.voltage = voltage
        self.signal_layer = signal_layer
        self.cos_phi = cos_phi
        self.fuse_current = fuse_current
        self.fuse_rating = fuse_rating
        self.orientation = orientation
        self.wire_group = wire_group
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        super()._read_xml(xml_node, xml_parent)
        self.connector_type = xml_node.attrib.get("ConnectorType")
        self.component_type = ComponentType(xml_node.attrib.get("ComponentType"))
        self.signal_type = xml_node.attrib.get("SignalType")
        self.pin_count = int(xml_node.attrib.get("PinCount", 0))
        self.electrical_payload = float(xml_node.attrib.get("ElectricalPayLoad", 0))
        self.voltage_range_max = float(xml_node.attrib.get("VoltageRangeMax", 0))
        self.voltage_range_min = float(xml_node.attrib.get("VoltageRangeMin", 0))
        self.frequency_range_max = float(xml_node.attrib.get("FrequencyRangeMax", 0))
        self.frequency_range_min = float(xml_node.attrib.get("FrequencyRangeMin", 0))
        self.max_payload = float(xml_node.attrib.get("MaxPayLoad", 0))
        self.voltage = float(xml_node.attrib.get("Voltage", 0))
        self.signal_layer = int(xml_node.attrib.get("SignalLayer", 0))
        self.cos_phi = float(xml_node.attrib.get("CosPhi", 0))
        self.fuse_current = float(xml_node.attrib.get("FuseCurrent", 0))
        self.fuse_rating = FuseRating(xml_node.attrib.get("FuseRating"))
        self.orientation = Orientation(xml_node.attrib.get("Orientation"))
        self.wire_group = xml_node.attrib.get("WireGroup")


class GeometryReference(BaseNode):
    def __init__(
        self,
        name: Optional[str] = None,
        parent_name: Optional[str] = None,
        position: "Matrix" = Matrix(0),
        geometry: Optional[str] = None,
        model: Optional[str] = None,
        *args,
        **kwargs,
    ):
        self.name = name
        self.parent_name = parent_name
        self.position = position
        self.geometry = geometry
        self.model = model
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.name = xml_node.attrib.get("Name")

        if xml_parent is not None:
            self.parent_name = xml_parent.get("Name")

        self.position = Matrix(xml_node.attrib.get("Position", 0))
        self.geometry = xml_node.attrib.get("Geometry")
        self.model = xml_node.attrib.get("Model")
        self.breaks = [Break(xml_node=i) for i in xml_node.findall("Break")]

    def __str__(self):
        return f"{self.name} ({self.model})"


class Break(BaseNode):
    def __init__(
        self,
        dmx_offset: "DmxAddress" = DmxAddress("1"),
        dmx_break: int = 1,
        *args,
        **kwargs,
    ):
        self.dmx_offset = dmx_offset
        self.dmx_break = dmx_break
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.dmx_offset = DmxAddress(xml_node.attrib.get("DMXOffset"))
        self.dmx_break = int(xml_node.attrib.get("DMXBreak", 1))

    def __str__(self):
        return f"Break: {self.dmx_break}, Offset: {self.dmx_offset}"


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
        self.logical_channels = logical_channels
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

            if highlight_value != "None":
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
                        channel_set.dmx_to.value = (1 << (byte_count * 8)) - 1
                        channel_set.dmx_to.byte_count = byte_count
                        previous_set_dmx_from = channel_set.dmx_from
                    else:
                        # set value of the previous dmx_from -1
                        channel_set.dmx_to = copy.deepcopy(previous_set_dmx_from)
                        channel_set.dmx_to.value -= 1
                        previous_set_dmx_from = channel_set.dmx_from

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
        attribute: Optional["NodeLink"] = None,
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
        attribute: Union["NodeLink", str] = NodeLink("Attributes", "NoFeature"),
        original_attribute: Optional[str] = None,
        dmx_from: "DmxValue" = DmxValue("0/1"),
        dmx_to: "DmxValue" = DmxValue("0/1"),
        default: "DmxValue" = DmxValue("0/1"),
        physical_from: float = 0,
        physical_to: float = 1,
        real_fade: float = 0,
        wheel: Optional["NodeLink"] = None,
        emitter: Optional["NodeLink"] = None,
        chn_filter: Optional["NodeLink"] = None,
        dmx_invert: "DmxInvert" = DmxInvert(None),
        mode_master: Optional["NodeLink"] = None,
        mode_from: "DmxValue" = DmxValue("0/1"),
        mode_to: "DmxValue" = DmxValue("0/1"),
        channel_sets: Optional[List["ChannelSet"]] = None,
        *args,
        **kwargs,
    ):
        self.name = name
        self.attribute = attribute
        self.original_attribute = original_attribute
        self.dmx_from = dmx_from
        self.default = default
        self.physical_from = physical_from
        self.physical_to = physical_to
        self.real_fade = real_fade
        self.wheel = wheel
        self.emitter = emitter
        self.filter = chn_filter
        self.dmx_invert = dmx_invert
        self.mode_master = mode_master
        self.mode_from = mode_from
        self.mode_to = mode_to
        if channel_sets is not None:
            self.channel_sets = channel_sets
        else:
            self.channel_sets = []
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
        self.physical_from = float(xml_node.attrib.get("PhysicalFrom", 0))
        self.physical_to = float(xml_node.attrib.get("PhysicalTo", 1))
        self.real_fade = float(xml_node.attrib.get("RealFade", 0))
        self.wheel = NodeLink("WheelCollect", xml_node.attrib.get("Wheel"))
        self.emitter = NodeLink("EmitterCollect", xml_node.attrib.get("Emitter"))
        self.filter = NodeLink("FilterCollect", xml_node.attrib.get("Filter"))
        self.dmx_invert = DmxInvert(xml_node.attrib.get("DMXInvert"))
        self.mode_master = NodeLink("DMXChannel", xml_node.attrib.get("ModeMaster"))
        self.mode_from = DmxValue(xml_node.attrib.get("ModeFrom", "0/1"))
        self.mode_to = DmxValue(xml_node.attrib.get("ModeTo", "0/1"))
        self.channel_sets = [
            ChannelSet(xml_node=i) for i in xml_node.findall("ChannelSet")
        ]

    def __str__(self):
        return f"{self.name}, {self.attribute.str_link}"

    def __repr__(self):
        return f"Name: {self.name}, Link: {self.attribute}, DMX From: {self.dmx_from}, DMX To: {self.dmx_to}"

    def as_dict(self):
        return {
            "name": self.name,
            "attribute": self.attribute.str_link,
            "dmx_from": self.dmx_from.get_value(),
            "dmx_to": self.dmx_to.get_value(),
            "default": self.default.get_value(),
            "real_fade": self.real_fade,
            "physical_to": self.physical_to,
            "physical_from": self.physical_from,
            "channel_sets": [
                channel_set.as_dict() for channel_set in self.channel_sets
            ],
        }


class ChannelSet(BaseNode):
    def __init__(
        self,
        name: Optional[str] = None,
        dmx_from: "DmxValue" = DmxValue("0/1"),
        dmx_to: "DmxValue" = DmxValue("0/1"),
        physical_from: float = 0,
        physical_to: float = 1,
        wheel_slot_index: int = 1,
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
        self.physical_from = float(xml_node.attrib.get("PhysicalFrom", 0))
        self.physical_to = float(xml_node.attrib.get("PhysicalTo", 1))
        self.wheel_slot_index = int(xml_node.attrib.get("WheelSlotIndex", 1))

    def as_dict(self):
        return {
            "name": self.name,
            "dmx_from": self.dmx_from.get_value(),
            "dmx_to": self.dmx_to.get_value(),
            "physical_from": self.physical_from,
            "physical_to": self.physical_to,
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


class Macro(BaseNode):
    def __init__(
        self,
        name: Optional[str] = None,
        dmx_steps: Optional[List["MacroDmxStep"]] = None,
        visual_steps: Optional[List["MacroVisualStep"]] = None,
        *args,
        **kwargs,
    ):
        self.name = name
        if dmx_steps is not None:
            self.dmx_steps = dmx_steps
        else:
            self.dmx_steps = []
        if visual_steps is not None:
            self.visual_steps = visual_steps
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.name = xml_node.attrib.get("Name")

        macro_dmx_collect = xml_node.find("MacroDMX")
        if macro_dmx_collect is not None:
            self.dmx_steps = [
                MacroDmxStep(xml_node=i)
                for i in macro_dmx_collect.findall("MacroDMXStep")
            ]
        macro_visual_collect = xml_node.find("MacroVisual")
        if macro_visual_collect is not None:
            self.visual_steps = [
                MacroVisualStep(xml_node=i)
                for i in macro_visual_collect.findall("MacroVisualStep")
            ]


class MacroDmxStep(BaseNode):
    def __init__(
        self,
        duration: float = 1,
        dmx_values: Optional[List["MacroDmxValue"]] = None,
        *args,
        **kwargs,
    ):
        self.duration = duration
        if dmx_values is not None:
            self.dmx_values = dmx_values
        else:
            self.dmx_values = []
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.duration = float(xml_node.attrib.get("Duration", 0.0))
        self.dmx_values = [
            MacroDmxValue(xml_node=i) for i in xml_node.findall("MacroDMXValue")
        ]


class MacroDmxValue(BaseNode):
    def __init__(
        self,
        macro_value: Optional["DmxValue"] = None,
        dmx_channel: Optional["NodeLink"] = None,
        *args,
        **kwargs,
    ):
        self.value = macro_value
        self.dmx_channel = dmx_channel
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.value = DmxValue(xml_node.attrib.get("Value"))
        self.dmx_channel = NodeLink(
            "DMXChannelCollect", xml_node.attrib.get("DMXChannel")
        )


class MacroVisualStep(BaseNode):
    def __init__(
        self,
        duration: int = 1,
        fade: float = 0.0,
        delay: float = 0.0,
        visual_values: Optional[List["MacroVisualValue"]] = None,
        *args,
        **kwargs,
    ):
        self.duration = duration
        self.fade = fade
        self.delay = delay
        if visual_values is not None:
            self.visual_values = visual_values
        else:
            self.visual_values = []
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.duration = int(xml_node.attrib.get("Duration", 1))
        self.fade = float(xml_node.attrib.get("Fade", 0.0))
        self.delay = float(xml_node.attrib.get("Delay", 0.0))
        self.visual_values = [
            MacroVisualValue(xml_node=i) for i in xml_node.findall("MacroVisualValue")
        ]


class MacroVisualValue(BaseNode):
    def __init__(
        self,
        macro_value: Optional["DmxValue"] = None,
        channel_function: Optional["NodeLink"] = None,
        *args,
        **kwargs,
    ):
        self.value = macro_value
        self.channel_function = channel_function
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.value = DmxValue(xml_node.attrib.get("Value"))
        self.channel_function = NodeLink(
            "DMXChannelCollect", xml_node.attrib.get("ChannelFunction")
        )


class Revisions(list):
    def sorted(self, reverse: bool = True):
        # reverse True: first item is the latest
        return sorted(
            self,
            key=lambda revision: parse_date(revision.date),
            reverse=reverse,
        )

    def as_dict(self, reverse: bool = True):
        return [revision.as_dict() for revision in self.sorted(reverse=reverse)]


class Revision(BaseNode):
    def __init__(
        self,
        text: Optional[str] = None,
        date: Optional[str] = None,
        user_id: int = 0,
        *args,
        **kwargs,
    ):
        self.text = text
        self.date = date
        self.user_id = user_id
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.text = xml_node.attrib.get("Text")
        self.date = xml_node.attrib.get("Date")
        self.user_id = int(xml_node.attrib.get("UserID", 0))

    class date_formats(pyEnum):
        STRING = "string"
        DATETIME = "datetime"
        TIMESTAMP = "timestamp"

    def get_date(self, format_as: "date_formats" = date_formats.STRING):
        if self.date is not None:
            if format_as == self.date_formats.DATETIME:
                return parse_date(self.date)
            elif format_as == self.date_formats.STRING:
                return self.date
            elif format_as == self.date_formats.TIMESTAMP:
                return int(parse_date(self.date).timestamp())

    def __str__(self):
        return f"{self.text} {self.date}"

    def __repr__(self):
        return f"{self.text} {self.date}"

    def as_dict(self):
        return {"text": self.text, "date": self.date, "user_id": self.user_id}


class Properties(BaseNode):
    def __init__(
        self,
        weight: float = 0,
        operating_temperature_low: float = 0,
        operating_temperature_high: float = 40,
        leg_height: float = 0,
        *args,
        **kwargs,
    ):
        self.weight = weight
        self.leg_height = leg_height
        self.operating_temperature_low = operating_temperature_low
        self.operating_temperature_high = operating_temperature_high

        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        operating_temperatures = xml_node.find("OperatingTemperature")
        if operating_temperatures is not None:
            self.operating_temperature_low = float(
                operating_temperatures.attrib.get("Low", 0)
            )
            self.operating_temperature_high = float(
                operating_temperatures.attrib.get("High", 30)
            )
        leg_height_tag = xml_node.find("LegHeight")
        if leg_height_tag is not None:
            self.leg_height = float(leg_height_tag.attrib.get("Value", 0))

        weight_tag = xml_node.find("Weight")
        if weight_tag is not None:
            self.weight = float(weight_tag.attrib.get("Value", 0))


class Rdm(BaseNode):
    def __init__(
        self,
        manufacturer_id: int = 0,
        device_model_id: int = 0,
        software_versions: Optional[List["SoftwareVersionId"]] = None,
        *args,
        **kwargs,
    ):
        self.manufacturer_id = manufacturer_id
        self.device_model_id = device_model_id
        if software_versions is not None:
            self.software_versions = software_versions
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.manufacturer_id = int(xml_node.attrib.get("ManufacturerID", "0"), 16)
        self.device_model_id = int(xml_node.attrib.get("DeviceModelID", "0"), 16)
        self.software_versions = [
            SoftwareVersionId(xml_node=i) for i in xml_node.findall("SoftwareVersionID")
        ]

    def __str__(self):
        return (
            f"{self.manufacturer_id} ({self.device_model_id}) {self.software_versions}"
        )


class SoftwareVersionId(BaseNode):
    def __init__(
        self,
        value: Optional[str] = None,
        dmx_personalities: Optional[List["DmxPersonality"]] = None,
        *args,
        **kwargs,
    ):
        self.value = value
        if dmx_personalities is not None:
            self.dmx_personalities = dmx_personalities
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.value = xml_node.attrib.get("Value")
        self.dmx_personalities = [
            DmxPersonality(xml_node=i) for i in xml_node.findall("DMXPersonality")
        ]

    def __str__(self):
        return f"{self.value} {self.dmx_personalities}"


class DmxPersonality(BaseNode):
    def __init__(
        self,
        dmx_mode: Optional[str] = None,
        value: Optional[str] = None,
        *args,
        **kwargs,
    ):
        self.dmx_mode = dmx_mode
        self.value = value
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.dmx_mode = xml_node.attrib.get("DMXMode")
        self.value = xml_node.attrib.get("Value")

    def __str__(self):
        return f"{self.dmx_mode} ({self.value})"


class ArtNet(BaseNode):
    def __init__(
        self,
        maps: Optional[List["Map"]] = None,
        *args,
        **kwargs,
    ):
        if maps is not None:
            self.maps = maps
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.maps = [Map(xml_node=i) for i in xml_node.findall("Map")]


class Map(BaseNode):
    def __init__(
        self,
        key: int = 0,
        value: int = 0,
        *args,
        **kwargs,
    ):
        self.key = key
        self.value = value
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.key = int(xml_node.attrib.get("Key", 0))
        self.value = int(xml_node.attrib.get("Value", 0))

    def __str__(self):
        return f"{self.key} {self.value}"


class Sacn(BaseNode):
    pass


class PosiStageNet(BaseNode):
    pass


class OpenSoundControl(BaseNode):
    pass


class Citp(BaseNode):
    pass
