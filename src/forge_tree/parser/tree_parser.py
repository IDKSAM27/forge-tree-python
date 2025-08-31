"""Tree structure parsing utilities."""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
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
            items = self._parse_structure(lines[1:])
        else:
            items = []
        
        return ProjectStructure(root=root_name, items=items)
    
    def _extract_root_name(self, line: str) -> str:
        """Extract the root directory name from the first line."""
        name = line.strip().rstrip('/')
        if not name:
            raise ForgeTreeError("Invalid root directory name")
        return name
    
    def _parse_structure(self, lines: List[str]) -> List[StructureItem]:
        """Parse the structure lines into StructureItem objects."""
        if not lines:
            return []
        
        items = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            if not line.strip():
                i += 1
                continue
            
            current_depth = self._get_depth(line)
            name, is_directory = self._parse_line(line)
            
            item = StructureItem(
                name=name,
                item_type=ItemType.DIRECTORY if is_directory else ItemType.FILE
            )
            
            # Collect children
            i += 1
            child_lines = []
            
            while i < len(lines):
                child_line = lines[i]
                if not child_line.strip():
                    i += 1
                    continue
                
                child_depth = self._get_depth(child_line)
                
                if child_depth <= current_depth:
                    break
                
                child_lines.append(child_line)
                i += 1
            
            # Recursively parse children
            if child_lines:
                item.children = self._parse_structure(child_lines)
                item.item_type = ItemType.DIRECTORY  # Has children, must be directory
            
            items.append(item)
        
        return items
    
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
    
    def _parse_line(self, line: str) -> tuple[str, bool]:
        """Parse a line to extract name and determine if it's a directory."""
        # Remove tree characters and get content
        content = ''.join(char for char in line if char not in '│├└─ \t').strip()
        
        if not content:
            raise ForgeTreeError(f"Empty name in line: {line}")
        
        # Determine if it's a directory
        is_directory = content.endswith('/') or '.' not in content
        clean_name = content.rstrip('/')
        
        return clean_name, is_directory
