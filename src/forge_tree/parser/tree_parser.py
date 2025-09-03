"""Tree structure parsing utilities."""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum

from ..errors import ForgeTreeError

class ItemType(Enum):
    """Type of structure item."""
    FILE = "file"
    DIRECTORY = "directory"

@dataclass
class StructureItem:
    """Represents a file or directory in the project structure."""
    name: str
    item_type: ItemType
    children: List['StructureItem'] = field(default_factory=list)
    template: Optional[str] = None
    content: Optional[str] = None

@dataclass
class ProjectStructure:
    """Represents a complete project structure."""
    root: str
    items: List[StructureItem] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)

class TreeParser:
    """Parses ASCII tree structures into ProjectStructure objects."""
    
    def __init__(self):
        self.tree_chars_pattern = re.compile(r'^([│├└─\s]*)(.*?)/?$')
    
    def parse(self, content: str) -> ProjectStructure:
        """Parse text content into a ProjectStructure."""
        lines = [line.rstrip() for line in content.splitlines() if line.strip()]
        
        if not lines:
            raise ForgeTreeError("Empty input")
        
        root_name = self._extract_root_name(lines[0])
        
        if len(lines) > 1:
            # Start parsing from line 1 (after root) with depth 0
            items, _ = self._parse_structure(lines, 1, 0)
        else:
            items = []
        
        return ProjectStructure(root=root_name, items=items)
    
    def _extract_root_name(self, line: str) -> str:
        """Extract the root directory name from the first line."""
        name = line.strip().rstrip('/')
        if not name:
            raise ForgeTreeError("Invalid root directory name")
        return name
    
    def _parse_structure(self, lines: List[str], start_index: int, current_depth: int) -> Tuple[List[StructureItem], int]:
        """Parse the structure lines into StructureItem objects with proper sibling handling."""
        items = []
        i = start_index
        
        while i < len(lines):
            line = lines[i]
            if not line.strip():
                i += 1
                continue
            
            depth = self._get_depth(line)
            
            if depth < current_depth:
                # We've returned to an ancestor level - stop parsing at this level
                break
            elif depth > current_depth:
                # This line is deeper - it should be a child of the previous item
                if not items:
                    raise ForgeTreeError(f"Invalid tree structure at line: {line}")
                
                # Recursively parse children and update the index
                children, new_i = self._parse_structure(lines, i, depth)
                items[-1].children = children
                items[-1].item_type = ItemType.DIRECTORY  # Has children, must be directory
                i = new_i
            else:
                # Same depth - this is a sibling, parse it normally
                name, is_directory = self._parse_line(line)
                item = StructureItem(
                    name=name,
                    item_type=ItemType.DIRECTORY if is_directory else ItemType.FILE
                )
                items.append(item)
                i += 1
        
        return items, i
    
    def _get_depth(self, line: str) -> int:
        """Calculate the indentation depth of a line."""
        depth = 0
        for char in line:
            if char in '├└│':
                depth += 1
            elif char in '─ \t':
                continue
            else:
                break
        return depth
    
    def _parse_line(self, line: str) -> Tuple[str, bool]:
        """Parse a line to extract name and determine if it's a directory."""
        # Remove tree characters and get content
        content = ''.join(char for char in line if char not in '│├└─ \t').strip()
        
        if not content:
            raise ForgeTreeError(f"Empty name in line: {line}")
        
        # Determine if it's a directory
        is_directory = content.endswith('/') or '.' not in content
        clean_name = content.rstrip('/')
        
        return clean_name, is_directory
