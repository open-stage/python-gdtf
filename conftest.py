# MIT License
#
# Copyright (C) 2023 vanous
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


def pytest_configure(config):
    plugin = config.pluginmanager.getplugin("mypy")
    #    plugin.mypy_argv.append("--no-strict-optional")
