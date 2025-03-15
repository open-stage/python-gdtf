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

        modes_info = []

        for idx, mode in enumerate(fixture.dmx_modes):
            dmx_mode_info = {
                "mode_id": idx,
                "mode_name": mode.name,
                "mode_dmx_channel_count": mode.dmx_channels_count,
                "mode_virtual_channel_count": mode.virtual_channels_count,
                "mode_dmx_breaks_count": mode.dmx_breaks_count,
                "mode_dmx_channels": mode.dmx_channels.as_dicts(),
                "mode_virtual_channels": mode.virtual_channels.as_dicts(),
            }
            modes_info.append(dmx_mode_info)
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
