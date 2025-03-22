# MIT License
#
# Copyright (C) 2024 vanous
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
from pathlib import Path


def test_modes_channels_count(pygdtf_module):
    """Test channel count for complex devices with GeometryReferences"""

    test_files = ["test1", "test2"]

    for test_file in test_files:
        test_fixture_test_file = Path(
            Path(__file__).parents[0], f"{test_file}.xml"
        ).as_posix()
        test_fixture_result_file = Path(Path(__file__).parents[0], f"{test_file}.json")
        with open(test_fixture_result_file) as f:
            test_result = json.load(f)
        fixture = pygdtf_module.FixtureType(dsc_file=test_fixture_test_file)

        modes_info = fixture.dmx_modes.as_dict()
        print("fixture", fixture.name)
        for mode in modes_info:
            print(mode["name"], mode["dmx_channels_count"])

        # This is here to capture test data next time if needed
        # with open(f"tests/{test_file}.json", "w") as f:
        #    json.dump(modes_info, f)
        assert modes_info == test_result


def test_get_geometries(pygdtf_module):
    """Test get geometries with GeometryReferences"""

    tests = [
        (
            "test1",
            [
                "GeometryBeam",
                "GeometryWiringObject",
                "GeometryAxis",
                "Geometry",
                "GeometryReference",
            ],
        ),
        (
            "test2",
            ["GeometryWiringObject", "GeometryBeam", "Geometry", "GeometryReference"],
        ),
    ]

    for test in tests:
        test_file = test[0]
        test_result = test[1]
        test_fixture_test_file = Path(
            Path(__file__).parents[0], f"{test_file}.xml"
        ).as_posix()
        fixture = pygdtf_module.FixtureType(dsc_file=test_fixture_test_file)
        geometries = pygdtf_module.utils.get_used_geometries(fixture)
        assert set(test_result) == set(geometries)


def test_calculate_complexity_total(pygdtf_module, gdtf_fixture):
    """Test calculation"""
    complexity = pygdtf_module.utils.calculate_complexity(gdtf_fixture)
    print(complexity)
    assert 119 == complexity["total"]
