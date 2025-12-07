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

from pathlib import Path
import pytest
import zipfile
import os
from xml.etree import ElementTree

import pygdtf


def _elements_equal(a, b, path: str = ""):
    """Return (equal, message) to surface the first difference."""
    current_path = f"{path}/{a.tag}" if path else a.tag
    if a.tag != b.tag:
        return False, f"Tag mismatch at {current_path}: {a.tag} != {b.tag}"
    text_a, text_b = (a.text or "").strip(), (b.text or "").strip()
    if text_a != text_b:
        return False, f"Text mismatch at {current_path}: '{text_a}' != '{text_b}'"
    tail_a, tail_b = (a.tail or "").strip(), (b.tail or "").strip()
    if tail_a != tail_b:
        return False, f"Tail mismatch at {current_path}: '{tail_a}' != '{tail_b}'"
    if a.attrib != b.attrib:
        # dict equality ignores order; diff tells you what changed
        missing = a.attrib.items() - b.attrib.items()
        extra = b.attrib.items() - a.attrib.items()
        detail = []
        if missing:
            detail.append(f"only in expected: {dict(missing)}")
        if extra:
            detail.append(f"only in actual: {dict(extra)}")
        return False, f"Attributes differ at {current_path} ({'; '.join(detail)})"
    if len(a) != len(b):
        return (
            False,
            f"Children count mismatch at {current_path}: {len(a)} != {len(b)}",
        )
    for idx, (c1, c2) in enumerate(zip(a, b)):
        equal, message = _elements_equal(c1, c2, path=f"{current_path}[{idx}]")
        if not equal:
            return equal, message
    return True, ""


def test_writer_roundtrip(tmp_path: Path, gdtf_fixture):
    writer = pygdtf.FixtureTypeWriter(gdtf_fixture)
    output = tmp_path / "roundtrip.gdtf"

    writer.write_gdtf(output)

    assert output.exists()

    # Avoid Python 3.10+ only parenthesized context manager syntax
    with zipfile.ZipFile(gdtf_fixture.path, "r") as original, zipfile.ZipFile(
        output, "r"
    ) as rewritten:
        assert sorted(original.namelist()) == sorted(rewritten.namelist())
        original_root = ElementTree.fromstring(original.read("description.xml"))
        rewritten_root = ElementTree.fromstring(rewritten.read("description.xml"))
        equal, message = _elements_equal(original_root, rewritten_root)
        assert equal, message


def test_writer_can_override_data_version(tmp_path: Path, gdtf_fixture):
    writer = pygdtf.FixtureTypeWriter(gdtf_fixture)
    output = tmp_path / "override_version.gdtf"
    writer.write_gdtf(output, data_version="9.9")

    with zipfile.ZipFile(output, "r") as rewritten:
        rewritten_root = ElementTree.fromstring(rewritten.read("description.xml"))
        assert rewritten_root.get("DataVersion") == "9.9"


def test_writer_serializes_channel_set_changes(tmp_path: Path, gdtf_fixture):
    first_mode = gdtf_fixture.dmx_modes[0]
    first_channel = first_mode._dmx_channels[0]
    first_function = first_channel.logical_channels[0].channel_functions[0]
    first_function.channel_sets[0].name = "Modified"

    writer = pygdtf.FixtureTypeWriter(gdtf_fixture)
    output = tmp_path / "mutated.gdtf"
    writer.write_gdtf(output)

    with zipfile.ZipFile(output, "r") as rewritten:
        root = ElementTree.fromstring(rewritten.read("description.xml"))
        cs = root.find(
            "./FixtureType/DMXModes/DMXMode/DMXChannels/DMXChannel/LogicalChannel/ChannelFunction/ChannelSet"
        )
        assert cs is not None
        assert cs.attrib.get("Name") == "Modified"


def test_writer_with_file(tmp_path: Path, request, pygdtf_module):
    # uv run pytest --file-path=../../gdtfs/ -s
    file_path = request.config.getoption("--file-path")

    if file_path is None:
        pytest.skip("File path not provided")
    print("aaa", file_path)
    path = Path(file_path)
    files = list(path.glob("*.gdtf"))
    sorted_files = sorted(files, key=os.path.getmtime, reverse=True)

    if not sorted_files:
        pytest.skip(f"No files found in {file_path} matching the pattern")

    for file in sorted_files:
        print(file)
        with pygdtf_module.FixtureType(file) as fixture:
            writer = pygdtf.FixtureTypeWriter(fixture)
            output = tmp_path / f"{file.stem}_roundtrip.gdtf"
            writer.write_gdtf(output)
            output.unlink()
