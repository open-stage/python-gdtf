from typing import Dict, List, Optional, Union
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from .base_node import BaseNode
from .value import *  # type: ignore


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
