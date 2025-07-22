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

from enum import Enum as pyEnum
from typing import Optional
from xml.etree.ElementTree import Element

from .base_node import BaseNode
from .utils import *
from .value import *  # type: ignore


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
        modified_by: Optional[str] = None,
        *args,
        **kwargs,
    ):
        self.text = text
        self.date = date
        self.user_id = user_id
        self.modified_by = modified_by
        super().__init__(*args, **kwargs)

    def _read_xml(self, xml_node: "Element", xml_parent: Optional["Element"] = None):
        self.text = xml_node.attrib.get("Text")
        self.date = xml_node.attrib.get("Date")
        self.user_id = int(xml_node.attrib.get("UserID", 0))
        self.modified_by = xml_node.attrib.get("ModifiedBy")

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
        return {
            "text": self.text,
            "date": self.date,
            "user_id": self.user_id,
            "modified_by": self.modified_by,
        }
