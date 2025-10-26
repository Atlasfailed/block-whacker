"""
Enhanced configuration system for Block Blast game.
Centralizes all constants, settings, and configuration values.
"""

import pygame
from enum import Enum
from dataclasses import dataclass
from typing import Tuple, List, Dict, Any
from pathlib import Path

# =============================================================================
# VERSION AND METADATA
# =============================================================================
GAME_VERSION = "2.0.0"
GAME_TITLE = "Block Blast Enhanced"
GAME_AUTHOR = "Block Blast Team"
GAME_DESCRIPTION = "A modular Tetris-inspired puzzle game"

# =============================================================================
# DISPLAY CONFIGURATION
# =============================================================================
class DisplayConfig:
    """Display and window configuration constants."""
    WINDOW_WIDTH: int = 900
    WINDOW_HEIGHT: int = 700
    WINDOW_TITLE: str = f"{GAME_TITLE} v{GAME_VERSION}"
    
    # Frame rate and performance
    TARGET_FPS: int = 60
    VSYNC_ENABLED: bool = True
    
    # Grid display settings
    GRID_SIZE: int = 10
    CELL_SIZE: int = 40
    GRID_OFFSET_X: int = 50
    GRID_OFFSET_Y: int = 100
    GRID_LINE_WIDTH: int = 2
    
    # UI layout
    SIDEBAR_WIDTH: int = 350
    SIDEBAR_PADDING: int = 20
    BLOCK_PREVIEW_SIZE: int = 30
    BLOCK_PREVIEW_SPACING: int = 120
    
    # Visual effects
    SCREEN_SHAKE_INTENSITY: float = 10.0
    FLASH_DURATION: float = 0.3
    ANIMATION_SPEED: float = 5.0

# =============================================================================
# COLOR PALETTE
# =============================================================================
class ColorPalette:
    """Standardized color palette for the entire game."""
    
    # Base colors
    BLACK: Tuple[int, int, int] = (0, 0, 0)
    WHITE: Tuple[int, int, int] = (255, 255, 255)
    TRANSPARENT: Tuple[int, int, int, int] = (0, 0, 0, 0)
    
    # Gray scale
    GRAY_DARK: Tuple[int, int, int] = (64, 64, 64)
    GRAY_MEDIUM: Tuple[int, int, int] = (128, 128, 128)
    GRAY_LIGHT: Tuple[int, int, int] = (200, 200, 200)
    
    # UI colors
    BACKGROUND_PRIMARY: Tuple[int, int, int] = WHITE
    BACKGROUND_SECONDARY: Tuple[int, int, int] = GRAY_LIGHT
    BORDER_PRIMARY: Tuple[int, int, int] = BLACK
    BORDER_SECONDARY: Tuple[int, int, int] = GRAY_MEDIUM
    
    # Block colors (vibrant and distinct)
    BLOCK_BLUE: Tuple[int, int, int] = (52, 152, 219)
    BLOCK_GREEN: Tuple[int, int, int] = (46, 204, 113)
    BLOCK_RED: Tuple[int, int, int] = (231, 76, 60)
    BLOCK_YELLOW: Tuple[int, int, int] = (241, 196, 15)
    BLOCK_PURPLE: Tuple[int, int, int] = (155, 89, 182)
    BLOCK_CYAN: Tuple[int, int, int] = (26, 188, 156)
    BLOCK_ORANGE: Tuple[int, int, int] = (230, 126, 34)
    BLOCK_PINK: Tuple[int, int, int] = (255, 20, 147)
    BLOCK_LIME: Tuple[int, int, int] = (50, 205, 50)
    
    # Special effect colors
    HIGHLIGHT_COLOR: Tuple[int, int, int] = (255, 255, 0)
    ERROR_COLOR: Tuple[int, int, int] = (220, 20, 60)
    SUCCESS_COLOR: Tuple[int, int, int] = (34, 139, 34)
    WARNING_COLOR: Tuple[int, int, int] = (255, 140, 0)
    
    # Text colors
    TEXT_PRIMARY: Tuple[int, int, int] = BLACK
    TEXT_SECONDARY: Tuple[int, int, int] = GRAY_DARK
    TEXT_DISABLED: Tuple[int, int, int] = GRAY_MEDIUM
    TEXT_HIGHLIGHT: Tuple[int, int, int] = HIGHLIGHT_COLOR

