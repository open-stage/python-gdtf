import pygdtf


def test_dmx_value_full_and_bytes():
    value = pygdtf.DmxValue("16909060/4")  # 0x01_02_03_04
    assert value.get_value(full=True) == 16909060
    assert value.get_value() == 1
    assert value.get_value(fine=True) == 4
    assert value.get_value(components=True) == [1, 2, 3, 4]
    assert value.get_value(byte_index=1) == 2
    assert value.get_value(byte_index=2) == 3
    assert value.get_value(byte_index=3) == 4


def test_channel_function_as_dict_full_values():
    channel_function = pygdtf.ChannelFunction(
        name="Test",
        attribute=pygdtf.NodeLink("Attributes", "Dimmer"),
        dmx_from=pygdtf.DmxValue("16909060/4"),
        dmx_to=pygdtf.DmxValue("16909061/4"),
        default=pygdtf.DmxValue("16909062/4"),
    )
    result = channel_function.as_dict()
    assert result["dmx_from"] == 16909060
    assert result["dmx_to"] == 16909061
    assert result["default"] == 16909062


def test_dmx_channel_as_dict_byte_defaults():
    channel = pygdtf.DmxChannel(
        offset=[1, 2, 3, 4],
        default=pygdtf.DmxValue("16909060/4"),
        highlight=pygdtf.DmxValue("84281096/4"),  # 0x05_06_07_08
        attribute=pygdtf.NodeLink("Attributes", "Dimmer"),
        logical_channels=[
            pygdtf.LogicalChannel(attribute=pygdtf.NodeLink("Attributes", "Dimmer"))
        ],
    )
    result = channel.as_dict()
    assert [entry["default"] for entry in result] == [
        16909060,
        16909060,
        16909060,
        16909060,
    ]
    assert result[0]["highlight"] == 84281096
