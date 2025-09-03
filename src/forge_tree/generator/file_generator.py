"""File and directory generation utilities."""

import os
from pathlib import Path
from typing import Optional, Callable, List, Dict

from rich.console import Console
from jinja2 import Environment, BaseLoader, TemplateError

from ..parser.tree_parser import ProjectStructure, StructureItem, ItemType
from ..errors import ForgeTreeError


class FileGenerator:
    """Generates files and directories from ProjectStructure."""

    def __init__(self, force_overwrite: bool = False, verbose: bool = False):
        self.force_overwrite = force_overwrite
        self.verbose = verbose
        self.console = Console()
        self.jinja_env = Environment(loader=BaseLoader())

    def generate(
        self,
        structure: ProjectStructure,
        output_path: Path,
        progress_callback: Optional[Callable] = None,
    ):
        """Generate the complete project structure."""

        # Create root directory
        root_path = output_path / structure.root
        self._create_directory(root_path)

        if self.verbose:
            self.console.print(f"✅ Created {root_path}", style="green")

        # Generate all items without double progress callback
        self._generate_items(
            structure.items, root_path, structure.variables, progress_callback
        )

    def _generate_items(
        self,
        items: List[StructureItem],
        base_path: Path,
        variables: Dict,
        progress_callback: Optional[Callable] = None,
    ):
        """Recursively generate all items."""

        for item in items:
            item_path = base_path / item.name

            # Update progress BEFORE processing, not during
            if progress_callback:
                progress_callback()

            if item.item_type == ItemType.DIRECTORY:
                self._create_directory(item_path)

                if self.verbose:
                    self.console.print(f"📁 Created {item_path}", style="green")

                # Recursively generate children WITHOUT passing progress_callback
                if item.children:
                    self._generate_items(
                        item.children, item_path, variables, progress_callback
                    )

            else:  # FILE
                content = self._render_content(item, variables)
                self._create_file(item_path, content)

                if self.verbose:
                    self.console.print(f"📄 Created {item_path}", style="blue")

    def _create_directory(self, path: Path):
        """Create a directory."""
        if path.exists() and not path.is_dir():
            raise ForgeTreeError(f"Path exists but is not a directory: {path}")

        path.mkdir(parents=True, exist_ok=True)

    def _create_file(self, path: Path, content: str):
        """Create a file with content."""
        if path.exists() and not self.force_overwrite:
            raise ForgeTreeError(f"File already exists: {path}")

        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def _render_content(self, item: StructureItem, variables: Dict) -> str:
        """Render template content with variables."""
        if item.template:
            try:
                template = self.jinja_env.from_string(item.template)
                return template.render(**variables)
            except TemplateError as e:
                raise ForgeTreeError(f"Template error in {item.name}: {e}")

        return item.content or ""
