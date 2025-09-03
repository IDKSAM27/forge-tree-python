"""Tests for the tree parser."""

import pytest
from forge_tree.parser.tree_parser import TreeParser, ProjectStructure, ItemType
from forge_tree.errors import ForgeTreeError


def test_simple_structure():
    """Test parsing a simple structure."""
    content = """my-project/
├── src/main.py
└── README.md"""

    parser = TreeParser()
    structure = parser.parse(content)

    assert structure.root == "my-project"
    assert len(structure.items) == 2
    assert structure.items[0].name == "src"
    assert structure.items[0].item_type == ItemType.DIRECTORY


def test_nested_structure():
    """Test parsing nested directories."""
    content = """my-app/
├── src/
│   ├── main.py
│   └── utils/
│       └── helpers.py
└── tests/"""

    parser = TreeParser()
    structure = parser.parse(content)

    assert structure.root == "my-app"
    src_item = structure.items[0]
    assert src_item.name == "src"
    assert len(src_item.children) == 2


def test_empty_input():
    """Test that empty input raises an error."""
    parser = TreeParser()

    with pytest.raises(ForgeTreeError):
        parser.parse("")
