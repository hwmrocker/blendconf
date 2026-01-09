import copy

import pytest

from blendconf import MergeStrategy, dict_merger


@pytest.mark.parametrize(
    "original,new,merge_strategy,expected",
    [
        # Basic dictionary merging with nested dicts
        (
            {"a": 1, "b": {"c": 2}},
            {"b": {"d": 3}, "e": 4},
            MergeStrategy.REPLACE,
            {"a": 1, "b": {"c": 2, "d": 3}, "e": 4},
        ),
        (
            {"a": 1, "b": {"c": 2}},
            {"b": {"d": 3}, "e": 4},
            MergeStrategy.APPEND,
            {"a": 1, "b": {"c": 2, "d": 3}, "e": 4},
        ),
        (
            {"a": 1, "b": {"c": 2}},
            {"b": {"d": 3}, "e": 4},
            MergeStrategy.PREPEND,
            {"a": 1, "b": {"c": 2, "d": 3}, "e": 4},
        ),
    ],
)
def test_dict_merger_strategies(original, new, merge_strategy, expected):
    """Test dict merging with different strategies."""
    original_copy = copy.deepcopy(original)
    result = dict_merger(original_copy, new, merge_strategy)
    assert result == expected


@pytest.mark.parametrize(
    "original,new,expected",
    [
        # Empty dicts
        ({}, {}, {}),
        ({}, {"a": 1, "b": 2}, {"a": 1, "b": 2}),
        ({"a": 1, "b": 2}, {}, {"a": 1, "b": 2}),
        # Simple merge
        ({"a": 1}, {"b": 2}, {"a": 1, "b": 2}),
        # Overwrite simple value
        ({"a": 1}, {"a": 2}, {"a": 2}),
    ],
)
def test_dict_merger_basic(original, new, expected):
    """Test basic dictionary merging scenarios."""
    result = dict_merger(original, new)
    assert result == expected


@pytest.mark.parametrize(
    "original,new,expected",
    [
        # Nested dict merge
        (
            {"a": {"b": 1, "c": 2}},
            {"a": {"c": 3, "d": 4}},
            {"a": {"b": 1, "c": 3, "d": 4}},
        ),
        # Deeply nested dict merge
        (
            {"a": {"b": {"c": {"d": 1}}}},
            {"a": {"b": {"c": {"e": 2}}}},
            {"a": {"b": {"c": {"d": 1, "e": 2}}}},
        ),
        # Nested dict to simple value
        ({"a": {"b": 1}}, {"a": 5}, {"a": 5}),
        # Simple value to nested dict
        ({"a": 5}, {"a": {"b": 1}}, {"a": {"b": 1}}),
        # Very deep nesting
        (
            {"a": {"b": {"c": {"d": {"e": {"f": 1}}}}}},
            {"a": {"b": {"c": {"d": {"e": {"g": 2}}}}}},
            {"a": {"b": {"c": {"d": {"e": {"f": 1, "g": 2}}}}}},
        ),
    ],
)
def test_dict_merger_nested(original, new, expected):
    """Test nested dictionary merging."""
    result = dict_merger(original, new)
    assert result == expected


@pytest.mark.parametrize(
    "original,new,merge_strategy,expected",
    [
        # List merge with REPLACE
        (
            {"items": [1, 2, 3]},
            {"items": [4, 5]},
            MergeStrategy.REPLACE,
            {"items": [4, 5]},
        ),
        # List merge with APPEND
        (
            {"items": [1, 2, 3]},
            {"items": [4, 5]},
            MergeStrategy.APPEND,
            {"items": [1, 2, 3, 4, 5]},
        ),
        # List merge with PREPEND
        (
            {"items": [1, 2, 3]},
            {"items": [4, 5]},
            MergeStrategy.PREPEND,
            {"items": [4, 5, 1, 2, 3]},
        ),
        # Nested dict with lists
        (
            {"config": {"ports": [8080, 8081]}},
            {"config": {"ports": [9000]}},
            MergeStrategy.APPEND,
            {"config": {"ports": [8080, 8081, 9000]}},
        ),
        # List to non-list
        (
            {"items": [1, 2, 3]},
            {"items": "single"},
            MergeStrategy.REPLACE,
            {"items": "single"},
        ),
        # Non-list to list
        (
            {"items": "single"},
            {"items": [1, 2, 3]},
            MergeStrategy.REPLACE,
            {"items": [1, 2, 3]},
        ),
    ],
)
def test_dict_merger_with_lists(original, new, merge_strategy, expected):
    """Test dictionary merging with list values."""
    result = dict_merger(original, new, merge_strategy)
    assert result == expected


