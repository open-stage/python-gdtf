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

import copy
from collections import deque
from typing import Any, Dict, List, Optional

import pygdtf
from .attr_loader import _load_annex_attribute_templates


def _apply_placeholders(value: Optional[str], groups: Dict[str, str]) -> Optional[str]:
    if not value:
        return value
    result = value
    for key, val in groups.items():
        result = result.replace(f"({key})", val)
        result = result.replace(f"({key.upper()})", val)
    return result


def _build_subphysical_units(
    spu_data: List[Dict[str, Any]],
) -> List["pygdtf.SubPhysicalUnit"]:
    subphysical_units: List["pygdtf.SubPhysicalUnit"] = []
    for spu in spu_data:
        subphysical_units.append(
            pygdtf.SubPhysicalUnit(
                unit_type=pygdtf.SubPhysicalUnitType(spu.get("Type")),
                physical_unit=pygdtf.PhysicalUnit(spu.get("PhysicalUnit")),
                physical_from=float(spu.get("PhysicalFrom", 0) or 0),
                physical_to=float(spu.get("PhysicalTo", 1) or 1),
            )
        )
    return subphysical_units


def _build_attribute_from_template(
    attr_name: str, template: Dict[str, Any], groups: Dict[str, str]
) -> "pygdtf.Attribute":
    activation_group = _apply_placeholders(template.get("activation_group"), groups)
    feature = _apply_placeholders(template.get("feature"), groups)
    main_attribute = _apply_placeholders(template.get("main_attribute"), groups)
    return pygdtf.Attribute(
        name=attr_name,
        pretty=_apply_placeholders(template.get("pretty"), groups),
        activation_group=pygdtf.NodeLink("ActivationGroups", activation_group)
        if activation_group
        else None,
        feature=pygdtf.NodeLink("FeatureGroups", feature) if feature else None,
        main_attribute=pygdtf.NodeLink("Attribute", main_attribute)
        if main_attribute
        else None,
        physical_unit=pygdtf.PhysicalUnit(template.get("physical_unit")),
        color=pygdtf.ColorCIE(str_repr=template.get("color"))
        if template.get("color")
        else None,
        subphysical_units=_build_subphysical_units(
            template.get("subphysical_units", [])
        ),
    )


def _match_attribute_template(attr_name: str, templates: Dict[str, Any]):
    if attr_name in templates["exact"]:
        return templates["exact"][attr_name], {}
    for tmpl in templates["wildcard"]:
        match = tmpl["pattern"].match(attr_name)
        if match:
            return tmpl, match.groupdict()
    return None, {}


def _collect_attribute_names(gdtf_profile: Optional["pygdtf.FixtureType"]) -> List[str]:
    """Collect all attribute names used in DMX modes, logical channels and functions."""
    if gdtf_profile is None:
        return []

    names: List[str] = []
    seen: set = set()
    for mode in getattr(gdtf_profile, "dmx_modes", []):
        for channel in getattr(mode, "_dmx_channels", []):
            for logical_channel in getattr(channel, "logical_channels", []):
                attr_link = getattr(logical_channel, "attribute", None)
                attr_name = getattr(attr_link, "str_link", None)
                if attr_name and attr_name not in seen:
                    names.append(attr_name)
                    seen.add(attr_name)
                for channel_function in getattr(
                    logical_channel, "channel_functions", []
                ):
                    cf_attr = getattr(channel_function, "attribute", None)
                    cf_name = getattr(cf_attr, "str_link", None)
                    if cf_name and cf_name not in seen:
                        names.append(cf_name)
                        seen.add(cf_name)
    return names


def _collect_custom_attributes(
    gdtf_profile: Optional["pygdtf.FixtureType"],
) -> Dict[str, "pygdtf.Attribute"]:
    """Map existing AttributeDefinitions by name for reuse (e.g., custom attributes)."""
    if gdtf_profile is None:
        return {}
    result: Dict[str, "pygdtf.Attribute"] = {}
    for attr in getattr(gdtf_profile, "attributes", []) or []:
        if getattr(attr, "name", None):
            result[attr.name] = copy.deepcopy(attr)
    return result