# =============================================================================
# GAME MODES AND RULES
# =============================================================================
class GameMode(Enum):
    """Available game modes with standardized naming."""
    CLASSIC = "classic"
    TIMED = "timed"
    CHALLENGE = "challenge"
    ENDLESS = "endless"
    TUTORIAL = "tutorial"

@dataclass
class GameRules:
    """Game rules and mechanics configuration."""
    
    # Scoring system
    SCORE_BLOCK_PLACEMENT: int = 10
    SCORE_LINE_BASE: int = 100
    SCORE_MULTIPLIER_BASE: float = 2.0
    SCORE_COMBO_BONUS: int = 50
    SCORE_PERFECT_CLEAR: int = 2000
    SCORE_ALL_BLOCKS_BONUS: int = 100
    
    # Level progression
    LINES_PER_LEVEL: int = 10
    MAX_LEVEL: int = 99
    
    # Game mode specific settings
    TIMED_MODE_DURATION: int = 300  # 5 minutes in seconds
    CHALLENGE_TARGET_SCORE: int = 10000
    TUTORIAL_STEPS: int = 5
    
    # Block generation
    AVAILABLE_BLOCKS_COUNT: int = 3
    NEXT_BLOCKS_PREVIEW_COUNT: int = 3
    
    # Difficulty scaling
    DIFFICULTY_SCALING_ENABLED: bool = True
    DIFFICULTY_SCALING_FACTOR: float = 1.1

# =============================================================================
# AUDIO CONFIGURATION
# =============================================================================
class AudioConfig:
    """Audio system configuration."""
    
    # General settings
    AUDIO_ENABLED: bool = True
    SAMPLE_RATE: int = 22050
    AUDIO_BUFFER_SIZE: int = 512
    AUDIO_CHANNELS: int = 2
    
    # Volume settings (0.0 to 1.0)
    MASTER_VOLUME: float = 0.8
    MUSIC_VOLUME: float = 0.7
    SFX_VOLUME: float = 0.8
    
    # Sound effect durations
    SFX_BLOCK_PLACE_DURATION: float = 0.1
    SFX_LINE_CLEAR_DURATION: float = 0.3
    SFX_GAME_OVER_DURATION: float = 0.5
    SFX_PERFECT_CLEAR_DURATION: float = 0.8
    SFX_COMBO_DURATION: float = 0.15
    SFX_BLOCK_SELECT_DURATION: float = 0.05

# =============================================================================
# INPUT CONFIGURATION
# =============================================================================
class InputConfig:
    """Input handling configuration."""
    
    # Keyboard mappings
    KEY_RESTART: int = pygame.K_r
    KEY_PAUSE: int = pygame.K_p
    KEY_QUIT: int = pygame.K_ESCAPE
    KEY_SAVE_GAME: int = pygame.K_s
    KEY_LOAD_GAME: int = pygame.K_l
    KEY_TOGGLE_AUDIO: int = pygame.K_m
    KEY_DEBUG_MODE: int = pygame.K_F1
    KEY_ROTATE_BLOCK: int = pygame.K_r
    
    # Game mode selection keys
    KEY_MODE_CLASSIC: int = pygame.K_1
    KEY_MODE_TIMED: int = pygame.K_2
    KEY_MODE_CHALLENGE: int = pygame.K_3
    KEY_MODE_ENDLESS: int = pygame.K_4
    KEY_MODE_TUTORIAL: int = pygame.K_5
    
    # Mouse settings
    MOUSE_CLICK_SENSITIVITY: int = 10  # pixels
    DOUBLE_CLICK_TIME: float = 0.3  # seconds
    DOUBLE_CLICK_DISTANCE: int = 5  # maximum pixels for double click
    
    # Input timing
    ROTATION_COOLDOWN: float = 0.2  # seconds between rotations
    KEY_REPEAT_DELAY: float = 0.25  # initial delay for key repetition (increased from 0.15)
    KEY_REPEAT_INTERVAL: float = 0.15  # interval for key repetition (increased from 0.05)

