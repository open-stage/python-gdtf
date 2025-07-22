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

from typing import List, Optional
from xml.etree.ElementTree import Element

from .base_node import BaseNode
from .dmxbreak import *
from .value import *  # type: ignore


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
        root_geometry: Optional["Geometry"] = None,
        geometry_class: Optional["Geometry"] = None,
    ) -> List["Geometry"]:
        """Recursively find all geometries of a given type. Requires a root geometry"""

        def iterate_geometries(collector):
            for g in collector.geometries:
                if type(g) is geometry_class:
                    matched.append(g)
                if hasattr(g, "geometries"):
                    iterate_geometries(g)

        matched: List["Geometry"] = []
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
        throw_ratio: float = 1.0,
        rectangle_ratio: float = 1.7777,
        emitter_spectrum: Optional["NodeLink"] = None,
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
        self.throw_ratio = throw_ratio
        self.rectangle_ratio = rectangle_ratio
        self.emitter_spectrum = emitter_spectrum
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
        self.throw_ratio = float(xml_node.attrib.get("ThrowRatio", 1.0))
        self.rectangle_ratio = float(xml_node.attrib.get("RectangleRatio", 1.7777))
        self.emitter_spectrum = NodeLink(
            "EmitterCollect", xml_node.attrib.get("EmitterSpectrum")
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


class PinPatch(BaseNode):
    def __init__(
        self,
        to_wiring_object: Optional["NodeLink"] = None,
        from_pin: int = 0,
        to_pin: int = 0,
        *args,
        **kwargs,
    ):
        self.to_wiring_object = to_wiring_object
        self.from_pin = from_pin
        self.to_pin = to_pin
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.to_wiring_object = NodeLink(
            "WiringObject", xml_node.attrib.get("ToWiringObject")
        )
        self.from_pin = int(xml_node.attrib.get("FromPin", 0))
        self.to_pin = int(xml_node.attrib.get("ToPin", 0))


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
        pin_patches: Optional[List["PinPatch"]] = None,
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
        self.pin_patches = pin_patches if pin_patches is not None else []
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
        self.pin_patches = [PinPatch(xml_node=i) for i in xml_node.findall("PinPatch")]


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
