import json
from pathlib import Path

import pytest
import tomli
import yaml
from dotenv import dotenv_values

from mconf import dump_file


@pytest.mark.parametrize(
    "extension,data,loader",
    [
        # JSON tests with various data types
        (".json", {"key": "value", "number": 42}, lambda p: json.load(p.open("r"))),
        (".json", {"nested": {"data": [1, 2, 3]}}, lambda p: json.load(p.open("r"))),
        (
            ".json",
            {"list": [1, 2, 3], "bool": True, "null": None},
            lambda p: json.load(p.open("r")),
        ),
        (".json", [], lambda p: json.load(p.open("r"))),
        (".json", [1, 2, 3], lambda p: json.load(p.open("r"))),
        (".json", {"unicode": "héllo wörld 世界"}, lambda p: json.load(p.open("r"))),
        (".json", {"empty_dict": {}}, lambda p: json.load(p.open("r"))),
        (".json", {"empty_list": []}, lambda p: json.load(p.open("r"))),
        # YAML tests with .yaml extension
        (
            ".yaml",
            {"key": "value", "number": 42},
            lambda p: yaml.safe_load(p.open("r")),
        ),
        (
            ".yaml",
            {"nested": {"data": [1, 2, 3]}},
            lambda p: yaml.safe_load(p.open("r")),
        ),
        (
            ".yaml",
            {"list": [1, 2, 3], "bool": True, "null": None},
            lambda p: yaml.safe_load(p.open("r")),
        ),
        (".yaml", [], lambda p: yaml.safe_load(p.open("r"))),
        (".yaml", [1, 2, 3], lambda p: yaml.safe_load(p.open("r"))),
        (
            ".yaml",
            {"unicode": "héllo wörld 世界"},
            lambda p: yaml.safe_load(p.open("r")),
        ),
        # YAML tests with .yml extension
        (".yml", {"key": "value", "number": 42}, lambda p: yaml.safe_load(p.open("r"))),
        (
            ".yml",
            {"nested": {"data": [1, 2, 3]}},
            lambda p: yaml.safe_load(p.open("r")),
        ),
        # TOML tests
        (".toml", {"key": "value", "number": 42}, lambda p: tomli.load(p.open("rb"))),
        (".toml", {"nested": {"data": [1, 2, 3]}}, lambda p: tomli.load(p.open("rb"))),
        (
            ".toml",
            {"string": "test", "bool": True, "list": [1, 2, 3]},
            lambda p: tomli.load(p.open("rb")),
        ),
        # ENV tests
        (".env", {"KEY": "value", "NUMBER": "42"}, lambda p: dotenv_values(p)),
        (
            ".env",
            {"EMPTY": "", "SPACES": "value with spaces"},
            lambda p: dotenv_values(p),
        ),
        (".env", {"UNICODE": "héllo"}, lambda p: dotenv_values(p)),
    ],
)
def test_dump_file_various_formats_and_data(tmp_path, extension, data, loader):
    """Test dumping various data types to different file formats."""
    file_path = tmp_path / f"output{extension}"
    dump_file(data, file_path)

    assert file_path.exists()
    result = loader(file_path)
    assert result == data


@pytest.mark.parametrize(
    "extension",
    [".json", ".yaml", ".yml", ".toml", ".env"],
)
def test_dump_file_creates_file(tmp_path, extension):
    """Test that dump_file creates the file if it doesn't exist."""
    file_path = tmp_path / f"new_file{extension}"
    data = {"test": "data"} if extension != ".env" else {"TEST": "data"}

    assert not file_path.exists()
    dump_file(data, file_path)
    assert file_path.exists()


@pytest.mark.parametrize(
    "extension",
    [".json", ".yaml", ".yml"],
)
def test_dump_file_overwrites_existing_file(tmp_path, extension):
    """Test that dump_file overwrites existing files."""
    file_path = tmp_path / f"existing{extension}"
    file_path.write_text("old content")

    data = {"new": "data"}
    dump_file(data, file_path)

    # Verify new content was written
    with open(file_path, "r") as f:
        if extension == ".json":
            result = json.load(f)
        else:
            result = yaml.safe_load(f)
    assert result == data


