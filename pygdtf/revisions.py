from typing import List, Optional, Union, Dict
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from .base_node import BaseNode
from .value import *  # type: ignore
from enum import Enum as pyEnum
from .utils import *


class Revisions(list):
    def sorted(self, reverse: bool = True):
        # reverse True: first item is the latest
        return sorted(
            self,
            key=lambda revision: parse_date(revision.date),
            reverse=reverse,
        )

    def as_dict(self, reverse: bool = True):
        return [revision.as_dict() for revision in self.sorted(reverse=reverse)]


class Revision(BaseNode):
    def __init__(
        self,
        text: Optional[str] = None,
        date: Optional[str] = None,
        user_id: int = 0,
        *args,
        **kwargs,
    ):
        self.text = text
        self.date = date
        self.user_id = user_id
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.text = xml_node.attrib.get("Text")
        self.date = xml_node.attrib.get("Date")
        self.user_id = int(xml_node.attrib.get("UserID", 0))

    class date_formats(pyEnum):
        STRING = "string"
        DATETIME = "datetime"
        TIMESTAMP = "timestamp"

    def get_date(self, format_as: "date_formats" = date_formats.STRING):
        if self.date is not None:
            if format_as == self.date_formats.DATETIME:
                return parse_date(self.date)
            elif format_as == self.date_formats.STRING:
                return self.date
            elif format_as == self.date_formats.TIMESTAMP:
                return int(parse_date(self.date).timestamp())

    def __str__(self):
        return f"{self.text} {self.date}"

    def __repr__(self):
        return f"{self.text} {self.date}"

    def as_dict(self):
        return {"text": self.text, "date": self.date, "user_id": self.user_id}
