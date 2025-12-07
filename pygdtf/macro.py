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
from xml.etree import ElementTree

from .base_node import BaseNode
from .value import *  # type: ignore


def _dmx_value_str(dmx_value: "DmxValue") -> str:
    return f"{dmx_value.value}/{dmx_value.byte_count}"


class Macro(BaseNode):
    def __init__(
        self,
        name: Optional[str] = None,
        channel_function: Optional["NodeLink"] = None,
        dmx_steps: Optional[List["MacroDmxStep"]] = None,
        *args,
        **kwargs,
    ):
        self.name = name
        self.channel_function = channel_function
        if dmx_steps is not None:
            self.dmx_steps = dmx_steps
        else:
            self.dmx_steps = []
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.name = xml_node.attrib.get("Name")
        self.channel_function = NodeLink(
            "DMXMode", xml_node.attrib.get("ChannelFunction")
        )

        macro_dmx_collect = xml_node.find("MacroDMX")
        if macro_dmx_collect is not None:
            self.dmx_steps = [
                MacroDmxStep(xml_node=i)
                for i in macro_dmx_collect.findall("MacroDMXStep")
            ]

    def to_xml(self):
        attrs = {}
        if self.name:
            attrs["Name"] = self.name
        if self.channel_function and self.channel_function.str_link:
            attrs["ChannelFunction"] = str(self.channel_function.str_link)
        element = Element("FTMacro", attrs)
        if getattr(self, "dmx_steps", None):
            macro_dmx = ElementTree.SubElement(element, "MacroDMX")
            for step in self.dmx_steps:
                macro_dmx.append(step.to_xml())
        return element


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

    def to_xml(self):
        element = Element("MacroDMXStep", {"Duration": str(self.duration)})
        for dmx_value in self.dmx_values:
            element.append(dmx_value.to_xml())
        return element


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

    def to_xml(self):
        attrs = {}
        if self.value is not None:
            attrs["Value"] = _dmx_value_str(self.value)
        if self.dmx_channel and self.dmx_channel.str_link:
            attrs["DMXChannel"] = str(self.dmx_channel.str_link)
        return Element("MacroDMXValue", attrs)
