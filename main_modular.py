#!/usr/bin/env python3
"""
Block Blast Game - Modular Entry Point
Enterprise-level modular Block Blast game with standardized architecture.

Usage:
    python main_modular.py              # Start the game
    python main_modular.py --demo        # Run demo mode
    python main_modular.py --test        # Test all modules
    python main_modular.py --help        # Show help
"""

import sys
import argparse
import pygame
from typing import Optional

# Import the modular game components
from src import (
    # Configuration
    DisplayConfig,
    ColorPalette,
    GameMode,
    AudioConfig,
    initialize_config,
    validate_configuration,
    
    # Core game logic
    BlockManager,
    GridManager,
    GameStateManager,
    
    # UI components
    RendererManager,
    EffectsManager,
    InputHandler,
    
    # Audio system
    AudioManager,
    SoundType,
    
    # Utilities
    FileManager,
    TimeUtils,
    ValidationUtils,
)


class BlockBlastGame:
    """
    Main game class that orchestrates all modular components.
    Provides the primary game loop and component coordination.
    """
    
    def __init__(self, game_mode: GameMode = GameMode.CLASSIC):
        """Initialize the game with specified mode."""
        self.game_mode = game_mode
        self.is_running = False
        self.is_paused = False
        self.debug_mode = False
        
        # Initialize pygame
        pygame.init()
        
        # Create main display
        self.screen = pygame.display.set_mode(
            (DisplayConfig.WINDOW_WIDTH, DisplayConfig.WINDOW_HEIGHT)
        )
        pygame.display.set_caption("Block Blast - Enterprise Edition")
        
        # Initialize game components
        self._initialize_components()
        
        # Game timing
        self.clock = pygame.time.Clock()
        self.delta_time = 0.0
        
        # Game state
        self.selected_block_index = -1
        self.selected_block = None
        
        print(f"Block Blast initialized in {game_mode.value} mode")
    
    def _initialize_components(self) -> None:
        """Initialize all game components."""
        # Core game managers
        self.block_manager = BlockManager()
        self.grid_manager = GridManager()
        self.game_state_manager = GameStateManager(
            block_manager=self.block_manager,
            grid_manager=self.grid_manager,
            game_mode=self.game_mode
        )
        
        # UI components
        self.renderer_manager = RendererManager(self.screen)
        self.effects_manager = EffectsManager()
        self.input_handler = InputHandler()
        
        # Audio system
        self.audio_manager = AudioManager()
        
        # Utilities
        self.file_manager = FileManager()
        
        # Setup input callbacks
        self._setup_input_callbacks()
        
        # Generate initial blocks
        self.game_state_manager.generate_new_block_set()
    
    def _setup_input_callbacks(self) -> None:
        """Setup input event callbacks."""
        # Register callbacks with the input handler
        pass  # Input callbacks would be set up here in a full implementation
    
    def start_game(self) -> None:
        """Start the main game loop."""
        self.is_running = True
        
        # Play background music
        self.audio_manager.play_music('main_game', fade_in_duration=1.0)
        
        print("Starting Block Blast game loop...")
        
        try:
            self._main_game_loop()
        except KeyboardInterrupt:
            print("\nGame interrupted by user")
        except Exception as e:
            print(f"Game error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self._cleanup()
    
    def _main_game_loop(self) -> None:
        """Main game loop."""
        frame_count = 0
        
        while self.is_running:
            # Calculate delta time
            self.delta_time = self.clock.tick(DisplayConfig.TARGET_FPS) / 1000.0
            frame_count += 1
            
            # Process input
            self._process_input()
            
            # Update game state
            if not self.is_paused:
                self._update_game_state()
            
            # Update effects
            self.effects_manager.update_effects(self.delta_time)
            
            # Render everything
            self._render_frame()
            
            # Update display
            pygame.display.flip()
            
            # Debug info every second
            if self.debug_mode and frame_count % DisplayConfig.TARGET_FPS == 0:
                self._print_debug_info()
    
    def _process_input(self) -> None:
        """Process user input."""
        mouse_position = pygame.mouse.get_pos()
        
        # Update renderer context
        self.renderer_manager.update_context(
            delta_time=self.delta_time,
            mouse_position=mouse_position,
            debug_mode=self.debug_mode
        )
        
        # Process input events
        game_actions = self.input_handler.process_game_input(self.delta_time)
        
        # Handle game actions
        if game_actions['quit_requested']:
            self.is_running = False
        
        if game_actions['pause_toggled']:
            self.is_paused = not self.is_paused
            sound_type = SoundType.PAUSE if self.is_paused else SoundType.UNPAUSE
            self.audio_manager.play_sound_effect(sound_type)
        
        if game_actions['reset_requested']:
            self._reset_game()
        
        if game_actions['debug_toggled']:
            self.debug_mode = not self.debug_mode
            print(f"Debug mode: {'ON' if self.debug_mode else 'OFF'}")
        
        if game_actions['rotate_block'] and self.selected_block:
            self._rotate_selected_block()
        
        if game_actions['selected_block_changed']:
            self._handle_block_selection(mouse_position)
        
        if 'number_block_selected' in game_actions:
            self._handle_number_block_selection(game_actions['number_block_selected'])
        
        if game_actions['block_placement_requested']:
            if 'placement_position' in game_actions:
                # Keyboard placement - use cursor position
                self._handle_block_placement_at_grid_position(game_actions['placement_position'])
            else:
                # Mouse placement - use mouse position
                self._handle_block_placement(mouse_position)
        
        if game_actions['sound_toggled']:
            self.audio_manager.toggle_sound_effects()
        
        if game_actions['music_toggled']:
            self.audio_manager.toggle_music()
    
    def _update_game_state(self) -> None:
        """Update game state."""
        # Update game state manager
        self.game_state_manager.update_game_state(self.delta_time)
        
        # Check for game over
        if self.game_state_manager.is_game_over:
            self.audio_manager.play_sound_effect(SoundType.GAME_OVER)
            self.effects_manager.create_screen_shake(10.0, 1.0)
    
    def _render_frame(self) -> None:
        """Render the current frame."""
        # Apply screen shake if active
        shake_offset = self.effects_manager.get_screen_shake_offset()
        
        if shake_offset != (0, 0):
            # Save current screen and apply shake
            saved_surface = self.screen.copy()
            self.screen.fill(ColorPalette.BLACK)
            self.screen.blit(saved_surface, shake_offset)
        
        # Render complete game state
        self.renderer_manager.render_complete_game_state(
            game_state_manager=self.game_state_manager,
            selected_block_index=self.selected_block_index,
            selected_block=self.selected_block,
            cursor_position=self.input_handler.get_cursor_position(),
            cursor_visible=self.input_handler.is_cursor_visible()
        )
        
        # Render effects
        self.effects_manager.render_effects(self.screen)
    
    def _handle_block_selection(self, mouse_position) -> None:
        """Handle block selection from mouse input."""
        # Get selected block index
        new_index = self.renderer_manager.get_selected_block_index_from_mouse(
            mouse_position, self.game_state_manager.available_blocks
        )
        
        if new_index >= 0 and new_index < len(self.game_state_manager.available_blocks):
            block = self.game_state_manager.available_blocks[new_index]
            if not block.is_used:
                self.selected_block_index = new_index
                self.selected_block = block
                self.audio_manager.play_sound_effect(SoundType.SELECTION)
    
    def _handle_number_block_selection(self, block_index: int) -> None:
        """Handle block selection from number keys (1, 2, 3)."""
        if 0 <= block_index < len(self.game_state_manager.available_blocks):
            block = self.game_state_manager.available_blocks[block_index]
            if not block.is_used:
                self.selected_block_index = block_index
                self.selected_block = block
                self.audio_manager.play_sound_effect(SoundType.SELECTION)
                # Make cursor visible for block preview
                self.input_handler.cursor_visible = True
    
    def _handle_block_placement(self, mouse_position) -> None:
        """Handle block placement from mouse input."""
        if not self.selected_block or self.selected_block.is_used:
            return
        
        # Get grid position
        grid_position = self.renderer_manager.get_grid_position_from_mouse(mouse_position)
        
        if grid_position and self.grid_manager.can_place_block(self.selected_block, grid_position):
            # Calculate the positions that will be filled for effects
            placed_positions = []
            for relative_pos in self.selected_block.get_filled_positions():
                absolute_pos = grid_position + relative_pos
                placed_positions.append(absolute_pos)
            
            # Use GameStateManager to place block (handles scoring and line clearing)
            success = self.game_state_manager.place_block(self.selected_block, grid_position)
            
            if success:
                # Play sound effect
                self.audio_manager.play_sound_effect(SoundType.BLOCK_PLACE)
                
                # Create placement effect
                self.effects_manager.create_block_placement_effect(
                    placed_positions, self.selected_block.color_rgb
                )
                
                # Check if any lines were cleared (for effects)
                if hasattr(self.game_state_manager, '_last_line_clear_score') and self.game_state_manager._last_line_clear_score > 0:
                    # Play sound and effects for line clear
                    self.audio_manager.play_sound_effect(SoundType.LINE_CLEAR)
                    self.effects_manager.create_score_popup(self.game_state_manager._last_line_clear_score, mouse_position)
                    
                    # Check for combo
                    if hasattr(self.game_state_manager, 'get_current_combo'):
                        combo_count = self.game_state_manager.get_current_combo()
                        if combo_count > 1:
                            self.audio_manager.play_sound_effect(SoundType.COMBO)
                            self.effects_manager.create_combo_flash(combo_count)
                
                # Clear selection
                self.selected_block = None
                self.selected_block_index = -1
                
                # Generate new blocks if needed (mouse placement version)
                if all(block.is_used for block in self.game_state_manager.available_blocks):
                    self.game_state_manager.generate_new_block_set()
        else:
            # Invalid placement
            self.audio_manager.play_sound_effect(SoundType.ERROR)
    
    def _handle_block_placement_at_grid_position(self, grid_position) -> None:
        """Handle block placement at a specific grid position (for keyboard input)."""
        if not self.selected_block or self.selected_block.is_used:
            return
        
        # Convert grid position to BlockPosition object
        from src.core.grid_manager import BlockPosition
        block_position = BlockPosition(grid_position[0], grid_position[1])
        
        if self.grid_manager.can_place_block(self.selected_block, block_position):
            # Calculate the positions that will be filled for effects
            placed_positions = []
            for relative_pos in self.selected_block.get_filled_positions():
                absolute_pos = block_position + relative_pos
                placed_positions.append(absolute_pos)
            
            # Use GameStateManager to place block (handles scoring and line clearing)
            success = self.game_state_manager.place_block(self.selected_block, block_position)
            
            if success:
                # Play sound effect
                self.audio_manager.play_sound_effect(SoundType.BLOCK_PLACE)
                
                # Create placement effect
                self.effects_manager.create_block_placement_effect(
                    placed_positions, self.selected_block.color_rgb
                )
                
                # Check if any lines were cleared (for effects)
                if hasattr(self.game_state_manager, '_last_line_clear_score') and self.game_state_manager._last_line_clear_score > 0:
                    # Play sound and effects for line clear
                    self.audio_manager.play_sound_effect(SoundType.LINE_CLEAR)
                    
                    # For keyboard placement, show score popup at cursor position
                    from src.config import DisplayConfig
                    cursor_screen_pos = (
                        DisplayConfig.GRID_OFFSET_X + grid_position[0] * DisplayConfig.CELL_SIZE + DisplayConfig.CELL_SIZE // 2,
                        DisplayConfig.GRID_OFFSET_Y + grid_position[1] * DisplayConfig.CELL_SIZE + DisplayConfig.CELL_SIZE // 2
                    )
                    self.effects_manager.create_score_popup(self.game_state_manager._last_line_clear_score, cursor_screen_pos)
                    
                    # Check for combo
                    if hasattr(self.game_state_manager, 'get_current_combo'):
                        combo_count = self.game_state_manager.get_current_combo()
                        if combo_count > 1:
                            self.audio_manager.play_sound_effect(SoundType.COMBO)
                            self.effects_manager.create_combo_flash(combo_count)
                
                # Clear selection
                self.selected_block = None
                self.selected_block_index = -1
                
                # Generate new blocks if needed (keyboard placement version)
                if all(block.is_used for block in self.game_state_manager.available_blocks):
                    self.game_state_manager.generate_new_block_set()
        else:
            # Invalid placement
            self.audio_manager.play_sound_effect(SoundType.ERROR)
    
    def _rotate_selected_block(self) -> None:
        """Rotate the currently selected block."""
        if self.selected_block and not self.selected_block.is_used:
            self.selected_block.rotate_clockwise()
            self.audio_manager.play_sound_effect(SoundType.ROTATION)
    
    def _reset_game(self) -> None:
        """Reset the game state to start over."""
        self.game_state_manager.restart_game()
    
    def _print_debug_info(self) -> None:
        """Print debug information."""
        stats = self.game_state_manager.get_comprehensive_statistics()
        print(f"Debug - Score: {stats['current_session_score']}, "
              f"Level: {stats['current_level']}, "
              f"Effects: {self.effects_manager.get_active_effects_count()}")
    
    def _cleanup(self) -> None:
        """Clean up resources."""
        print("Cleaning up...")
        self.audio_manager.cleanup()
        pygame.quit()


def run_module_tests() -> bool:
    """Run basic tests of all modules."""
    print("Running module tests...")
    
    try:
        # Test configuration
        print("✓ Testing configuration...")
        assert validate_configuration(), "Configuration validation failed"
        
        # Test core components
        print("✓ Testing core components...")
        block_manager = BlockManager()
        grid_manager = GridManager()
        game_state_manager = GameStateManager(block_manager, grid_manager)
        
        # Test UI components
        print("✓ Testing UI components...")
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        renderer_manager = RendererManager(screen)
        effects_manager = EffectsManager()
        input_handler = InputHandler()
        
        # Test audio system
        print("✓ Testing audio system...")
        audio_manager = AudioManager()
        
        # Test utilities
        print("✓ Testing utilities...")
        file_manager = FileManager()
        
        pygame.quit()
        print("All module tests passed!")
        return True
        
    except Exception as e:
        print(f"Module test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_demo_mode() -> None:
    """Run a demonstration of the game features."""
    print("Running Block Blast demo...")
    
    try:
        game = BlockBlastGame(GameMode.CLASSIC)
        
        # Run for a short time to demonstrate
        pygame.time.set_timer(pygame.USEREVENT + 1, 10000)  # 10 seconds
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.USEREVENT + 1:
                    print("Demo completed!")
                    return
            
            # Basic demo rendering
            game.screen.fill(ColorPalette.BACKGROUND_PRIMARY)
            
            # Render demo text
            font = pygame.font.Font(None, 48)
            text = font.render("Block Blast Demo", True, ColorPalette.TEXT_PRIMARY)
            text_rect = text.get_rect(center=(DisplayConfig.WINDOW_WIDTH // 2, 100))
            game.screen.blit(text, text_rect)
            
            # Show module information
            y_offset = 200
            for i, module in enumerate(['Core', 'UI', 'Audio', 'Utils']):
                module_text = font.render(f"✓ {module} Module Loaded", True, ColorPalette.SCORE_COLOR)
                game.screen.blit(module_text, (100, y_offset + i * 60))
            
            pygame.display.flip()
            pygame.time.Clock().tick(60)
            
    except Exception as e:
        print(f"Demo error: {e}")
    finally:
        pygame.quit()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Block Blast - Enterprise Edition")
    parser.add_argument('--demo', action='store_true', help='Run demo mode')
    parser.add_argument('--test', action='store_true', help='Test all modules')
    parser.add_argument('--mode', choices=['classic', 'timed', 'zen'], 
                       default='classic', help='Game mode')
    
    args = parser.parse_args()
    
    # Initialize configuration
    initialize_config()
    
    if args.test:
        success = run_module_tests()
        sys.exit(0 if success else 1)
    
    if args.demo:
        run_demo_mode()
        return
    
    # Start the game
    try:
        game_mode = GameMode(args.mode)
        game = BlockBlastGame(game_mode)
        game.start_game()
    except KeyboardInterrupt:
        print("\nGame interrupted")
    except Exception as e:
        print(f"Error starting game: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()