# =============================================================================
# VISUAL EFFECTS CONFIGURATION
# =============================================================================
class EffectsConfig:
    """Visual and particle effects configuration."""
    
    # Particle system
    PARTICLES_MAX_COUNT: int = 200
    PARTICLE_LIFETIME_MIN: float = 0.3
    PARTICLE_LIFETIME_MAX: float = 1.5
    PARTICLE_SIZE_MIN: int = 2
    PARTICLE_SIZE_MAX: int = 5
    PARTICLE_GRAVITY: float = 200.0
    PARTICLE_VELOCITY_MIN: float = 50.0
    PARTICLE_VELOCITY_MAX: float = 200.0
    
    # Animation timings
    LINE_CLEAR_ANIMATION_DURATION: float = 0.5
    BLOCK_PLACEMENT_ANIMATION_DURATION: float = 0.3
    SCREEN_FLASH_DURATION: float = 0.2
    COMBO_DISPLAY_DURATION: float = 2.0
    
    # Visual feedback
    PREVIEW_ALPHA: int = 128
    SELECTION_HIGHLIGHT_WIDTH: int = 4
    GRID_HIGHLIGHT_ALPHA: int = 100

# =============================================================================
# FILE SYSTEM CONFIGURATION
# =============================================================================
class FileConfig:
    """File paths and data storage configuration."""
    
    # Base directories
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    SRC_DIR: Path = PROJECT_ROOT / "src"
    DATA_DIR: Path = PROJECT_ROOT / "data"
    SAVES_DIR: Path = DATA_DIR / "saves"
    BACKUP_DIR: Path = DATA_DIR / "backups"
    ASSETS_DIR: Path = PROJECT_ROOT / "assets"
    
    # Data files
    HIGH_SCORES_FILE: str = "high_scores.json"
    SAVE_GAME_FILE: str = "save_game.json"
    SETTINGS_FILE: str = "settings.json"
    
    # Ensure directories exist
    @classmethod
    def ensure_directories_exist(cls):
        """Create necessary directories if they don't exist."""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.SAVES_DIR.mkdir(exist_ok=True)
        cls.BACKUP_DIR.mkdir(exist_ok=True)

# =============================================================================
# BLOCK SHAPES CONFIGURATION
# =============================================================================
class BlockShapesConfig:
    """Configuration for block shapes and generation."""
    
    # Standard Tetris-like shapes
    SHAPES_BASIC: List[List[List[int]]] = [
        # Single block
        [[1]],
        
        # Lines (horizontal)
        [[1, 1]],
        [[1, 1, 1]],
        [[1, 1, 1, 1]],
        [[1, 1, 1, 1, 1]],
        
        # Lines (vertical)
        [[1], [1]],
        [[1], [1], [1]],
        [[1], [1], [1], [1]],
        [[1], [1], [1], [1], [1]],
    ]
    
    SHAPES_L_PIECES: List[List[List[int]]] = [
        # Small L shapes
        [[1, 1], [1, 0]],
        [[1, 1], [0, 1]],
        [[1, 0], [1, 1]],
        [[0, 1], [1, 1]],
        
        # Large L shapes
        [[1, 1, 1], [1, 0, 0]],
        [[1, 1, 1], [0, 0, 1]],
        [[1, 0, 0], [1, 1, 1]],
        [[0, 0, 1], [1, 1, 1]],
    ]
    
    SHAPES_SQUARES: List[List[List[int]]] = [
        # Square blocks
        [[1, 1], [1, 1]],
        [[1, 1, 1], [1, 1, 1], [1, 1, 1]],
    ]
    
    SHAPES_T_PIECES: List[List[List[int]]] = [
        # T shapes
        [[1, 1, 1], [0, 1, 0]],
        [[0, 1], [1, 1], [0, 1]],
        [[0, 1, 0], [1, 1, 1]],
        [[1, 0], [1, 1], [1, 0]],
    ]
    
    SHAPES_Z_PIECES: List[List[List[int]]] = [
        # Z shapes
        [[1, 1, 0], [0, 1, 1]],
        [[0, 1, 1], [1, 1, 0]],
        [[1, 0], [1, 1], [0, 1]],
        [[0, 1], [1, 1], [1, 0]],
    ]
    
    SHAPES_SPECIAL: List[List[List[int]]] = [
        # Plus shape
        [[0, 1, 0], [1, 1, 1], [0, 1, 0]],
        
        # Corner shapes
        [[1, 0, 0], [1, 0, 0], [1, 1, 1]],
        [[0, 0, 1], [0, 0, 1], [1, 1, 1]],
        [[1, 1, 1], [1, 0, 0], [1, 0, 0]],
        [[1, 1, 1], [0, 0, 1], [0, 0, 1]],
    ]
    
    # Combined shape list
    @classmethod
    def get_all_shapes(cls) -> List[List[List[int]]]:
        """Get all available block shapes."""
        return (cls.SHAPES_BASIC + cls.SHAPES_L_PIECES + 
                cls.SHAPES_SQUARES + cls.SHAPES_T_PIECES + 
                cls.SHAPES_Z_PIECES + cls.SHAPES_SPECIAL)

