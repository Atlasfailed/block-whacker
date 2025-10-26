"""
Audio Package - Sound and music management with standardized audio handling.
Provides comprehensive audio system for the Block Blast game.
"""

# Import main audio manager
from .audio_manager import AudioManager

# Import audio types and components
from .audio_manager import (
    SoundType,
    AudioConfig,
    SoundEffect,
    MusicTrack,
    AudioChannel
)

# Package version and metadata
__version__ = "1.0.0"
__author__ = "Block Blast Game Team"

# Main exports
__all__ = [
    # Main manager
    'AudioManager',
    
    # Audio system types
    'SoundType',
    'AudioConfig', 
    'SoundEffect',
    'MusicTrack',
    'AudioChannel',
]