def _expand_attribute_dependencies(
    attr_names: List[str], templates: Dict[str, Any]
) -> List[str]:
    """Ensure main attributes referenced in templates are also included."""
    # We discover new dependencies while iterating, so we need a queue that can
    # grow during traversal (a fixed for-loop over the initial list would miss
    # newly enqueued main attributes).
    queue = deque(attr_names)
    seen = set(attr_names)
    ordered: List[str] = []

    while queue:
        current = queue.popleft()
        ordered.append(current)
        template, groups = _match_attribute_template(current, templates)
        if template and template.get("main_attribute"):
            main_attr = _apply_placeholders(template.get("main_attribute"), groups)
            if main_attr and main_attr not in seen:
                seen.add(main_attr)
                queue.append(main_attr)

    return ordered


def _build_fallback_attribute(
    name: str, features_by_group: Dict[str, set]
) -> "pygdtf.Attribute":
    """Create a minimal attribute when no Annex template is found."""
    features_by_group.setdefault("Control", set()).add("Control")
    return pygdtf.Attribute(
        name=name,
        pretty=name,
        feature=pygdtf.NodeLink("FeatureGroups", "Control.Control"),
        physical_unit=pygdtf.PhysicalUnit(None),
    )


def regenerate_attribute_definitions(
    gdtf_profile: Optional["pygdtf.FixtureType"],
):
    """
    Generate AttributeDefinitions based on DMX content and Annex B data.

    Returns a dict with activation_groups, feature_groups, attributes, and missing_attributes.
    """
    templates = _load_annex_attribute_templates()
    attr_names = _collect_attribute_names(gdtf_profile)
    attr_names = _expand_attribute_dependencies(attr_names, templates["attributes"])
    custom_attr_map = _collect_custom_attributes(gdtf_profile)

    attributes: List["pygdtf.Attribute"] = []
    used_activation_groups: set = set()
    features_by_group: Dict[str, set] = {}
    missing_attributes: List[str] = []

    for name in attr_names:
        template, groups = _match_attribute_template(name, templates["attributes"])
        if template is None:
            if name in custom_attr_map:
                attr = copy.deepcopy(custom_attr_map[name])
                # ensure linked groups/features are tracked
                if attr.activation_group and attr.activation_group.str_link:
                    used_activation_groups.add(str(attr.activation_group.str_link))
                if attr.feature and attr.feature.str_link:
                    feature_link_str = str(attr.feature.str_link)
                    if "." in feature_link_str:
                        group_name, feature_name = feature_link_str.split(".", 1)
                    else:
                        group_name, feature_name = feature_link_str, feature_link_str
                    features_by_group.setdefault(group_name, set()).add(feature_name)
            else:
                missing_attributes.append(name)
                attr = _build_fallback_attribute(name, features_by_group)
        else:
            activation_group = _apply_placeholders(
                template.get("activation_group"), groups
            )
            feature_link: Optional[str] = _apply_placeholders(
                template.get("feature"), groups
            )
            if activation_group:
                used_activation_groups.add(activation_group)
            if feature_link:
                if "." in feature_link:
                    group_name, feature_name = feature_link.split(".", 1)
                else:
                    group_name, feature_name = feature_link, feature_link
                features_by_group.setdefault(group_name, set()).add(feature_name)
            attr = _build_attribute_from_template(name, template, groups)
        attributes.append(attr)

    activation_group_objs = [
        pygdtf.ActivationGroup(name=ag)
        for ag in templates["activation_groups"]
        if ag in used_activation_groups
    ]
    # Append any custom activation groups that were not in Annex templates
    for ag in sorted(used_activation_groups):
        if ag not in templates["activation_groups"]:
            activation_group_objs.append(pygdtf.ActivationGroup(name=ag))

    feature_template_map = {
        fg["name"]: fg for fg in templates["feature_groups"] if fg.get("name")
    }
    feature_group_objs: List["pygdtf.FeatureGroup"] = []
    for group_name, feature_names in features_by_group.items():
        template = feature_template_map.get(group_name, {})
        ordered_features = [
            name for name in template.get("features", []) if name in feature_names
        ]
        trailing = [name for name in feature_names if name not in ordered_features]
        feature_group_objs.append(
            pygdtf.FeatureGroup(
                name=group_name,
                pretty=template.get("pretty") or group_name,
                features=[
                    pygdtf.Feature(name=feature_name)
                    for feature_name in ordered_features + trailing
                ],
            )
        )

    return {
        "activation_groups": activation_group_objs,
        "feature_groups": feature_group_objs,
        "attributes": attributes,
        "missing_attributes": missing_attributes,
    }
