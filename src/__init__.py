"""
Block Blast Enhanced - Main Package with Enterprise-Level Modular Architecture
A comprehensive, modular Tetris-inspired puzzle game with standardized naming conventions.
"""

__version__ = "2.0.0"
__author__ = "Block Blast Team"
__email__ = "team@blockblast.game"

# Import configuration system
from .config import (
    GAME_VERSION,
    GAME_TITLE,
    DisplayConfig,
    ColorPalette,
    GameMode,
    GameRules,
    AudioConfig,
    InputConfig,
    EffectsConfig,
    FileConfig,
    BlockShapesConfig,
    FontConfig,
    DebugConfig,
    get_block_colors,
    get_game_modes,
    validate_configuration,
    initialize_config,
)

# Import core game logic
from .core import (
    BlockData,
    BlockPosition,
    BlockManager,
    GridCell,
    CellState,
    GridManager,
    GameStatistics,
    GameSession,
    GameStateManager,
)

# Import UI components
from .ui import (
    RendererManager,
    EffectsManager,
    InputHandler,
    RenderContext,
    GridRenderer,
    BlockRenderer,
    UIRenderer,
    EffectType,
    EffectInstance,
    ParticleData,
    InputAction,
    InputEvent,
    InputEventType,
)

# Import audio system
from .audio import (
    AudioManager,
    SoundType,
    SoundEffect,
    MusicTrack,
    AudioChannel,
)

# Import utilities
from .utils import (
    FileManager,
    MathUtils,
    TimeUtils,
    ColorUtils,
    ValidationUtils,
)

# Ensure configuration is valid on import
if not validate_configuration():
    raise ImportError("Block Blast configuration is invalid")

__all__ = [
    # Version info
    "__version__",
    "__author__", 
    "__email__",
    
    # Constants
    "GAME_VERSION",
    "GAME_TITLE",
    
    # Configuration classes
    "DisplayConfig",
    "ColorPalette", 
    "GameMode",
    "GameRules",
    "AudioConfig",
    "InputConfig",
    "EffectsConfig",
    "FileConfig",
    "BlockShapesConfig",
    "FontConfig",
    "DebugConfig",
    
    # Configuration utility functions
    "get_block_colors",
    "get_game_modes", 
    "validate_configuration",
    "initialize_config",
    
    # Core game logic
    "BlockData",
    "BlockPosition",
    "BlockManager", 
    "GridCell",
    "CellState",
    "GridManager",
    "GameStatistics",
    "GameSession",
    "GameStateManager",
    
    # UI components
    "RendererManager",
    "EffectsManager",
    "InputHandler",
    "RenderContext",
    "GridRenderer",
    "BlockRenderer",
    "UIRenderer",
    "EffectType",
    "EffectInstance",
    "ParticleData",
    "InputAction",
    "InputEvent",
    "InputEventType",
    
    # Audio system
    "AudioManager",
    "SoundType",
    "SoundEffect",
    "MusicTrack",
    "AudioChannel",
    
    # Utilities
    "FileManager",
    "MathUtils",
    "TimeUtils",
    "ColorUtils",
    "ValidationUtils",
]