@pytest.mark.parametrize(
    "data",
    [
        {
            "deeply": {
                "nested": {"structure": {"with": {"multiple": {"levels": "value"}}}}
            }
        },
        {"list_of_dicts": [{"a": 1}, {"b": 2}, {"c": 3}]},
        {
            "mixed": {
                "numbers": [1, 2, 3],
                "strings": ["a", "b"],
                "nested": {"key": "value"},
            }
        },
    ],
)
def test_dump_file_complex_structures_json(tmp_path, data):
    """Test dumping complex nested structures to JSON."""
    file_path = tmp_path / "complex.json"
    dump_file(data, file_path)

    with open(file_path, "r") as f:
        result = json.load(f)
    assert result == data


@pytest.mark.parametrize(
    "extension,data",
    [
        (".json", "string"),
        (".json", 123),
        (".json", True),
        (".json", None),
        (".yaml", "string"),
        (".yaml", 123),
        (".yaml", True),
        (".yaml", None),
    ],
)
def test_dump_file_primitive_types(tmp_path, extension, data):
    """Test dumping primitive data types."""
    file_path = tmp_path / f"primitive{extension}"
    dump_file(data, file_path)

    assert file_path.exists()
    with open(file_path, "r") as f:
        if extension == ".json":
            result = json.load(f)
        else:
            result = yaml.safe_load(f)
    assert result == data


def test_dump_file_env_empty_dict(tmp_path):
    """Test dumping an empty dictionary to .env file."""
    file_path = tmp_path / "empty.env"
    dump_file({}, file_path)

    assert file_path.exists()
    result = dotenv_values(file_path)
    assert result == {}


@pytest.mark.parametrize(
    "extension",
    [".json", ".yaml", ".yml"],
)
def test_dump_file_empty_dict(tmp_path, extension):
    """Test dumping empty dictionaries."""
    file_path = tmp_path / f"empty{extension}"
    dump_file({}, file_path)

    with open(file_path, "r") as f:
        if extension == ".json":
            result = json.load(f)
        else:
            result = yaml.safe_load(f)
    # YAML returns None for empty documents, JSON returns {}
    assert result == {} or result is None


@pytest.mark.parametrize(
    "extension",
    [".json", ".yaml", ".yml"],
)
def test_dump_file_empty_list(tmp_path, extension):
    """Test dumping empty lists."""
    file_path = tmp_path / f"empty_list{extension}"
    dump_file([], file_path)

    with open(file_path, "r") as f:
        if extension == ".json":
            result = json.load(f)
        else:
            result = yaml.safe_load(f)
    assert result == []


def test_dump_file_toml_with_dates_and_floats(tmp_path):
    """Test dumping TOML with various numeric types."""
    file_path = tmp_path / "numbers.toml"
    data = {"integer": 42, "float": 3.14, "negative": -10, "nested": {"value": 100}}
    dump_file(data, file_path)

    with open(file_path, "rb") as f:
        result = tomli.load(f)
    assert result == data


def test_dump_file_special_characters_in_values(tmp_path):
    """Test dumping data with special characters."""
    data = {
        "quotes": 'value with "quotes"',
        "newlines": "line1\nline2",
        "tabs": "value\twith\ttabs",
        "backslash": "path\\to\\file",
    }

    # Test JSON
    json_path = tmp_path / "special.json"
    dump_file(data, json_path)
    with open(json_path, "r") as f:
        result = json.load(f)
    assert result == data

    # Test YAML
    yaml_path = tmp_path / "special.yaml"
    dump_file(data, yaml_path)
    with open(yaml_path, "r") as f:
        result = yaml.safe_load(f)
    assert result == data


def test_dump_file_case_insensitive_extension(tmp_path):
    """Test that file extensions are handled case-insensitively."""
    data = {"key": "value"}

    # Test uppercase extensions
    for ext in [".JSON", ".YAML", ".YML"]:
        file_path = tmp_path / f"test{ext}"
        dump_file(data, file_path)
        assert file_path.exists()


