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
