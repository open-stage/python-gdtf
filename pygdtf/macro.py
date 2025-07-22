from typing import Dict, List, Optional, Union
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from .base_node import BaseNode
from .value import *  # type: ignore


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
