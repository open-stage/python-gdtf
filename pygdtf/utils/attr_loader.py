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

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional
from xml.etree import ElementTree


def _annex_attr_path() -> Path:
    """Return path to structured Annex attribute XML."""
    return Path(__file__).resolve().parents[2] / "AttributeDefinitions.xml"


def _parse_attribute_definitions_xml(xml_path: Path) -> Dict[str, Any]:
    root = ElementTree.parse(xml_path).getroot()

    activation_group_nodes = root.find("ActivationGroups")
    activation_groups = [
        ag.attrib.get("Name")
        for ag in (
            activation_group_nodes.findall("ActivationGroup")
            if activation_group_nodes is not None
            else []
        )
        if ag.attrib.get("Name")
    ]

    feature_group_nodes = root.find("FeatureGroups")
    feature_groups = []
    if feature_group_nodes is not None:
        for feature_group in feature_group_nodes.findall("FeatureGroup"):
            feature_groups.append(
                {
                    "name": feature_group.attrib.get("Name"),
                    "pretty": feature_group.attrib.get("Pretty"),
                    "features": [
                        feature.attrib.get("Name")
                        for feature in feature_group.findall("Feature")
                        if feature.attrib.get("Name")
                    ],
                }
            )

    attribute_nodes = root.find("Attributes")
    attributes = []
    if attribute_nodes is not None:
        for attr in attribute_nodes.findall("Attribute"):
            attributes.append(
                {
                    "name": attr.attrib.get("Name"),
                    "pretty": attr.attrib.get("Pretty"),
                    "activation_group": attr.attrib.get("ActivationGroup"),
                    "feature": attr.attrib.get("Feature"),
                    "main_attribute": attr.attrib.get("MainAttribute"),
                    "physical_unit": attr.attrib.get("PhysicalUnit"),
                    "color": attr.attrib.get("Color"),
                    "subphysical_units": [
                        {
                            "Type": spu.attrib.get("Type"),
                            "PhysicalUnit": spu.attrib.get("PhysicalUnit"),
                            "PhysicalFrom": spu.attrib.get("PhysicalFrom"),
                            "PhysicalTo": spu.attrib.get("PhysicalTo"),
                        }
                        for spu in attr.findall("SubPhysicalUnit")
                    ],
                }
            )

    return {
        "activation_groups": activation_groups,
        "feature_groups": feature_groups,
        "attributes": attributes,
    }


def _build_templates_from_data(data: Dict[str, Any]) -> Dict[str, Any]:
    activation_groups = data.get("activation_groups", [])
    feature_groups = data.get("feature_groups", [])

    attributes_exact: Dict[str, Dict[str, Any]] = {}
    attributes_wildcard: List[Dict[str, Any]] = []

    for attr in data.get("attributes", []):
        template = {
            "name": attr.get("name"),
            "pretty": attr.get("pretty"),
            "activation_group": attr.get("activation_group"),
            "feature": attr.get("feature"),
            "main_attribute": attr.get("main_attribute"),
            "physical_unit": attr.get("physical_unit"),
            "color": attr.get("color"),
            "subphysical_units": attr.get("subphysical_units", []),
        }
        name = template["name"]
        if not name:
            continue
        if "(n)" in name or "(m)" in name:
            pattern = re.escape(name)
            pattern = pattern.replace("\\(n\\)", "(?P<n>\\d+)")
            pattern = pattern.replace("\\(m\\)", "(?P<m>\\d+)")
            attributes_wildcard.append(
                {
                    **template,
                    "pattern": re.compile(f"^{pattern}$"),
                }
            )
        else:
            attributes_exact[name] = template

    return {
        "activation_groups": activation_groups,
        "feature_groups": feature_groups,
        "attributes": {
            "exact": attributes_exact,
            "wildcard": attributes_wildcard,
        },
    }


@lru_cache(maxsize=1)
def _load_annex_attribute_templates():
    """Load Annex attribute definitions from generated module or XML."""
    try:
        from . import attribute_definitions_data as _attr_data_module

        raw_data = getattr(_attr_data_module, "ANNEX_ATTRIBUTE_DEFINITIONS", None)
    except Exception:
        raw_data = None

    if raw_data is None:
        raw_data = _parse_attribute_definitions_xml(_annex_attr_path())

    return _build_templates_from_data(raw_data)


def generate_attribute_definitions_module(
    xml_path: Optional[Path] = None, output_path: Optional[Path] = None
) -> Path:
    """
    Generate a Python module with AttributeDefinitions data for zero-IO startup.

    The generated module exports ANNEX_ATTRIBUTE_DEFINITIONS matching the XML content.
    """
    source = Path(xml_path) if xml_path is not None else _annex_attr_path()
    target = (
        Path(output_path)
        if output_path is not None
        else Path(__file__).resolve().parent / "attribute_definitions_data.py"
    )

    data = _parse_attribute_definitions_xml(source)
    # Use repr so generated file is valid Python (no JSON null/true/false).
    content = (
        "# Auto-generated from AttributeDefinitions XML; do not edit by hand.\n"
        f"# Source: {source.name}\n"
        "ANNEX_ATTRIBUTE_DEFINITIONS = " + repr(data) + "\n"
    )
    target.write_text(content, encoding="utf-8")
    return target
