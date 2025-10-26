"""
Utils Package - Utility functions and helper classes with standardized naming.
Provides common functionality used across the Block Blast game.
"""

# Import utility modules
from .file_manager import FileManager
from .math_utils import MathUtils
from .time_utils import TimeUtils
from .color_utils import ColorUtils
from .validation_utils import ValidationUtils

# Package version and metadata
__version__ = "1.0.0"
__author__ = "Block Blast Game Team"

# Main exports
__all__ = [
    # Utility managers and classes
    'FileManager',
    'MathUtils', 
    'TimeUtils',
    'ColorUtils',
    'ValidationUtils',
]