"""Command-line interface for forge-tree Python implementation."""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

import click
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeElapsedColumn,
)
from rich.panel import Panel
from rich.text import Text

from .parser.tree_parser import TreeParser
from .generator.file_generator import FileGenerator
from .errors import ForgeTreeError

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """
    🐍🏗️🌳 Forge project structures from text representations (Python implementation).

    🦀 For maximum performance, try the Rust version: https://crates.io/crates/forge-tree
    """
    pass


@main.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-o",
    "--output",
    default=".",
    type=click.Path(path_type=Path),
    help="Output directory (default: current directory)",
)
@click.option("-f", "--force", is_flag=True, help="Force overwrite existing files")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Verbose output showing each file/directory creation",
)
@click.option("--var", multiple=True, help="Set template variables (format: key=value)")
def forge(input_file: Path, output: Path, force: bool, verbose: bool, var: tuple):
    """Forge a project structure from a text file."""

    try:
        # Parse variables
        variables = {}
        for variable in var:
            if "=" in variable:
                key, value = variable.split("=", 1)
                variables[key.strip()] = value.strip()
            else:
                console.print(
                    f"⚠️  Invalid variable format: {variable} (expected key=value)",
                    style="yellow",
                )

        if verbose:
            console.print(f"📖 Parsing structure from: {input_file}", style="cyan")

        # Parse the structure
        parser = TreeParser()
        with open(input_file, "r", encoding="utf-8") as f:
            content = f.read()

        structure = parser.parse(content)
        structure.variables.update(variables)

        if verbose:
            console.print(f"🌳 Root: {structure.root}", style="green")
            console.print(f"📁 Items: {count_items(structure.items)}", style="blue")

        # Generate the project
        generator = FileGenerator(force_overwrite=force, verbose=verbose)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.1f}%",
            "•",
            TextColumn("[progress.completed]{task.completed}/{task.total}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:

            total_items = count_items(structure.items)
            task = progress.add_task("🏗️ Forging project...", total=total_items)

            generator.generate(
                structure, output, progress_callback=lambda: progress.advance(task)
            )

        # Success message
        project_path = output / structure.root
        console.print()
        console.print(
            Panel(
                f"✅ Project '[bold cyan]{structure.root}[/bold cyan]' forged successfully!\n"
                f"📍 Location: [bold]{project_path.resolve()}[/bold]\n\n"
                f"🦀 [dim]Try the Rust version for even faster performance: cargo install forge-tree[/dim]",
                title="🎉 Success",
                border_style="green",
            )
        )

    except ForgeTreeError as e:
        console.print(f"❌ Error: {e}", style="red")
        sys.exit(1)
    except Exception as e:
        console.print(f"💥 Unexpected error: {e}", style="red")
        sys.exit(1)


@main.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
def validate(input_file: Path):
    """Validate a structure file without forging it."""

    try:
        console.print(f"🔍 Validating: {input_file}", style="cyan")

        parser = TreeParser()
        with open(input_file, "r", encoding="utf-8") as f:
            content = f.read()

        structure = parser.parse(content)

        console.print(
            Panel(
                f"✅ Structure is valid!\n"
                f"🌳 Root: [bold]{structure.root}[/bold]\n"
                f"📊 Total items: [bold]{count_items(structure.items)}[/bold]",
                title="Validation Results",
                border_style="green",
            )
        )

    except ForgeTreeError as e:
        console.print(f"❌ Validation failed: {e}", style="red")
        sys.exit(1)


def count_items(items) -> int:
    """Recursively count total items in structure."""
    count = len(items)
    for item in items:
        count += count_items(item.children)
    return count


if __name__ == "__main__":
    main()
