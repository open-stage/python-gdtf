from enum import Enum as pyEnum
from typing import Dict, List, Optional, Union
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from .base_node import BaseNode
from .value import *  # type: ignore


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