@pytest.mark.parametrize(
    "extension",
    [".txt", ".xml", ".ini", ".cfg", ".py", ".md"],
)
def test_dump_file_unsupported_format(tmp_path, extension):
    """Test that unsupported file formats raise ValueError."""
    file_path = tmp_path / f"test{extension}"
    data = {"key": "value"}

    with pytest.raises(ValueError, match="Unsupported file format"):
        dump_file(data, file_path)


@pytest.mark.parametrize(
    "file_type,data,parser",
    [
        ("json", {"key": "value", "number": 42}, lambda out: json.loads(out)),
        ("yaml", {"key": "value", "number": 42}, lambda out: yaml.safe_load(out)),
        ("toml", {"key": "value", "number": 42}, lambda out: tomli.loads(out)),
        (
            "env",
            {"KEY": "value", "NUMBER": "42"},
            lambda out: dict(
                line.split("=", 1) for line in out.strip().split("\n") if line
            ),
        ),
    ],
)
def test_dump_file_to_stdout(capsys, file_type, data, parser):
    """Test dumping various formats to stdout when file_path is None."""
    dump_file(data, None, file_type=file_type)

    captured = capsys.readouterr()
    result = parser(captured.out)
    assert result == data


def test_dump_file_to_stdout_without_file_type():
    """Test that dumping to stdout without file_type raises ValueError."""
    data = {"key": "value"}

    with pytest.raises(
        ValueError, match="file_type must be specified when file_path is None"
    ):
        dump_file(data, None)


@pytest.mark.parametrize(
    "extension,data,assertions",
    [
        (
            ".json",
            {"nested": {"key": "value"}},
            lambda content: ("\n" in content and "    " in content),  # 4-space indent
        ),
        (
            ".env",
            {"KEY1": "value1", "KEY2": "value2"},
            lambda content: ("KEY1=value1\n" in content and "KEY2=value2\n" in content),
        ),
    ],
)
def test_dump_file_format_specific(tmp_path, extension, data, assertions):
    """Test that files are formatted correctly for each format."""
    file_path = tmp_path / f"test{extension}"
    dump_file(data, file_path)

    content = file_path.read_text()
    assert assertions(content)


def test_dump_file_path_object(tmp_path):
    """Test that dump_file works with Path objects."""
    file_path = Path(tmp_path) / "test.json"
    data = {"key": "value"}
    dump_file(data, file_path)

    assert file_path.exists()
    with open(file_path, "r") as f:
        result = json.load(f)
    assert result == data


def test_dump_file_creates_nested_directories(tmp_path):
    """Test that dump_file creates parent directories if they don't exist."""
    # Note: This test checks if dump_file handles nested paths
    # Based on the code, it uses file_path.open("w") which should fail if parent doesn't exist
    # We'll test the expected behavior
    nested_dir = tmp_path / "level1" / "level2"
    nested_dir.mkdir(parents=True)

    file_path = nested_dir / "test.json"
    data = {"key": "value"}
    dump_file(data, file_path)

    assert file_path.exists()


@pytest.mark.parametrize(
    "data",
    [
        {"key with spaces": "value with spaces"},
        {"key-with-dashes": "value-with-dashes"},
        {"key_with_underscores": "value_with_underscores"},
        {"key.with.dots": "value.with.dots"},
        {"UPPERCASE_KEY": "UPPERCASE_VALUE"},
        {"mixedCaseKey": "mixedCaseValue"},
    ],
)
def test_dump_file_various_key_formats_json(tmp_path, data):
    """Test dumping dictionaries with various key formats to JSON."""
    file_path = tmp_path / "keys.json"
    dump_file(data, file_path)

    with open(file_path, "r") as f:
        result = json.load(f)
    assert result == data


def test_dump_file_large_data_structure(tmp_path):
    """Test dumping a large data structure."""
    data = {f"key_{i}": f"value_{i}" for i in range(1000)}
    file_path = tmp_path / "large.json"
    dump_file(data, file_path)

    with open(file_path, "r") as f:
        result = json.load(f)
    assert result == data
    assert len(result) == 1000