@pytest.mark.parametrize(
    "original,new,merge_strategy,expected",
    [
        # Set merge with REPLACE
        (
            {"tags": {1, 2, 3}},
            {"tags": {4, 5}},
            MergeStrategy.REPLACE,
            {"tags": {4, 5}},
        ),
        # Set merge with APPEND (union)
        (
            {"tags": {1, 2, 3}},
            {"tags": {3, 4, 5}},
            MergeStrategy.APPEND,
            {"tags": {1, 2, 3, 4, 5}},
        ),
        # Set merge with PREPEND (union)
        (
            {"tags": {1, 2, 3}},
            {"tags": {3, 4, 5}},
            MergeStrategy.PREPEND,
            {"tags": {1, 2, 3, 4, 5}},
        ),
        # Nested dict with sets
        (
            {"config": {"flags": {"a", "b"}}},
            {"config": {"flags": {"c"}}},
            MergeStrategy.APPEND,
            {"config": {"flags": {"a", "b", "c"}}},
        ),
    ],
)
def test_dict_merger_with_sets(original, new, merge_strategy, expected):
    """Test dictionary merging with set values."""
    result = dict_merger(original, new, merge_strategy)
    assert result == expected


@pytest.mark.parametrize(
    "original,new,merge_strategy,expected",
    [
        # Mixed types in nested structure
        (
            {"database": {"hosts": ["localhost"], "ports": {5432}}, "debug": True},
            {
                "database": {"hosts": ["remote"], "timeout": 30},
                "logging": {"level": "INFO"},
            },
            MergeStrategy.APPEND,
            {
                "database": {
                    "hosts": ["localhost", "remote"],
                    "ports": {5432},
                    "timeout": 30,
                },
                "debug": True,
                "logging": {"level": "INFO"},
            },
        ),
        # Multiple levels with PREPEND
        (
            {"level1": {"level2": {"items": [1, 2]}, "other": [10, 20]}, "top": [100]},
            {"level1": {"level2": {"items": [3, 4]}, "other": [30]}, "top": [200]},
            MergeStrategy.PREPEND,
            {
                "level1": {"level2": {"items": [3, 4, 1, 2]}, "other": [30, 10, 20]},
                "top": [200, 100],
            },
        ),
        # None values
        (
            {"a": None, "b": 1},
            {"a": 2, "c": None},
            MergeStrategy.REPLACE,
            {"a": 2, "b": 1, "c": None},
        ),
        # Different primitive types
        (
            {"string": "hello", "int": 42, "float": 3.14, "bool": True},
            {
                "string": "world",
                "int": 99,
                "float": 2.71,
                "bool": False,
                "new_key": "new_value",
            },
            MergeStrategy.REPLACE,
            {
                "string": "world",
                "int": 99,
                "float": 2.71,
                "bool": False,
                "new_key": "new_value",
            },
        ),
    ],
)
def test_dict_merger_complex_scenarios(original, new, merge_strategy, expected):
    """Test complex merging scenarios with mixed types."""
    result = dict_merger(original, new, merge_strategy)
    assert result == expected


@pytest.mark.parametrize(
    "original,new,expected",
    [
        # Keys with special characters
        (
            {"key-with-dash": 1, "key.with.dot": 2},
            {"key_with_underscore": 3, "key with space": 4},
            {
                "key-with-dash": 1,
                "key.with.dot": 2,
                "key_with_underscore": 3,
                "key with space": 4,
            },
        ),
        # Numeric string keys
        (
            {"1": "one", "2": "two"},
            {"3": "three", "1": "ONE"},
            {"1": "ONE", "2": "two", "3": "three"},
        ),
        # Empty strings and lists
        (
            {"empty_str": "", "empty_list": []},
            {"empty_str": "filled", "empty_list": [1, 2]},
            {"empty_str": "filled", "empty_list": [1, 2]},
        ),
    ],
)
def test_dict_merger_edge_cases(original, new, expected):
    """Test edge cases with special keys and empty values."""
    result = dict_merger(original, new)
    assert result == expected


def test_dict_merger_modifies_original():
    """Test that dict_merger modifies the original dict."""
    original = {"a": 1, "b": 2}
    new = {"c": 3}
    result = dict_merger(original, new)
    # The function modifies original and returns it
    assert result is original
    assert result == {"a": 1, "b": 2, "c": 3}


def test_dict_merger_with_deepcopy_changes_original():
    """Test that using deepcopy preserves the original dict."""
    original = {"a": 1, "b": {"c": 2}}
    original_backup = copy.deepcopy(original)
    new = {"b": {"d": 3}}
    result = dict_merger(original, new)
    # Original should be changed
    assert original != original_backup
    assert result == {"a": 1, "b": {"c": 2, "d": 3}}


def test_dict_merger_large_number_of_keys():
    """Test merging dictionaries with many keys."""
    original = {f"key_{i}": i for i in range(100)}
    new = {f"key_{i}": i * 2 for i in range(50, 150)}
    result = dict_merger(original, new)
    expected = {f"key_{i}": i for i in range(50)}
    expected.update({f"key_{i}": i * 2 for i in range(50, 150)})
    assert result == expected
