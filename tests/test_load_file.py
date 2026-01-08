import json
from pathlib import Path

import pytest
import tomli_w
import yaml
from dotenv import dotenv_values

from mconf import load_file


@pytest.mark.parametrize(
    "extension,content,expected",
    [
        # JSON tests
        (".json", '{"key": "value", "number": 42}', {"key": "value", "number": 42}),
        (".json", '{"nested": {"data": [1, 2, 3]}}', {"nested": {"data": [1, 2, 3]}}),
        (".json", "[]", []),
        (".json", "null", None),
        (".json", "true", True),
        (".json", "123", 123),
        (".json", '"string"', "string"),
        # YAML tests with .yaml extension
        (".yaml", "key: value\nnumber: 42", {"key": "value", "number": 42}),
        (".yaml", "nested:\n  data:\n    - 1\n    - 2\n    - 3", {"nested": {"data": [1, 2, 3]}}),
        (".yaml", "- item1\n- item2\n- item3", ["item1", "item2", "item3"]),
        (".yaml", "null", None),
        (".yaml", "true", True),
        (".yaml", "123", 123),
        (".yaml", "string", "string"),
        # YAML tests with .yml extension
        (".yml", "key: value\nnumber: 42", {"key": "value", "number": 42}),
        (".yml", "nested:\n  data:\n    - 1\n    - 2\n    - 3", {"nested": {"data": [1, 2, 3]}}),
        # TOML tests
        (".toml", 'key = "value"\nnumber = 42', {"key": "value", "number": 42}),
        (".toml", '[nested]\ndata = [1, 2, 3]', {"nested": {"data": [1, 2, 3]}}),
        # ENV tests
        (".env", "KEY=value\nNUMBER=42", {"KEY": "value", "NUMBER": "42"}),
        (".env", "EMPTY=\nSPACES=value with spaces", {"EMPTY": "", "SPACES": "value with spaces"}),
        (".env", "", {}),
    ],
)
def test_load_file_success(tmp_path, extension, content, expected):
    """Test loading files with various formats and content."""
    file_path = tmp_path / f"config{extension}"
    
    # Write content based on file type
    if extension == ".toml":
        file_path.write_bytes(content.encode("utf-8"))
    else:
        file_path.write_text(content, encoding="utf-8")
    
    result = load_file(file_path)
    assert result == expected


@pytest.mark.parametrize(
    "extension,content,expected",
    [
        # Empty files
        (".json", "", None),  # Will raise error
        (".yaml", "", None),
        (".yml", "", None),
        (".toml", "", {}),  # Returns empty dict
    ],
)
def test_load_file_empty_content(tmp_path, extension, content, expected):
    """Test loading empty or whitespace-only files."""
    file_path = tmp_path / f"config{extension}"
    file_path.write_text(content, encoding="utf-8")
    
    # Empty files should either return None/empty dict or raise an error depending on the format
    if extension in [".yaml", ".yml"]:
        # YAML returns None for empty content
        result = load_file(file_path)
        assert result is None
    elif extension == ".toml":
        # TOML returns empty dict for empty content
        result = load_file(file_path)
        assert result == {}
    else:
        # JSON should raise errors
        with pytest.raises(Exception):
            load_file(file_path)


@pytest.mark.parametrize(
    "extension,content",
    [
        (".json", "invalid json {"),
        (".json", '{"unclosed": '),
        (".yaml", "invalid: yaml: [unclosed"),
        (".toml", "invalid toml [unclosed"),
        (".toml", "= value"),
    ],
)
def test_load_file_invalid_content(tmp_path, extension, content):
    """Test loading files with invalid content."""
    file_path = tmp_path / f"config{extension}"
    
    if extension == ".toml":
        file_path.write_bytes(content.encode("utf-8"))
    else:
        file_path.write_text(content, encoding="utf-8")
    
    with pytest.raises(Exception):
        load_file(file_path)


@pytest.mark.parametrize(
    "extension",
    [
        ".txt",
        ".xml",
        ".ini",
        ".cfg",
        ".py",
        ".unknown",
        "",
    ],
)
def test_load_file_unsupported_format(tmp_path, extension):
    """Test loading files with unsupported formats."""
    file_path = tmp_path / f"config{extension}"
    file_path.write_text("some content", encoding="utf-8")
    
    with pytest.raises(ValueError, match="Unsupported file format"):
        load_file(file_path)


