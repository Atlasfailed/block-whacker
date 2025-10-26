"""
Input Handler - Manages all input processing with standardized event handling.
Provides unified interface for keyboard, mouse, and other input devices.
"""

import pygame
from typing import Dict, List, Set, Optional, Callable, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from ..config import InputConfig, DisplayConfig


class InputEventType(Enum):
    """Types of input events."""
    KEY_DOWN = "key_down"
    KEY_UP = "key_up"
    MOUSE_DOWN = "mouse_down"
    MOUSE_UP = "mouse_up"
    MOUSE_MOTION = "mouse_motion"
    QUIT = "quit"


class InputAction(Enum):
    """Game input actions."""
    QUIT_GAME = "quit_game"
    PAUSE_TOGGLE = "pause_toggle"
    ROTATE_BLOCK = "rotate_block"
    SELECT_BLOCK = "select_block"
    PLACE_BLOCK = "place_block"
    RESET_GAME = "reset_game"
    TOGGLE_DEBUG = "toggle_debug"
    SAVE_GAME = "save_game"
    LOAD_GAME = "load_game"
    TOGGLE_SOUND = "toggle_sound"
    TOGGLE_MUSIC = "toggle_music"
    NEXT_BLOCK = "next_block"
    PREVIOUS_BLOCK = "previous_block"
    
    # New movement actions
    MOVE_UP = "move_up"
    MOVE_DOWN = "move_down"
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    CONFIRM_PLACEMENT = "confirm_placement"
    
    # Block selection actions
    SELECT_BLOCK_1 = "select_block_1"
    SELECT_BLOCK_2 = "select_block_2"
    SELECT_BLOCK_3 = "select_block_3"


@dataclass
class InputEvent:
    """Standardized input event data."""
    event_type: InputEventType
    action: Optional[InputAction] = None
    key_code: Optional[int] = None
    mouse_button: Optional[int] = None
    mouse_position: Optional[Tuple[int, int]] = None
    modifiers: Set[str] = None
    raw_event: Optional[pygame.event.Event] = None
    
    def __post_init__(self):
        if self.modifiers is None:
            self.modifiers = set()


