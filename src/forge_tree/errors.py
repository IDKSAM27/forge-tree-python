"""Custom exceptions for forge-tree."""

class ForgeTreeError(Exception):
    """Base exception for forge-tree operations."""
    pass

class ParseError(ForgeTreeError):
    """Exception raised during parsing operations."""
    pass

class GenerationError(ForgeTreeError):
    """Exception raised during file/directory generation."""
    pass

class TemplateError(ForgeTreeError):
    """Exception raised during template processing."""
    pass
