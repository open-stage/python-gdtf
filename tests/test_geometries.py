# MIT License
#
# Copyright (C) 2026 vanous
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

from pathlib import Path


def _find_geometry(geometry, name):
    if geometry is None:
        return None
    if geometry.name == name:
        return geometry
    for child in getattr(geometry, "geometries", []):
        found = _find_geometry(child, name)
        if found is not None:
            return found
    return None


def test_get_geometry_tree_expands_references(pygdtf_module):
    root = pygdtf_module.Geometry(name="Root")
    referenced_child = pygdtf_module.Geometry(name="RefChild")
    referenced = pygdtf_module.Geometry(
        name="Referenced",
        geometries=pygdtf_module.Geometries([referenced_child]),
    )
    root.geometries = pygdtf_module.Geometries(
        [pygdtf_module.GeometryReference(name="Ref", geometry="Referenced")]
    )

    geometries = pygdtf_module.Geometries([root, referenced])
    fixture_type = type("Fixture", (), {})()
    fixture_type.geometries = geometries
    fixture_type.dmx_modes = pygdtf_module.DmxModes(
        [pygdtf_module.DmxMode(name="Default", geometry="Root")]
    )

    tree = geometries.get_geometry_tree(fixture_type)

    assert tree.name == "Root"
    assert [child.name for child in tree.geometries] == ["Ref"]
    assert [child.name for child in tree.geometries[0].geometries] == ["RefChild"]


def test_get_geometry_tree_expands_references_from_files(pygdtf_module):
    test_fixture_test_file = Path(Path(__file__).parents[0], "test2.xml").as_posix()
    fixture = pygdtf_module.FixtureType(dsc_file=test_fixture_test_file)
    tree = fixture.geometries.get_geometry_tree(fixture, mode_name="Mode 1 - Wash")

    pixel = _find_geometry(tree, "Pixel 1")

    assert pixel is not None
    assert isinstance(pixel, pygdtf_module.GeometryReference)
    assert [child.name for child in pixel.geometries] == ["Patt cross 1"]


def test_as_dict_uses_mode_name_for_root(pygdtf_module):
    root = pygdtf_module.Geometry(name="Root")
    referenced_child = pygdtf_module.Geometry(name="RefChild")
    referenced = pygdtf_module.Geometry(
        name="Referenced",
        geometries=pygdtf_module.Geometries([referenced_child]),
    )
    root.geometries = pygdtf_module.Geometries(
        [pygdtf_module.GeometryReference(name="Ref", geometry="Referenced")]
    )

    geometries = pygdtf_module.Geometries([root, referenced])
    fixture_type = type("Fixture", (), {})()
    fixture_type.geometries = geometries
    fixture_type.dmx_modes = pygdtf_module.DmxModes(
        [pygdtf_module.DmxMode(name="Default", geometry="Root")]
    )

    tree = geometries.as_dict(None, fixture_type, mode_name="Default")

    assert tree["name"] == "Root"
    assert [child["name"] for child in tree["children"]] == ["Ref"]
    assert [child["name"] for child in tree["children"][0]["children"]] == ["RefChild"]