# =============================================================================
# FONT CONFIGURATION
# =============================================================================
class FontConfig:
    """Font and typography configuration."""
    
    # Font sizes
    FONT_SIZE_HUGE: int = 48
    FONT_SIZE_LARGE: int = 36
    FONT_SIZE_MEDIUM: int = 24
    FONT_SIZE_SMALL: int = 18
    FONT_SIZE_TINY: int = 14
    
    # Font styles
    FONT_FAMILY_DEFAULT: str = "Arial"
    FONT_FAMILY_MONOSPACE: str = "Courier New"
    
    # Text rendering
    TEXT_ANTIALIAS: bool = True
    TEXT_LINE_SPACING: float = 1.2

# =============================================================================
# DEVELOPMENT AND DEBUG CONFIGURATION
# =============================================================================
class DebugConfig:
    """Development and debugging configuration."""
    
    DEBUG_MODE_ENABLED: bool = False
    SHOW_FPS: bool = True
    SHOW_GRID_COORDINATES: bool = False
    SHOW_COLLISION_BOXES: bool = False
    SHOW_PARTICLE_COUNT: bool = True
    LOG_LEVEL: str = "INFO"
    VERBOSE_LOGGING: bool = False

# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================
def get_block_colors() -> List[Tuple[int, int, int]]:
    """Get all available block colors."""
    return [
        ColorPalette.BLOCK_BLUE,
        ColorPalette.BLOCK_GREEN,
        ColorPalette.BLOCK_RED,
        ColorPalette.BLOCK_YELLOW,
        ColorPalette.BLOCK_PURPLE,
        ColorPalette.BLOCK_CYAN,
        ColorPalette.BLOCK_ORANGE,
        ColorPalette.BLOCK_PINK,
        ColorPalette.BLOCK_LIME,
    ]

def get_game_modes() -> List[GameMode]:
    """Get all available game modes."""
    return list(GameMode)

def validate_configuration() -> bool:
    """Validate all configuration values."""
    try:
        # Check display configuration
        assert DisplayConfig.WINDOW_WIDTH > 0
        assert DisplayConfig.WINDOW_HEIGHT > 0
        assert DisplayConfig.GRID_SIZE > 0
        assert DisplayConfig.CELL_SIZE > 0
        
        # Check color values
        for color in get_block_colors():
            assert len(color) == 3
            assert all(0 <= c <= 255 for c in color)
        
        # Check game rules
        assert GameRules.SCORE_BLOCK_PLACEMENT >= 0
        assert GameRules.TIMED_MODE_DURATION > 0
        
        # Ensure file directories
        FileConfig.ensure_directories_exist()
        
        return True
    except (AssertionError, Exception) as e:
        print(f"Configuration validation failed: {e}")
        return False

# =============================================================================
# INITIALIZATION
# =============================================================================
def initialize_config():
    """Initialize configuration system."""
    if not validate_configuration():
        raise RuntimeError("Configuration validation failed")
    
    FileConfig.ensure_directories_exist()
    print(f"Configuration initialized for {GAME_TITLE} v{GAME_VERSION}")

# Auto-initialize when module is imported
initialize_config()