class KeyboardHandler:
    """Handles keyboard input processing."""
    
    def __init__(self):
        """Initialize keyboard handler."""
        self.pressed_keys: Set[int] = set()
        self.key_repeat_timers: Dict[int, float] = {}
        self.key_first_repeat: Dict[int, bool] = {}  # Track if first repeat has occurred
        
        # Key bindings
        self.key_bindings = {
            pygame.K_ESCAPE: InputAction.QUIT_GAME,
            pygame.K_p: InputAction.PAUSE_TOGGLE,
            pygame.K_r: InputAction.ROTATE_BLOCK,  # R key rotates blocks
            pygame.K_b: InputAction.ROTATE_BLOCK,  # B key also rotates blocks
            pygame.K_F1: InputAction.TOGGLE_DEBUG,
            pygame.K_F5: InputAction.RESET_GAME,  # F5 resets the game
            pygame.K_s: InputAction.SAVE_GAME,
            pygame.K_l: InputAction.LOAD_GAME,
            pygame.K_m: InputAction.TOGGLE_MUSIC,
            pygame.K_n: InputAction.TOGGLE_SOUND,
            pygame.K_TAB: InputAction.NEXT_BLOCK,
            pygame.K_BACKSPACE: InputAction.PREVIOUS_BLOCK,
            
            # Movement controls
            pygame.K_LEFT: InputAction.MOVE_LEFT,
            pygame.K_RIGHT: InputAction.MOVE_RIGHT,
            pygame.K_UP: InputAction.MOVE_UP,
            pygame.K_DOWN: InputAction.MOVE_DOWN,
            pygame.K_SPACE: InputAction.CONFIRM_PLACEMENT,  # Space places blocks
            
            # Block selection
            pygame.K_1: InputAction.SELECT_BLOCK_1,
            pygame.K_2: InputAction.SELECT_BLOCK_2,
            pygame.K_3: InputAction.SELECT_BLOCK_3,
        }
        
        # Keys that support continuous input (hold down)
        self.repeatable_keys = {
            pygame.K_LEFT,
            pygame.K_RIGHT,
            pygame.K_UP,
            pygame.K_DOWN
        }
    
    def process_key_event(self, event: pygame.event.Event) -> Optional[InputEvent]:
        """Process keyboard event and return standardized input event."""
        if event.type == pygame.KEYDOWN:
            self.pressed_keys.add(event.key)
            
            # Initialize repeat timer for repeatable keys
            if event.key in self.repeatable_keys:
                self.key_repeat_timers[event.key] = 0.0
                self.key_first_repeat[event.key] = True  # Mark as waiting for first repeat
            
            # Get action for key
            action = self.key_bindings.get(event.key)
            
            # Get modifiers
            modifiers = self._get_current_modifiers()
            
            return InputEvent(
                event_type=InputEventType.KEY_DOWN,
                action=action,
                key_code=event.key,
                modifiers=modifiers,
                raw_event=event
            )
        
        elif event.type == pygame.KEYUP:
            self.pressed_keys.discard(event.key)
            
            # Remove repeat timer
            self.key_repeat_timers.pop(event.key, None)
            self.key_first_repeat.pop(event.key, None)
            
            action = self.key_bindings.get(event.key)
            modifiers = self._get_current_modifiers()
            
            return InputEvent(
                event_type=InputEventType.KEY_UP,
                action=action,
                key_code=event.key,
                modifiers=modifiers,
                raw_event=event
            )
        
        return None
    
    def update_key_repeat(self, delta_time: float) -> List[InputEvent]:
        """Update key repeat timers and generate repeat events."""
        repeat_events = []
        
        for key in list(self.key_repeat_timers.keys()):
            if key not in self.pressed_keys:
                # Key was released, remove timer
                self.key_repeat_timers.pop(key, None)
                self.key_first_repeat.pop(key, None)
                continue
            
            self.key_repeat_timers[key] += delta_time
            
            # Use different thresholds for first repeat vs subsequent repeats
            is_first_repeat = self.key_first_repeat.get(key, True)
            threshold = InputConfig.KEY_REPEAT_DELAY if is_first_repeat else InputConfig.KEY_REPEAT_INTERVAL
            
            # Check if it's time for a repeat
            if self.key_repeat_timers[key] >= threshold:
                self.key_repeat_timers[key] = 0.0
                
                # Mark that first repeat has occurred
                if is_first_repeat:
                    self.key_first_repeat[key] = False
                
                action = self.key_bindings.get(key)
                modifiers = self._get_current_modifiers()
                
                repeat_event = InputEvent(
                    event_type=InputEventType.KEY_DOWN,
                    action=action,
                    key_code=key,
                    modifiers=modifiers
                )
                repeat_events.append(repeat_event)
        
        return repeat_events
    
    def _get_current_modifiers(self) -> Set[str]:
        """Get currently pressed modifier keys."""
        modifiers = set()
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
            modifiers.add('ctrl')
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            modifiers.add('shift')
        if keys[pygame.K_LALT] or keys[pygame.K_RALT]:
            modifiers.add('alt')
        
        return modifiers
    
    def is_key_pressed(self, key: int) -> bool:
        """Check if a key is currently pressed."""
        return key in self.pressed_keys
    
    def add_key_binding(self, key: int, action: InputAction) -> None:
        """Add a key binding."""
        self.key_bindings[key] = action
    
    def remove_key_binding(self, key: int) -> None:
        """Remove a key binding."""
        self.key_bindings.pop(key, None)
    
    def get_key_bindings(self) -> Dict[int, InputAction]:
        """Get all current key bindings."""
        return self.key_bindings.copy()


