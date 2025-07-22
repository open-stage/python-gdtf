from typing import List, Optional, Union, Dict
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from .base_node import BaseNode
from .value import *  # type: ignore


class PresetValue(BaseNode):
    def __init__(
        self,
        attribute: Optional["NodeLink"] = None,
        value: "DmxValue" = DmxValue("0/1"),
        *args,
        **kwargs,
    ):
        self.attribute = attribute
        self.value = value
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.attribute = NodeLink("Attributes", xml_node.attrib.get("Attribute"))
        self.value = DmxValue(xml_node.attrib.get("Value", "0/1"))

    def as_dict(self):
        return {
            "attribute": self.attribute.str_link,
            "value": self.value.get_value(),
        }


class FTPreset(BaseNode):
    def __init__(
        self,
        name: Optional[str] = None,
        values: Optional[List["PresetValue"]] = None,
        *args,
        **kwargs,
    ):
        self.name = name
        self.values = values if values is not None else []
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.name = xml_node.attrib.get("Name")
        self.values = [PresetValue(xml_node=i) for i in xml_node.findall("Value")]

    def as_dict(self):
        return {
            "name": self.name,
            "values": [v.as_dict() for v in self.values],
        }


class FTPresets(list):
    def get_preset_by_name(self, name):
        for preset in self:
            if preset.name == name:
                return preset
        return None

    def as_dict(self):
        return [p.as_dict() for p in self]
