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

from typing import Optional
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