def test_load_file_nonexistent(tmp_path):
    """Test loading a file that doesn't exist."""
    file_path = tmp_path / "nonexistent.json"
    
    with pytest.raises(FileNotFoundError):
        load_file(file_path)


@pytest.mark.parametrize(
    "extension,data",
    [
        (".json", {"unicode": "Hello 世界 🌍", "special": "Ñoño"}),
        (".yaml", {"unicode": "Hello 世界 🌍", "special": "Ñoño"}),
        (".toml", {"unicode": "Hello 世界 🌍", "special": "Ñoño"}),
        (".env", {"UNICODE": "Hello_世界_🌍", "SPECIAL": "Noño"}),
    ],
)
def test_load_file_unicode(tmp_path, extension, data):
    """Test loading files with unicode content."""
    file_path = tmp_path / f"config{extension}"
    
    # Write the file based on format
    if extension == ".json":
        file_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    elif extension in [".yaml", ".yml"]:
        file_path.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
    elif extension == ".toml":
        file_path.write_bytes(tomli_w.dumps(data).encode("utf-8"))
    elif extension == ".env":
        content = "\n".join(f"{k}={v}" for k, v in data.items())
        file_path.write_text(content, encoding="utf-8")
    
    result = load_file(file_path)
    assert result == data


@pytest.mark.parametrize(
    "extension,data",
    [
        (".json", {"list": [1, 2, 3], "dict": {"nested": "value"}, "bool": True, "null": None}),
        (".yaml", {"list": [1, 2, 3], "dict": {"nested": "value"}, "bool": True, "null": None}),
        (".toml", {"list": [1, 2, 3], "dict": {"nested": "value"}, "bool": True}),
    ],
)
def test_load_file_complex_data(tmp_path, extension, data):
    """Test loading files with complex nested data structures."""
    file_path = tmp_path / f"config{extension}"
    
    if extension == ".json":
        file_path.write_text(json.dumps(data), encoding="utf-8")
    elif extension in [".yaml", ".yml"]:
        file_path.write_text(yaml.dump(data), encoding="utf-8")
    elif extension == ".toml":
        file_path.write_bytes(tomli_w.dumps(data).encode("utf-8"))
    
    result = load_file(file_path)
    assert result == data


def test_load_file_case_insensitive_extension(tmp_path):
    """Test that file extensions are case-insensitive."""
    test_cases = [
        (".JSON", '{"key": "value"}', {"key": "value"}),
        (".YAML", "key: value", {"key": "value"}),
        (".YML", "key: value", {"key": "value"}),
        (".TOML", 'key = "value"', {"key": "value"}),
        (".ENV", "KEY=value", {"KEY": "value"}),
    ]
    
    for extension, content, expected in test_cases:
        file_path = tmp_path / f"config{extension}"
        if extension == ".TOML":
            file_path.write_bytes(content.encode("utf-8"))
        else:
            file_path.write_text(content, encoding="utf-8")
        
        result = load_file(file_path)
        assert result == expected


@pytest.mark.parametrize(
    "extension,special_values",
    [
        (".yaml", {"infinity": float('inf'), "neg_infinity": float('-inf')}),
        (".yaml", {"scientific": 1.23e-4, "negative": -42}),
    ],
)
def test_load_file_special_yaml_values(tmp_path, extension, special_values):
    """Test loading YAML files with special numeric values."""
    file_path = tmp_path / f"config{extension}"
    file_path.write_text(yaml.dump(special_values), encoding="utf-8")
    
    result = load_file(file_path)
    assert result == special_values


def test_load_file_env_with_comments_and_quotes(tmp_path):
    """Test loading .env files with comments, quotes, and special cases."""
    file_path = tmp_path / "config.env"
    content = """# Comment
KEY1=value1
KEY2="quoted value"
KEY3='single quoted'
# Another comment
KEY4=value with spaces
EMPTY=
"""
    file_path.write_text(content, encoding="utf-8")
    
    result = load_file(file_path)
    # dotenv_values handles comments and quotes
    assert "KEY1" in result
    assert result["KEY1"] == "value1"


def test_load_file_path_object(tmp_path):
    """Test that load_file works with Path objects."""
    file_path = tmp_path / "config.json"
    data = {"key": "value"}
    file_path.write_text(json.dumps(data), encoding="utf-8")
    
    # Ensure file_path is a Path object
    assert isinstance(file_path, Path)
    
    result = load_file(file_path)
    assert result == data
