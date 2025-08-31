"""
Forge-Tree Python

A powerful project scaffolding tool that generates folder and file structures
from text representations.

This is the Python implementation of forge-tree. For maximum performance,
check out the Rust version: https://github.com/IDKSAM27/forge-tree

Example:
    >>> from forge_tree import Parser, Generator
    >>> structure = '''
    ... my-project/
    ... ├── src/main.py
    ... └── README.md
    ... '''
    >>> parsed = Parser().parse(structure)
    >>> Generator().generate(parsed, "./output")
"""

from .parser.tree_parser import TreeParser as Parser
from .generator.file_generator import FileGenerator as Generator
from .errors import ForgeTreeError

__version__ = "0.1.0"
__author__ = "Sampreet Patil"
__email__ = "sampreetpatil270@gmail.com"
__description__ = "Python implementation of forge-tree - Transform ASCII trees into real project structures"
__repository__ = "https://github.com/IDKSAM27/forge-tree-python"
__rust_version__ = "https://github.com/IDKSAM27/forge-tree"

__all__ = ["Parser", "Generator", "ForgeTreeError"]
