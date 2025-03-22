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


def test_version(gdtf_fixture):
    """GDTF version should be 1.2"""

    assert gdtf_fixture.data_version == "1.2"


def test_name(gdtf_fixture):
    """Name of the fixture should be as defined"""

    assert gdtf_fixture.name == "LED PAR 64 RGBW"


def test_dmx_channel_count(gdtf_fixture, pygdtf_module):
    """DMX mode name should be Default, channel count should be 5"""

    for mode in gdtf_fixture.dmx_modes:
        assert mode.name == "Default"
        assert mode.dmx_channels_count == 5
