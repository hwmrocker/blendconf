from pathlib import Path

import typer
from rich.console import Console
from rich.traceback import install

from blendconf import MergeStrategy, dump_file, merge_configs

install()
console = Console(
    stderr=True,
)
print = console.print


def main(
    input_files: list[Path] = typer.Argument(
        ...,
        help="List of input configuration files to merge.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
    output_file: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Path to the output merged configuration file. Defaults to stdout.",
        writable=True,
        resolve_path=True,
    ),
    merge_strategy: MergeStrategy = typer.Option(
        MergeStrategy.REPLACE,
        "--strategy",
        "-s",
        help="Merge strategy to use when merging configurations.",
    ),
):
    """
    Merge multiple configuration files into one.

    Supports YAML, TOML, JSON, and ENV file formats.
    """
    if not input_files:
        print("[red]Error:[/red] No input files provided.")
        raise typer.Exit(code=1)

    try:
        merged_config = merge_configs(input_files, merge_strategy)

        if output_file is None:
            suffix = input_files[0].suffix.lower() if input_files else ".yaml"
        else:
            suffix = output_file.suffix.lower()

        match suffix:
            case ".yaml" | ".yml":
                file_type = "yaml"
            case ".toml":
                file_type = "toml"
            case ".json":
                file_type = "json"
            case ".env":
                file_type = "env"
            case _:
                print(f"[red]Error:[/red] Unsupported output file format: {suffix}")
                raise typer.Exit(code=1)

        dump_file(merged_config, output_file, file_type)
        if output_file:
            print(
                f"[green]Success:[/green] Merged configuration written to {output_file}"
            )

    except Exception as e:
        print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)


def entry_point():
    typer.run(main)


if __name__ == "__main__":
    entry_point()
