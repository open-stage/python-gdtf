from pathlib import Path
import json


def test_modes_channels_count(pygdtf_module):
    """Test channel count for complex devices with GeometryReferences"""

    test_files = ["test1", "test2"]

    for test_file in test_files:
        test_fixture_test_file = Path(Path(__file__).parents[0], f"{test_file}.xml")
        test_fixture_result_file = Path(Path(__file__).parents[0], f"{test_file}.json")
        with open(test_fixture_result_file) as f:
            test_result = json.load(f)
        fixture = pygdtf_module.FixtureType(dsc_file=test_fixture_test_file)
        modes_info = pygdtf_module.utils.get_dmx_modes_info(
            fixture, include_channels=False, include_channel_functions=False
        )
        assert modes_info == test_result