class MouseHandler:
    """Handles mouse input processing."""
    
    def __init__(self):
        """Initialize mouse handler."""
        self.mouse_position = (0, 0)
        self.pressed_buttons: Set[int] = set()
        self.last_click_time = 0.0
        self.last_click_position = (0, 0)
        
        # Mouse button mappings
        self.button_actions = {
            1: InputAction.SELECT_BLOCK,  # Left click for both selection and placement
            3: InputAction.PLACE_BLOCK,   # Right click for placement only
        }
    
    def process_mouse_event(self, event: pygame.event.Event) -> Optional[InputEvent]:
        """Process mouse event and return standardized input event."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.pressed_buttons.add(event.button)
            self.last_click_time = pygame.time.get_ticks() / 1000.0
            self.last_click_position = event.pos
            
            action = self.button_actions.get(event.button)
            
            return InputEvent(
                event_type=InputEventType.MOUSE_DOWN,
                action=action,
                mouse_button=event.button,
                mouse_position=event.pos,
                raw_event=event
            )
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.pressed_buttons.discard(event.button)
            
            action = self.button_actions.get(event.button)
            
            return InputEvent(
                event_type=InputEventType.MOUSE_UP,
                action=action,
                mouse_button=event.button,
                mouse_position=event.pos,
                raw_event=event
            )
        
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_position = event.pos
            
            return InputEvent(
                event_type=InputEventType.MOUSE_MOTION,
                mouse_position=event.pos,
                raw_event=event
            )
        
        return None
    
    def is_button_pressed(self, button: int) -> bool:
        """Check if a mouse button is currently pressed."""
        return button in self.pressed_buttons
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse position."""
        return self.mouse_position
    
    def is_double_click(self, current_time: float, current_position: Tuple[int, int]) -> bool:
        """Check if current click is a double click."""
        time_diff = current_time - self.last_click_time
        position_diff = (
            abs(current_position[0] - self.last_click_position[0]) +
            abs(current_position[1] - self.last_click_position[1])
        )
        
        return (time_diff <= InputConfig.DOUBLE_CLICK_TIME and 
                position_diff <= InputConfig.DOUBLE_CLICK_DISTANCE)
    
    def is_position_in_grid(self, position: Tuple[int, int]) -> bool:
        """Check if position is within the game grid."""
        x, y = position
        
        grid_left = DisplayConfig.GRID_OFFSET_X
        grid_right = grid_left + DisplayConfig.GRID_SIZE * DisplayConfig.CELL_SIZE
        grid_top = DisplayConfig.GRID_OFFSET_Y
        grid_bottom = grid_top + DisplayConfig.GRID_SIZE * DisplayConfig.CELL_SIZE
        
        return grid_left <= x <= grid_right and grid_top <= y <= grid_bottom
    
    def is_position_in_sidebar(self, position: Tuple[int, int]) -> bool:
        """Check if position is within the sidebar area."""
        x, y = position
        
        sidebar_left = DisplayConfig.GRID_OFFSET_X + DisplayConfig.GRID_SIZE * DisplayConfig.CELL_SIZE
        sidebar_right = DisplayConfig.WINDOW_WIDTH
        
        return sidebar_left <= x <= sidebar_right and y >= 0
    
    def add_button_action(self, button: int, action: InputAction) -> None:
        """Add a mouse button action mapping."""
        self.button_actions[button] = action
    
    def remove_button_action(self, button: int) -> None:
        """Remove a mouse button action mapping."""
        self.button_actions.pop(button, None)


