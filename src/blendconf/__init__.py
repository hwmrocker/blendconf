import warnings
from enum import Enum
from pathlib import Path
from typing import Any, Literal


class MergeStrategy(Enum):
    APPEND = "append"
    PREPEND = "prepend"
    REPLACE = "replace"


def load_file(file_path: Path) -> Any:
    match file_path.suffix.lower():
        case ".yaml" | ".yml":
            import yaml

            with file_path.open("r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        case ".toml":
            import tomli

            with file_path.open("rb") as f:
                return tomli.load(f)
        case ".json":
            import json

            with file_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        case ".env":
            import dotenv

            return dotenv.dotenv_values(file_path)
        case _:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")


def dict_merger(
    original: dict, new: dict, merge_strategy: MergeStrategy = MergeStrategy.REPLACE
) -> dict:
    """Merge two configuration dictionaries.

    Args:
        original (dict): The original configuration dictionary.
        new (dict): The new configuration dictionary to merge into the original.

    Returns:
        dict: The merged configuration dictionary.
    """
    for key, value in new.items():
        match (original.get(key), value):
            case (dict(), dict()):
                original[key] = dict_merger(original[key], value, merge_strategy)
            case (list(), list()):
                original[key] = list_merger(original[key], value, merge_strategy)
            case (set(), set()):
                original[key] = set_merger(original[key], value, merge_strategy)
            case _:
                original[key] = value
    return original


def list_merger(
    original: list,
    new: list | None,
    merge_strategy: MergeStrategy = MergeStrategy.REPLACE,
) -> list:
    """Merge two configuration lists based on the specified strategy.

    Args:
        original (list): The original configuration list.
        new (list): The new configuration list to merge into the original.
        merge_strategy (ListMergeStrategy): The strategy to use for merging lists.

    Returns:
        list: The merged configuration list.
    """
    if new is None:
        return original

    match merge_strategy:
        case MergeStrategy.APPEND:
            return original + new
        case MergeStrategy.PREPEND:
            return new + original
        case MergeStrategy.REPLACE:
            return new
        case _:
            raise ValueError(f"Unsupported merge strategy: {merge_strategy}")


def set_merger(
    original: set,
    new: set | None,
    merge_strategy: MergeStrategy = MergeStrategy.REPLACE,
) -> set:
    """Merge two configuration sets based on the specified strategy.

    Args:
        original (set): The original configuration set.
        new (set): The new configuration set to merge into the original.
        merge_strategy (SetMergeStrategy): The strategy to use for merging sets.

    Returns:
        set: The merged configuration set.
    """
    if new is None:
        return original

    match merge_strategy:
        case MergeStrategy.APPEND | MergeStrategy.PREPEND:
            return original.union(new)
        case MergeStrategy.REPLACE:
            return new
        case _:
            raise ValueError(f"Unsupported merge strategy: {merge_strategy}")


def dump_file(
    data: Any,
    file_path: Path | None,
    file_type: Literal["yaml", "toml", "json", "env"] | None = None,
) -> None:
    try:
        if file_path is None:
            if file_type is None:
                raise ValueError("file_type must be specified when file_path is None")
            import sys

            fh = sys.stdout
            suffix = f".{file_type}"
        else:
            fh = file_path.open("w", encoding="utf-8")
            suffix = file_path.suffix.lower()

        match suffix:
            case ".yaml" | ".yml":
                import yaml

                yaml.safe_dump(data, fh)
            case ".toml":
                import tomli_w

                fh.write(tomli_w.dumps(data))
            case ".json":
                import json

                json.dump(data, fh, indent=4)
            case ".env":
                for key, value in data.items():
                    fh.write(f"{key}={value}\n")
            case _:
                raise ValueError(f"Unsupported file format: {suffix}")
    finally:
        if file_path is not None:
            fh.close()


def merge_configs(
    config_files: list[Path], merge_strategy: MergeStrategy = MergeStrategy.REPLACE
) -> Any:
    merged_config: Any = None

    for file_path in config_files:
        config_data = load_file(file_path)

        if merged_config is None:
            merged_config = config_data
        else:
            match (merged_config, config_data):
                case (dict(), dict()):
                    merged_config = dict_merger(
                        merged_config, config_data, merge_strategy
                    )
                case (list(), list()):
                    merged_config = list_merger(
                        merged_config, config_data, merge_strategy
                    )
                case (set(), set()):
                    merged_config = set_merger(
                        merged_config, config_data, merge_strategy
                    )
                case _:
                    warnings.warn(
                        f"Cannot merge different types: {type(merged_config)} and {type(config_data)}. Replacing."
                    )
                    merged_config = config_data

    return merged_config
