from typing import List, Optional, Union, Dict
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from .base_node import BaseNode
from .value import *  # type: ignore


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
