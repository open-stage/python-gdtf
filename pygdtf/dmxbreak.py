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

    def __repr__(self):
        return f"Break: {self.dmx_break}, Offset: {self.dmx_offset}"
