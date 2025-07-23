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
from .value import *  # type: ignore


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


class PosiStageNet(BaseNode):
    pass


class OpenSoundControl(BaseNode):
    pass


class Citp(BaseNode):
    pass
