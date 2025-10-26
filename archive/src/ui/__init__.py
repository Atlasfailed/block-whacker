"""
UI Package - User Interface components with standardized rendering and input handling.
Provides comprehensive interface management for the Block Blast game.
"""

# Import managers
from .renderer_manager import RendererManager, RenderContext
from .effects_manager import EffectsManager
from .input_handler import InputHandler

# Import specialized renderers
from .renderer_manager import GridRenderer, BlockRenderer, UIRenderer

# Import effect types and data
from .effects_manager import (
    EffectType,
    EffectInstance,
    ParticleData,
    LineCloseEffect,
    ScorePopupEffect,
    ComboEffect,
    ScreenShakeEffect,
    BlockPlacementEffect
)

# Import input types and data
from .input_handler import (
    InputEventType,
    InputAction,
    InputEvent,
    KeyboardHandler,
    MouseHandler,
    InputManager
)

# Package version and metadata
__version__ = "1.0.0"
__author__ = "Block Blast Game Team"

# Main exports
__all__ = [
    # Main managers
    'RendererManager',
    'EffectsManager', 
    'InputHandler',
    
    # Rendering components
    'RenderContext',
    'GridRenderer',
    'BlockRenderer',
    'UIRenderer',
    
    # Effects system
    'EffectType',
    'EffectInstance',
    'ParticleData',
    'LineCloseEffect',
    'ScorePopupEffect',
    'ComboEffect',
    'ScreenShakeEffect',
    'BlockPlacementEffect',
    
    # Input system
    'InputEventType',
    'InputAction',
    'InputEvent',
    'KeyboardHandler',
    'MouseHandler',
    'InputManager',
]