class InputManager:
    """
    Main input manager that coordinates all input handling.
    Provides unified interface for processing user input.
    """
    
    def __init__(self):
        """Initialize input manager."""
        self.keyboard_handler = KeyboardHandler()
        self.mouse_handler = MouseHandler()
        
        # Event callbacks
        self.action_callbacks: Dict[InputAction, List[Callable]] = {}
        
        # Input state
        self.input_enabled = True
        self.debug_mode = False
        
        # Statistics
        self.total_events_processed = 0
        self.events_per_type: Dict[InputEventType, int] = {}
        self.actions_per_type: Dict[InputAction, int] = {}
    
    def process_events(self, delta_time: float) -> List[InputEvent]:
        """Process all pygame events and return standardized input events."""
        if not self.input_enabled:
            return []
        
        input_events = []
        
        # Process pygame events
        for raw_event in pygame.event.get():
            input_event = None
            
            if raw_event.type == pygame.QUIT:
                input_event = InputEvent(
                    event_type=InputEventType.QUIT,
                    action=InputAction.QUIT_GAME,
                    raw_event=raw_event
                )
            
            elif raw_event.type in [pygame.KEYDOWN, pygame.KEYUP]:
                input_event = self.keyboard_handler.process_key_event(raw_event)
            
            elif raw_event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]:
                input_event = self.mouse_handler.process_mouse_event(raw_event)
            
            if input_event:
                input_events.append(input_event)
                self._register_event(input_event)
        
        # Process key repeats
        repeat_events = self.keyboard_handler.update_key_repeat(delta_time)
        for repeat_event in repeat_events:
            input_events.append(repeat_event)
            self._register_event(repeat_event)
        
        # Execute callbacks for actions
        for event in input_events:
            if event.action:
                self._execute_action_callbacks(event.action, event)
        
        return input_events
    
    def register_action_callback(self, action: InputAction, callback: Callable) -> None:
        """Register a callback for a specific input action."""
        if action not in self.action_callbacks:
            self.action_callbacks[action] = []
        
        self.action_callbacks[action].append(callback)
    
    def unregister_action_callback(self, action: InputAction, callback: Callable) -> None:
        """Unregister a callback for a specific input action."""
        if action in self.action_callbacks:
            try:
                self.action_callbacks[action].remove(callback)
            except ValueError:
                pass  # Callback not found
    
    def clear_action_callbacks(self, action: InputAction = None) -> None:
        """Clear callbacks for a specific action or all actions."""
        if action:
            self.action_callbacks.pop(action, None)
        else:
            self.action_callbacks.clear()
    
    def _execute_action_callbacks(self, action: InputAction, event: InputEvent) -> None:
        """Execute all callbacks for a specific action."""
        callbacks = self.action_callbacks.get(action, [])
        
        for callback in callbacks:
            try:
                callback(event)
            except Exception as e:
                if self.debug_mode:
                    print(f"Error executing callback for {action}: {e}")
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse position."""
        return self.mouse_handler.get_mouse_position()
    
    def is_key_pressed(self, key: int) -> bool:
        """Check if a key is currently pressed."""
        return self.keyboard_handler.is_key_pressed(key)
    
    def is_mouse_button_pressed(self, button: int) -> bool:
        """Check if a mouse button is currently pressed."""
        return self.mouse_handler.is_button_pressed(button)
    
    def is_mouse_in_grid(self) -> bool:
        """Check if mouse is currently over the game grid."""
        return self.mouse_handler.is_position_in_grid(self.get_mouse_position())
    
    def is_mouse_in_sidebar(self) -> bool:
        """Check if mouse is currently over the sidebar."""
        return self.mouse_handler.is_position_in_sidebar(self.get_mouse_position())
    
    def set_input_enabled(self, enabled: bool) -> None:
        """Enable or disable input processing."""
        self.input_enabled = enabled
    
    def set_debug_mode(self, debug: bool) -> None:
        """Enable or disable debug mode."""
        self.debug_mode = debug
    
    def add_key_binding(self, key: int, action: InputAction) -> None:
        """Add a keyboard binding."""
        self.keyboard_handler.add_key_binding(key, action)
    
    def remove_key_binding(self, key: int) -> None:
        """Remove a keyboard binding."""
        self.keyboard_handler.remove_key_binding(key)
    
    def add_mouse_binding(self, button: int, action: InputAction) -> None:
        """Add a mouse button binding."""
        self.mouse_handler.add_button_action(button, action)
    
    def remove_mouse_binding(self, button: int) -> None:
        """Remove a mouse button binding."""
        self.mouse_handler.remove_button_action(button)
    
    def get_key_bindings(self) -> Dict[int, InputAction]:
        """Get all current key bindings."""
        return self.keyboard_handler.get_key_bindings()
    
    def get_mouse_bindings(self) -> Dict[int, InputAction]:
        """Get all current mouse button bindings."""
        return self.mouse_handler.button_actions.copy()
    
    def get_input_statistics(self) -> Dict[str, Any]:
        """Get input processing statistics."""
        return {
            'total_events_processed': self.total_events_processed,
            'events_per_type': dict(self.events_per_type),
            'actions_per_type': dict(self.actions_per_type),
            'input_enabled': self.input_enabled,
            'debug_mode': self.debug_mode,
            'active_callbacks': {action.value: len(callbacks) 
                               for action, callbacks in self.action_callbacks.items()}
        }
    
    def reset_statistics(self) -> None:
        """Reset input statistics."""
        self.total_events_processed = 0
        self.events_per_type.clear()
        self.actions_per_type.clear()
    
    def _register_event(self, event: InputEvent) -> None:
        """Register an event for statistics."""
        self.total_events_processed += 1
        
        # Count by event type
        self.events_per_type[event.event_type] = self.events_per_type.get(event.event_type, 0) + 1
        
        # Count by action type
        if event.action:
            self.actions_per_type[event.action] = self.actions_per_type.get(event.action, 0) + 1
    
    def __repr__(self) -> str:
        """String representation of input manager."""
        return (f"InputManager(enabled={self.input_enabled}, "
                f"events_processed={self.total_events_processed}, "
                f"callbacks={len(self.action_callbacks)})")


class InputHandler:
    """
    High-level input handler that provides game-specific input processing.
    Builds on top of InputManager to provide game logic integration.
    """
    
    def __init__(self):
        """Initialize input handler."""
        self.input_manager = InputManager()
        
        # Game-specific state
        self.selected_block_index = -1
        self.last_rotation_time = 0.0
        self.rotation_cooldown = InputConfig.ROTATION_COOLDOWN
        
        # Keyboard cursor position for grid navigation
        self.cursor_x = 5  # Start in middle of grid
        self.cursor_y = 5
        self.cursor_visible = False
        
        # Input context
        self.context_stack: List[str] = ['game']  # Current input context
        
        # Register default callbacks
        self._setup_default_callbacks()
    
    def _setup_default_callbacks(self) -> None:
        """Setup default input callbacks for the game."""
        # These will be connected to the actual game logic later
        pass
    
    def process_game_input(self, delta_time: float) -> Dict[str, Any]:
        """Process input and return game actions."""
        current_time = pygame.time.get_ticks() / 1000.0
        input_events = self.input_manager.process_events(delta_time)
        
        game_actions = {
            'quit_requested': False,
            'pause_toggled': False,
            'reset_requested': False,
            'rotate_block': False,
            'selected_block_changed': False,
            'block_placement_requested': False,
            'debug_toggled': False,
            'save_requested': False,
            'load_requested': False,
            'sound_toggled': False,
            'music_toggled': False,
            'mouse_position': self.input_manager.get_mouse_position(),
            'cursor_position': (self.cursor_x, self.cursor_y),
            'cursor_visible': self.cursor_visible,
            'raw_events': input_events
        }
        
        for event in input_events:
            if not event.action:
                continue
            
            if event.action == InputAction.QUIT_GAME:
                game_actions['quit_requested'] = True
            
            elif event.action == InputAction.PAUSE_TOGGLE:
                if event.event_type == InputEventType.KEY_DOWN:
                    game_actions['pause_toggled'] = True
            
            elif event.action == InputAction.RESET_GAME:
                if event.event_type == InputEventType.KEY_DOWN:
                    game_actions['reset_requested'] = True
            
            elif event.action == InputAction.ROTATE_BLOCK:
                if (event.event_type == InputEventType.KEY_DOWN and
                    current_time - self.last_rotation_time >= self.rotation_cooldown):
                    game_actions['rotate_block'] = True
                    self.last_rotation_time = current_time
            
            elif event.action == InputAction.SELECT_BLOCK:
                if event.event_type == InputEventType.MOUSE_DOWN:
                    # Check if click is in sidebar (block selection area) or grid (placement area)
                    from ..config import DisplayConfig
                    mouse_x, mouse_y = event.mouse_position
                    
                    # Calculate sidebar bounds
                    sidebar_left = DisplayConfig.GRID_OFFSET_X + DisplayConfig.GRID_SIZE * DisplayConfig.CELL_SIZE
                    grid_right = DisplayConfig.GRID_OFFSET_X + DisplayConfig.GRID_SIZE * DisplayConfig.CELL_SIZE
                    grid_left = DisplayConfig.GRID_OFFSET_X
                    grid_top = DisplayConfig.GRID_OFFSET_Y
                    grid_bottom = grid_top + DisplayConfig.GRID_SIZE * DisplayConfig.CELL_SIZE
                    
                    if mouse_x >= sidebar_left:
                        # Click in sidebar area - select block
                        game_actions['selected_block_changed'] = True
                    elif (grid_left <= mouse_x <= grid_right and 
                          grid_top <= mouse_y <= grid_bottom):
                        # Click in grid area - place block
                        game_actions['block_placement_requested'] = True
                    # If click is outside both areas, do nothing
            
            elif event.action == InputAction.PLACE_BLOCK:
                if event.event_type == InputEventType.MOUSE_DOWN:
                    game_actions['block_placement_requested'] = True
            
            elif event.action == InputAction.TOGGLE_DEBUG:
                if event.event_type == InputEventType.KEY_DOWN:
                    game_actions['debug_toggled'] = True
            
            elif event.action == InputAction.SAVE_GAME:
                if (event.event_type == InputEventType.KEY_DOWN and
                    'ctrl' in event.modifiers):
                    game_actions['save_requested'] = True
            
            elif event.action == InputAction.LOAD_GAME:
                if (event.event_type == InputEventType.KEY_DOWN and
                    'ctrl' in event.modifiers):
                    game_actions['load_requested'] = True
            
            elif event.action == InputAction.TOGGLE_SOUND:
                if event.event_type == InputEventType.KEY_DOWN:
                    game_actions['sound_toggled'] = True
            
            elif event.action == InputAction.TOGGLE_MUSIC:
                if event.event_type == InputEventType.KEY_DOWN:
                    game_actions['music_toggled'] = True
            
            elif event.action == InputAction.NEXT_BLOCK:
                if event.event_type == InputEventType.KEY_DOWN:
                    game_actions['selected_block_changed'] = True
                    game_actions['block_direction'] = 'next'
            
            elif event.action == InputAction.PREVIOUS_BLOCK:
                if event.event_type == InputEventType.KEY_DOWN:
                    game_actions['selected_block_changed'] = True
                    game_actions['block_direction'] = 'previous'
            
            # New movement actions
            elif event.action == InputAction.MOVE_LEFT:
                if event.event_type == InputEventType.KEY_DOWN:
                    self.cursor_x = max(0, self.cursor_x - 1)
                    self.cursor_visible = True
                    game_actions['cursor_position'] = (self.cursor_x, self.cursor_y)
            
            elif event.action == InputAction.MOVE_RIGHT:
                if event.event_type == InputEventType.KEY_DOWN:
                    from ..config import DisplayConfig
                    self.cursor_x = min(DisplayConfig.GRID_SIZE - 1, self.cursor_x + 1)
                    self.cursor_visible = True
                    game_actions['cursor_position'] = (self.cursor_x, self.cursor_y)
            
            elif event.action == InputAction.MOVE_UP:
                if event.event_type == InputEventType.KEY_DOWN:
                    self.cursor_y = max(0, self.cursor_y - 1)
                    self.cursor_visible = True
                    game_actions['cursor_position'] = (self.cursor_x, self.cursor_y)
            
            elif event.action == InputAction.MOVE_DOWN:
                if event.event_type == InputEventType.KEY_DOWN:
                    from ..config import DisplayConfig
                    self.cursor_y = min(DisplayConfig.GRID_SIZE - 1, self.cursor_y + 1)
                    self.cursor_visible = True
                    game_actions['cursor_position'] = (self.cursor_x, self.cursor_y)
            
            elif event.action == InputAction.CONFIRM_PLACEMENT:
                if event.event_type == InputEventType.KEY_DOWN:
                    self.cursor_visible = True
                    game_actions['block_placement_requested'] = True
                    # Use cursor position for keyboard placement
                    game_actions['placement_position'] = (self.cursor_x, self.cursor_y)
            
            # Number key block selection
            elif event.action == InputAction.SELECT_BLOCK_1:
                if event.event_type == InputEventType.KEY_DOWN:
                    game_actions['number_block_selected'] = 0  # First block (index 0)
                    self.cursor_visible = True  # Show cursor for preview
            
            elif event.action == InputAction.SELECT_BLOCK_2:
                if event.event_type == InputEventType.KEY_DOWN:
                    game_actions['number_block_selected'] = 1  # Second block (index 1)
                    self.cursor_visible = True  # Show cursor for preview
            
            elif event.action == InputAction.SELECT_BLOCK_3:
                if event.event_type == InputEventType.KEY_DOWN:
                    game_actions['number_block_selected'] = 2  # Third block (index 2)
                    self.cursor_visible = True  # Show cursor for preview
        
        return game_actions
    
    def get_cursor_position(self) -> Tuple[int, int]:
        """Get current cursor position."""
        return (self.cursor_x, self.cursor_y)
    
    def is_cursor_visible(self) -> bool:
        """Check if cursor is visible."""
        return self.cursor_visible
    
    def hide_cursor(self) -> None:
        """Hide the cursor."""
        self.cursor_visible = False
    
    def set_cursor_position(self, x: int, y: int) -> None:
        """Set cursor position."""
        from ..config import DisplayConfig
        self.cursor_x = max(0, min(DisplayConfig.GRID_SIZE - 1, x))
        self.cursor_y = max(0, min(DisplayConfig.GRID_SIZE - 1, y))
        self.cursor_visible = True
    
    def push_input_context(self, context: str) -> None:
        """Push a new input context (e.g., 'menu', 'game', 'pause')."""
        self.context_stack.append(context)
    
    def pop_input_context(self) -> Optional[str]:
        """Pop the current input context."""
        if len(self.context_stack) > 1:
            return self.context_stack.pop()
        return None
    
    def get_current_context(self) -> str:
        """Get the current input context."""
        return self.context_stack[-1] if self.context_stack else 'default'
    
    def set_selected_block_index(self, index: int) -> None:
        """Set the currently selected block index."""
        self.selected_block_index = index
    
    def get_selected_block_index(self) -> int:
        """Get the currently selected block index."""
        return self.selected_block_index
    
    def register_callback(self, action: InputAction, callback: Callable) -> None:
        """Register a callback for an input action."""
        self.input_manager.register_action_callback(action, callback)
    
    def unregister_callback(self, action: InputAction, callback: Callable) -> None:
        """Unregister a callback for an input action."""
        self.input_manager.unregister_action_callback(action, callback)
    
    def set_input_enabled(self, enabled: bool) -> None:
        """Enable or disable input processing."""
        self.input_manager.set_input_enabled(enabled)
    
    def get_input_statistics(self) -> Dict[str, Any]:
        """Get comprehensive input statistics."""
        stats = self.input_manager.get_input_statistics()
        stats.update({
            'selected_block_index': self.selected_block_index,
            'current_context': self.get_current_context(),
            'context_stack': self.context_stack.copy(),
            'rotation_cooldown': self.rotation_cooldown
        })
        return stats
    
    def __repr__(self) -> str:
        """String representation of input handler."""
        return (f"InputHandler(context={self.get_current_context()}, "
                f"selected_block={self.selected_block_index})")