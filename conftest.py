import os
from pathlib import Path
import pytest
from pygdtf import pygdtf

# This file sets up a pytest fixtures for the tests
# It is important that this file stays in this location
# as this makes pytest to load pygdtf from the pygdtf directory

@pytest.fixture(scope="session")
def gdtf_fixture():
    test_fixture_file_path = Path(
        Path(__file__).parents[0], "tests", "BlenderDMX@LED_PAR_64_RGBW@v0.3.gdtf"
    )  # test file path is made from current directory, tests directory and a file name
    gdtf_fixture = pygdtf.FixtureType(test_fixture_file_path)
    yield gdtf_fixture


@pytest.fixture(scope="session")
def pygdtf_module():
    yield pygdtf
