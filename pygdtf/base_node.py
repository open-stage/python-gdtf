from typing import Dict, List, Optional, Union
from xml.etree import ElementTree
from xml.etree.ElementTree import Element


class BaseNode:
    def __init__(
        self,
        xml_node: Optional["Element"] = None,
        xml_parent: Optional["Element"] = None,
    ):
        if xml_node is not None:
            self._read_xml(xml_node, xml_parent)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        pass
