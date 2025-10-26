"""
Renderer Manager - Handles all rendering operations with standardized naming.
Provides unified interface for drawing game elements, UI components, and effects.
"""

import pygame
import math
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass

from ..config import (
    DisplayConfig,
    ColorPalette, 
    FontConfig,
    EffectsConfig,
)
from ..core.block_manager import BlockData, BlockPosition
from ..core.grid_manager import GridManager
from ..core.game_state_manager import GameStateManager


@dataclass
class RenderContext:
    """Context information for rendering operations."""
    screen_surface: pygame.Surface
    delta_time: float
    mouse_position: Tuple[int, int]
    current_frame: int = 0
    debug_mode_enabled: bool = False


class GridRenderer:
    """Specialized renderer for the game grid."""
    
    def __init__(self, render_context: RenderContext):
        self.context = render_context
        self._cell_size = DisplayConfig.CELL_SIZE
        self._grid_offset_x = DisplayConfig.GRID_OFFSET_X
        self._grid_offset_y = DisplayConfig.GRID_OFFSET_Y
        self._grid_size = DisplayConfig.GRID_SIZE
    
    def render_grid_background(self) -> None:
        """Render the grid background and borders."""
        # Calculate grid bounds
        grid_width = self._grid_size * self._cell_size
        grid_height = self._grid_size * self._cell_size
        
        # Draw grid background
        grid_rect = pygame.Rect(
            self._grid_offset_x - DisplayConfig.GRID_LINE_WIDTH,
            self._grid_offset_y - DisplayConfig.GRID_LINE_WIDTH,
            grid_width + 2 * DisplayConfig.GRID_LINE_WIDTH,
            grid_height + 2 * DisplayConfig.GRID_LINE_WIDTH
        )
        
        pygame.draw.rect(self.context.screen_surface, ColorPalette.GRAY_DARK, grid_rect)
        pygame.draw.rect(self.context.screen_surface, ColorPalette.BORDER_PRIMARY, grid_rect, 
                        DisplayConfig.GRID_LINE_WIDTH)
    
    def render_grid_cells(self, grid_manager: GridManager) -> None:
        """Render all grid cells with their current state."""
        for row_idx in range(self._grid_size):
            for col_idx in range(self._grid_size):
                position = BlockPosition(col_idx, row_idx)
                cell = grid_manager.get_cell_at_position(position)
                
                cell_rect = pygame.Rect(
                    self._grid_offset_x + col_idx * self._cell_size,
                    self._grid_offset_y + row_idx * self._cell_size,
                    self._cell_size,
                    self._cell_size
                )
                
                if cell.is_empty:
                    # Empty cell
                    pygame.draw.rect(self.context.screen_surface, 
                                   ColorPalette.BACKGROUND_PRIMARY, cell_rect)
                    pygame.draw.rect(self.context.screen_surface, 
                                   ColorPalette.BORDER_SECONDARY, cell_rect, 1)
                else:
                    # Filled cell
                    pygame.draw.rect(self.context.screen_surface, cell.color_rgb, cell_rect)
                    pygame.draw.rect(self.context.screen_surface, 
                                   ColorPalette.BORDER_PRIMARY, cell_rect, 2)
                    
                    # Add highlight effect
                    highlight_rect = pygame.Rect(
                        cell_rect.x + 2, cell_rect.y + 2,
                        cell_rect.width - 4, cell_rect.height - 4
                    )
                    lighter_color = tuple(min(255, c + 30) for c in cell.color_rgb)
                    pygame.draw.rect(self.context.screen_surface, lighter_color, 
                                   highlight_rect, 1)
    
    def render_grid_coordinates(self) -> None:
        """Render grid coordinates for debug mode."""
        if not self.context.debug_mode_enabled:
            return
        
        font = pygame.font.Font(None, FontConfig.FONT_SIZE_TINY)
        
        for row_idx in range(self._grid_size):
            for col_idx in range(self._grid_size):
                coord_text = f"{col_idx},{row_idx}"
                text_surface = font.render(coord_text, FontConfig.TEXT_ANTIALIAS, 
                                         ColorPalette.TEXT_SECONDARY)
                
                text_x = self._grid_offset_x + col_idx * self._cell_size + 2
                text_y = self._grid_offset_y + row_idx * self._cell_size + 2
                
                self.context.screen_surface.blit(text_surface, (text_x, text_y))


class BlockRenderer:
    """Specialized renderer for blocks."""
    
    def __init__(self, render_context: RenderContext):
        self.context = render_context
    
    def render_block(self, block: BlockData, position: Tuple[int, int], 
                    scale: float = 1.0, alpha: int = 255) -> None:
        """Render a block at specified screen position."""
        x, y = position
        cell_size = int(DisplayConfig.BLOCK_PREVIEW_SIZE * scale)
        
        for row_idx, row_data in enumerate(block.shape_matrix):
            for col_idx, cell_value in enumerate(row_data):
                if cell_value == 1:
                    cell_rect = pygame.Rect(
                        x + col_idx * cell_size,
                        y + row_idx * cell_size,
                        cell_size - 1,
                        cell_size - 1
                    )
                    
                    if alpha < 255:
                        # Create surface with alpha for transparency
                        cell_surface = pygame.Surface((cell_rect.width, cell_rect.height))
                        cell_surface.set_alpha(alpha)
                        cell_surface.fill(block.color_rgb)
                        self.context.screen_surface.blit(cell_surface, cell_rect)
                    else:
                        pygame.draw.rect(self.context.screen_surface, block.color_rgb, cell_rect)
                    
                    # Add border
                    pygame.draw.rect(self.context.screen_surface, ColorPalette.BORDER_PRIMARY, 
                                   cell_rect, 1)
    
    def render_block_preview(self, block: BlockData, grid_manager: GridManager, cursor_position: Tuple[int, int] = None, cursor_visible: bool = False) -> None:
        """Render block placement preview on grid."""
        # Use cursor position if available and visible, otherwise use mouse position
        if cursor_visible and cursor_position:
            grid_x, grid_y = cursor_position
            target_position = BlockPosition(grid_x, grid_y)
        else:
            mouse_x, mouse_y = self.context.mouse_position
            
            # Convert mouse position to grid coordinates
            grid_x = (mouse_x - DisplayConfig.GRID_OFFSET_X) // DisplayConfig.CELL_SIZE
            grid_y = (mouse_y - DisplayConfig.GRID_OFFSET_Y) // DisplayConfig.CELL_SIZE
            
            target_position = BlockPosition(grid_x, grid_y)
        
        # Check if placement is valid
        can_place = grid_manager.can_place_block(block, target_position)
        
        # Render preview
        for relative_pos in block.get_filled_positions():
            absolute_pos = target_position + relative_pos
            
            if grid_manager.is_position_valid(absolute_pos):
                preview_rect = pygame.Rect(
                    DisplayConfig.GRID_OFFSET_X + absolute_pos.x * DisplayConfig.CELL_SIZE,
                    DisplayConfig.GRID_OFFSET_Y + absolute_pos.y * DisplayConfig.CELL_SIZE,
                    DisplayConfig.CELL_SIZE,
                    DisplayConfig.CELL_SIZE
                )
                
                # Create preview surface
                preview_surface = pygame.Surface((DisplayConfig.CELL_SIZE, DisplayConfig.CELL_SIZE))
                preview_surface.set_alpha(EffectsConfig.PREVIEW_ALPHA)
                
                if can_place:
                    preview_surface.fill(block.color_rgb)
                else:
                    preview_surface.fill(ColorPalette.ERROR_COLOR)
                
                self.context.screen_surface.blit(preview_surface, preview_rect)
                pygame.draw.rect(self.context.screen_surface, ColorPalette.BORDER_PRIMARY, 
                               preview_rect, 2)
    
    def render_available_blocks(self, blocks: List[BlockData], selected_index: int = -1) -> None:
        """Render available blocks in the sidebar."""
        start_x = DisplayConfig.GRID_OFFSET_X + DisplayConfig.GRID_SIZE * DisplayConfig.CELL_SIZE + DisplayConfig.SIDEBAR_PADDING
        start_y = DisplayConfig.GRID_OFFSET_Y + 50
        
        # Title
        font = pygame.font.Font(None, FontConfig.FONT_SIZE_MEDIUM)
        title_surface = font.render("Available Blocks", FontConfig.TEXT_ANTIALIAS, 
                                  ColorPalette.TEXT_PRIMARY)
        self.context.screen_surface.blit(title_surface, (start_x, start_y - 40))
        
        for i, block in enumerate(blocks):
            if block.is_used:
                continue
            
            block_y = start_y + i * DisplayConfig.BLOCK_PREVIEW_SPACING
            
            # Calculate block dimensions
            max_width = max(len(row) for row in block.shape_matrix) if block.shape_matrix else 1
            max_height = len(block.shape_matrix)
            
            # Background rectangle
            bg_rect = pygame.Rect(
                start_x - 10,
                block_y - 10,
                max_width * DisplayConfig.BLOCK_PREVIEW_SIZE + 20,
                max_height * DisplayConfig.BLOCK_PREVIEW_SIZE + 20
            )
            
            # Highlight if selected
            if i == selected_index:
                pygame.draw.rect(self.context.screen_surface, ColorPalette.HIGHLIGHT_COLOR, 
                               bg_rect, EffectsConfig.SELECTION_HIGHLIGHT_WIDTH)
                # Add glow effect
                glow_rect = bg_rect.inflate(8, 8)
                glow_surface = pygame.Surface((glow_rect.width, glow_rect.height))
                glow_surface.set_alpha(50)
                glow_surface.fill(ColorPalette.HIGHLIGHT_COLOR)
                self.context.screen_surface.blit(glow_surface, glow_rect)
            else:
                pygame.draw.rect(self.context.screen_surface, ColorPalette.BORDER_SECONDARY, 
                               bg_rect, 2)
            
            # Fill background
            pygame.draw.rect(self.context.screen_surface, ColorPalette.BACKGROUND_PRIMARY, bg_rect)
            
            # Render the block
            self.render_block(block, (start_x, block_y))
            
            # Add number label (1, 2, 3) near the block
            number_font = pygame.font.Font(None, FontConfig.FONT_SIZE_MEDIUM)
            number_text = str(i + 1)
            number_surface = number_font.render(number_text, FontConfig.TEXT_ANTIALIAS, 
                                              ColorPalette.TEXT_PRIMARY)
            number_bg_rect = pygame.Rect(
                start_x - 35, 
                block_y,
                25, 25
            )
            # Draw number background circle
            pygame.draw.circle(self.context.screen_surface, ColorPalette.BACKGROUND_SECONDARY,
                             (start_x - 22, block_y + 12), 15)
            pygame.draw.circle(self.context.screen_surface, ColorPalette.BORDER_PRIMARY,
                             (start_x - 22, block_y + 12), 15, 2)
            # Center the number text in the circle
            number_rect = number_surface.get_rect(center=(start_x - 22, block_y + 12))
            self.context.screen_surface.blit(number_surface, number_rect)
            
            # Add rotation hint for selected block
            if i == selected_index:
                hint_font = pygame.font.Font(None, FontConfig.FONT_SIZE_TINY)
                hint_surface = hint_font.render("B: Rotate", FontConfig.TEXT_ANTIALIAS, 
                                              ColorPalette.TEXT_SECONDARY)
                hint_y = block_y + max_height * DisplayConfig.BLOCK_PREVIEW_SIZE + 5
                self.context.screen_surface.blit(hint_surface, (start_x, hint_y))
    
    def render_next_blocks_preview(self, blocks: List[BlockData]) -> None:
        """Render preview of next blocks."""
        start_x = DisplayConfig.GRID_OFFSET_X + DisplayConfig.GRID_SIZE * DisplayConfig.CELL_SIZE + DisplayConfig.SIDEBAR_PADDING
        start_y = DisplayConfig.GRID_OFFSET_Y + 400
        
        # Title
        font = pygame.font.Font(None, FontConfig.FONT_SIZE_SMALL)
        title_surface = font.render("Next Blocks", FontConfig.TEXT_ANTIALIAS, 
                                  ColorPalette.TEXT_SECONDARY)
        self.context.screen_surface.blit(title_surface, (start_x, start_y - 25))
        
        for i, block in enumerate(blocks[:3]):
            block_x = start_x + i * 80
            
            # Small background
            bg_rect = pygame.Rect(block_x - 5, start_y - 5, 70, 70)
            pygame.draw.rect(self.context.screen_surface, ColorPalette.BORDER_SECONDARY, bg_rect, 1)
            pygame.draw.rect(self.context.screen_surface, ColorPalette.BACKGROUND_PRIMARY, bg_rect)
            
            # Render small block
            self.render_block(block, (block_x, start_y), scale=0.5, alpha=150)


class UIRenderer:
    """Renders UI elements and game information."""
    
    def __init__(self, render_context: RenderContext):
        self.context = render_context
        self._font_large = pygame.font.Font(None, FontConfig.FONT_SIZE_LARGE)
        self._font_medium = pygame.font.Font(None, FontConfig.FONT_SIZE_MEDIUM)
        self._font_small = pygame.font.Font(None, FontConfig.FONT_SIZE_SMALL)
        self._font_tiny = pygame.font.Font(None, FontConfig.FONT_SIZE_TINY)
    
    def render_game_statistics(self, game_state_manager: GameStateManager) -> None:
        """Render game statistics and information."""
        stats = game_state_manager.get_comprehensive_statistics()
        
        # Main stats panel
        panel_x = DisplayConfig.SIDEBAR_PADDING
        panel_y = DisplayConfig.SIDEBAR_PADDING
        
        # Score
        score_text = self._font_large.render(f"Score: {stats['current_session_score']:,}", 
                                           FontConfig.TEXT_ANTIALIAS, ColorPalette.TEXT_PRIMARY)
        self.context.screen_surface.blit(score_text, (panel_x, panel_y))
        
        # High score
        high_score_text = self._font_medium.render(f"High: {stats['highest_score']:,}", 
                                                 FontConfig.TEXT_ANTIALIAS, ColorPalette.TEXT_SECONDARY)
        self.context.screen_surface.blit(high_score_text, (panel_x, panel_y + 50))
        
        # Level and lines
        level_text = self._font_medium.render(f"Level: {stats['current_level']}", 
                                            FontConfig.TEXT_ANTIALIAS, ColorPalette.TEXT_PRIMARY)
        self.context.screen_surface.blit(level_text, (panel_x + 200, panel_y))
        
        lines_text = self._font_medium.render(f"Lines: {stats['lines_cleared_total']}", 
                                            FontConfig.TEXT_ANTIALIAS, ColorPalette.TEXT_PRIMARY)
        self.context.screen_surface.blit(lines_text, (panel_x + 200, panel_y + 30))
        
        # Game mode
        mode_text = self._font_small.render(f"Mode: {stats['current_mode'].title()}", 
                                          FontConfig.TEXT_ANTIALIAS, ColorPalette.TEXT_SECONDARY)
        self.context.screen_surface.blit(mode_text, (panel_x + 350, panel_y))
        
        # Timer for timed mode
        if game_state_manager.current_mode.value == 'timed':
            time_remaining = max(0, stats['time_remaining'])
            minutes = int(time_remaining // 60)
            seconds = int(time_remaining % 60)
            
            color = ColorPalette.ERROR_COLOR if time_remaining < 30 else ColorPalette.TEXT_PRIMARY
            timer_text = self._font_medium.render(f"Time: {minutes:02d}:{seconds:02d}", 
                                                FontConfig.TEXT_ANTIALIAS, color)
            self.context.screen_surface.blit(timer_text, (panel_x + 350, panel_y + 25))
        
        # Combo counter
        if stats['current_combo_count'] > 1:
            combo_text = self._font_medium.render(f"Combo x{stats['current_combo_count']}!", 
                                                FontConfig.TEXT_ANTIALIAS, ColorPalette.WARNING_COLOR)
            combo_rect = combo_text.get_rect(center=(DisplayConfig.WINDOW_WIDTH // 2, 80))
            
            # Background
            bg_rect = combo_rect.inflate(20, 10)
            pygame.draw.rect(self.context.screen_surface, ColorPalette.BACKGROUND_PRIMARY, bg_rect)
            pygame.draw.rect(self.context.screen_surface, ColorPalette.WARNING_COLOR, bg_rect, 2)
            
            self.context.screen_surface.blit(combo_text, combo_rect)
    
    def render_control_help(self) -> None:
        """Render control instructions."""
        help_y = DisplayConfig.WINDOW_HEIGHT - 120
        panel_x = DisplayConfig.SIDEBAR_PADDING
        
        help_texts = [
            "Click block to select",
            "Click grid to place", 
            "R: Rotate block",
            "P: Pause",
            "ESC: Quit"
        ]
        
        for i, text in enumerate(help_texts):
            help_surface = self._font_tiny.render(text, FontConfig.TEXT_ANTIALIAS, 
                                                 ColorPalette.TEXT_SECONDARY)
            self.context.screen_surface.blit(help_surface, (panel_x, help_y + i * 20))
    
    def render_debug_information(self, game_state_manager: GameStateManager) -> None:
        """Render debug information if enabled."""
        if not self.context.debug_mode_enabled:
            return
        
        debug_y = 10
        debug_x = DisplayConfig.WINDOW_WIDTH - 200
        
        debug_info = [
            f"FPS: {pygame.time.Clock().get_fps():.1f}",
            f"Frame: {self.context.current_frame}",
            f"Mouse: {self.context.mouse_position}",
            f"Session: {game_state_manager.session_duration:.1f}s",
            f"Mode: {game_state_manager.current_mode.value}",
        ]
        
        for i, info in enumerate(debug_info):
            debug_surface = self._font_tiny.render(info, FontConfig.TEXT_ANTIALIAS, 
                                                  ColorPalette.TEXT_PRIMARY)
            self.context.screen_surface.blit(debug_surface, (debug_x, debug_y + i * 20))
    
    def render_game_over_overlay(self, game_state_manager: GameStateManager) -> None:
        """Render game over overlay."""
        # Semi-transparent overlay
        overlay_surface = pygame.Surface((DisplayConfig.WINDOW_WIDTH, DisplayConfig.WINDOW_HEIGHT))
        overlay_surface.set_alpha(128)
        overlay_surface.fill(ColorPalette.BLACK)
        self.context.screen_surface.blit(overlay_surface, (0, 0))
        
        # Game over text
        game_over_text = self._font_large.render("GAME OVER", FontConfig.TEXT_ANTIALIAS, 
                                                ColorPalette.ERROR_COLOR)
        game_over_rect = game_over_text.get_rect(center=(DisplayConfig.WINDOW_WIDTH // 2, 
                                                        DisplayConfig.WINDOW_HEIGHT // 2 - 60))
        
        # Background for text
        bg_rect = game_over_rect.inflate(40, 20)
        pygame.draw.rect(self.context.screen_surface, ColorPalette.BACKGROUND_PRIMARY, bg_rect)
        pygame.draw.rect(self.context.screen_surface, ColorPalette.ERROR_COLOR, bg_rect, 3)
        
        self.context.screen_surface.blit(game_over_text, game_over_rect)
        
        # Final score
        stats = game_state_manager.get_comprehensive_statistics()
        score_text = self._font_medium.render(f"Final Score: {stats['current_session_score']:,}", 
                                            FontConfig.TEXT_ANTIALIAS, ColorPalette.TEXT_PRIMARY)
        score_rect = score_text.get_rect(center=(DisplayConfig.WINDOW_WIDTH // 2, 
                                                DisplayConfig.WINDOW_HEIGHT // 2 - 20))
        self.context.screen_surface.blit(score_text, score_rect)
        
        # High score check
        if stats['current_session_score'] == stats['highest_score'] and stats['current_session_score'] > 0:
            new_high_text = self._font_medium.render("NEW HIGH SCORE!", FontConfig.TEXT_ANTIALIAS, 
                                                   ColorPalette.WARNING_COLOR)
            new_high_rect = new_high_text.get_rect(center=(DisplayConfig.WINDOW_WIDTH // 2, 
                                                          DisplayConfig.WINDOW_HEIGHT // 2 + 10))
            self.context.screen_surface.blit(new_high_text, new_high_rect)
        
        # Restart instructions
        restart_text = self._font_small.render("Press R to restart or ESC to quit", 
                                             FontConfig.TEXT_ANTIALIAS, ColorPalette.TEXT_PRIMARY)
        restart_rect = restart_text.get_rect(center=(DisplayConfig.WINDOW_WIDTH // 2, 
                                                    DisplayConfig.WINDOW_HEIGHT // 2 + 50))
        self.context.screen_surface.blit(restart_text, restart_rect)
    
    def render_pause_overlay(self) -> None:
        """Render pause overlay."""
        # Semi-transparent overlay
        overlay_surface = pygame.Surface((DisplayConfig.WINDOW_WIDTH, DisplayConfig.WINDOW_HEIGHT))
        overlay_surface.set_alpha(100)
        overlay_surface.fill(ColorPalette.GRAY_DARK)
        self.context.screen_surface.blit(overlay_surface, (0, 0))
        
        # Pause text
        pause_text = self._font_large.render("PAUSED", FontConfig.TEXT_ANTIALIAS, 
                                           ColorPalette.BACKGROUND_PRIMARY)
        pause_rect = pause_text.get_rect(center=(DisplayConfig.WINDOW_WIDTH // 2, 
                                                DisplayConfig.WINDOW_HEIGHT // 2))
        
        # Background
        bg_rect = pause_rect.inflate(40, 20)
        pygame.draw.rect(self.context.screen_surface, ColorPalette.BLACK, bg_rect)
        pygame.draw.rect(self.context.screen_surface, ColorPalette.BACKGROUND_PRIMARY, bg_rect, 2)
        
        self.context.screen_surface.blit(pause_text, pause_rect)
        
        # Instructions
        instruction_text = self._font_small.render("Press P to resume", FontConfig.TEXT_ANTIALIAS, 
                                                 ColorPalette.GRAY_LIGHT)
        instruction_rect = instruction_text.get_rect(center=(DisplayConfig.WINDOW_WIDTH // 2, 
                                                           DisplayConfig.WINDOW_HEIGHT // 2 + 40))
        self.context.screen_surface.blit(instruction_text, instruction_rect)


class RendererManager:
    """
    Main renderer manager that coordinates all rendering operations.
    Provides unified interface for all visual elements.
    """
    
    def __init__(self, screen_surface: pygame.Surface):
        """Initialize renderer manager."""
        self.screen_surface = screen_surface
        self.render_context = RenderContext(
            screen_surface=screen_surface,
            delta_time=0.0,
            mouse_position=(0, 0),
            current_frame=0,
            debug_mode_enabled=False
        )
        
        # Specialized renderers
        self.grid_renderer = GridRenderer(self.render_context)
        self.block_renderer = BlockRenderer(self.render_context)
        self.ui_renderer = UIRenderer(self.render_context)
        
        # Frame counting
        self._frame_counter = 0
    
    def update_context(self, delta_time: float, mouse_position: Tuple[int, int], 
                      debug_mode: bool = False) -> None:
        """Update rendering context with current frame information."""
        self.render_context.delta_time = delta_time
        self.render_context.mouse_position = mouse_position
        self.render_context.debug_mode_enabled = debug_mode
        self.render_context.current_frame = self._frame_counter
        self._frame_counter += 1
    
    def clear_screen(self, color: Tuple[int, int, int] = None) -> None:
        """Clear the screen with specified color."""
        clear_color = color or ColorPalette.BACKGROUND_PRIMARY
        self.screen_surface.fill(clear_color)
    
    def render_complete_game_state(self, game_state_manager: GameStateManager, 
                                 selected_block_index: int = -1,
                                 selected_block: BlockData = None,
                                 cursor_position: Tuple[int, int] = None,
                                 cursor_visible: bool = False) -> None:
        """Render the complete game state including all UI elements."""
        # Clear screen
        self.clear_screen()
        
        # Render grid
        self.grid_renderer.render_grid_background()
        self.grid_renderer.render_grid_cells(game_state_manager.grid_manager)
        
        if self.render_context.debug_mode_enabled:
            self.grid_renderer.render_grid_coordinates()
        
        # Render available blocks
        self.block_renderer.render_available_blocks(
            game_state_manager.available_blocks, 
            selected_block_index
        )
        
        # Render next blocks preview
        self.block_renderer.render_next_blocks_preview(
            game_state_manager.next_blocks_preview
        )
        
        # Render block preview if one is selected
        if selected_block and not game_state_manager.is_game_over and not game_state_manager.is_paused:
            self.block_renderer.render_block_preview(
                selected_block, 
                game_state_manager.grid_manager, 
                cursor_position, 
                cursor_visible
            )
        
        # Render UI elements
        self.ui_renderer.render_game_statistics(game_state_manager)
        self.ui_renderer.render_control_help()
        
        if self.render_context.debug_mode_enabled:
            self.ui_renderer.render_debug_information(game_state_manager)
        
        # Render cursor if visible
        if cursor_visible and cursor_position:
            self._render_cursor(cursor_position)
        
        # Render overlays
        if game_state_manager.is_game_over:
            self.ui_renderer.render_game_over_overlay(game_state_manager)
        elif game_state_manager.is_paused:
            self.ui_renderer.render_pause_overlay()
    
    def _render_cursor(self, cursor_position: Tuple[int, int]) -> None:
        """Render keyboard cursor on the grid."""
        x, y = cursor_position
        
        # Calculate screen position
        screen_x = DisplayConfig.GRID_OFFSET_X + x * DisplayConfig.CELL_SIZE
        screen_y = DisplayConfig.GRID_OFFSET_Y + y * DisplayConfig.CELL_SIZE
        
        # Draw cursor outline
        cursor_rect = pygame.Rect(screen_x, screen_y, DisplayConfig.CELL_SIZE, DisplayConfig.CELL_SIZE)
        pygame.draw.rect(self.render_context.screen_surface, ColorPalette.HIGHLIGHT_COLOR, cursor_rect, 3)
        
        # Draw corner markers for better visibility
        corner_size = 8
        corners = [
            (screen_x, screen_y),  # Top-left
            (screen_x + DisplayConfig.CELL_SIZE - corner_size, screen_y),  # Top-right
            (screen_x, screen_y + DisplayConfig.CELL_SIZE - corner_size),  # Bottom-left
            (screen_x + DisplayConfig.CELL_SIZE - corner_size, screen_y + DisplayConfig.CELL_SIZE - corner_size)  # Bottom-right
        ]
        
        for corner_x, corner_y in corners:
            corner_rect = pygame.Rect(corner_x, corner_y, corner_size, corner_size)
            pygame.draw.rect(self.render_context.screen_surface, ColorPalette.WHITE, corner_rect)
    
    def get_grid_position_from_mouse(self, mouse_position: Tuple[int, int]) -> Optional[BlockPosition]:
        """Convert mouse position to grid coordinates."""
        mouse_x, mouse_y = mouse_position
        
        grid_x = (mouse_x - DisplayConfig.GRID_OFFSET_X) // DisplayConfig.CELL_SIZE
        grid_y = (mouse_y - DisplayConfig.GRID_OFFSET_Y) // DisplayConfig.CELL_SIZE
        
        if (0 <= grid_x < DisplayConfig.GRID_SIZE and 
            0 <= grid_y < DisplayConfig.GRID_SIZE):
            return BlockPosition(grid_x, grid_y)
        
        return None
    
    def get_selected_block_index_from_mouse(self, mouse_position: Tuple[int, int], 
                                          available_blocks: List[BlockData]) -> int:
        """Get block index from mouse position in sidebar."""
        mouse_x, mouse_y = mouse_position
        
        start_x = (DisplayConfig.GRID_OFFSET_X + DisplayConfig.GRID_SIZE * 
                  DisplayConfig.CELL_SIZE + DisplayConfig.SIDEBAR_PADDING)
        start_y = DisplayConfig.GRID_OFFSET_Y + 50
        
        for i, block in enumerate(available_blocks):
            if block.is_used:
                continue
            
            block_y = start_y + i * DisplayConfig.BLOCK_PREVIEW_SPACING
            max_width = max(len(row) for row in block.shape_matrix) if block.shape_matrix else 1
            max_height = len(block.shape_matrix)
            
            if (start_x <= mouse_x <= start_x + max_width * DisplayConfig.BLOCK_PREVIEW_SIZE and
                block_y <= mouse_y <= block_y + max_height * DisplayConfig.BLOCK_PREVIEW_SIZE):
                return i
        
        return -1
    
    def __repr__(self) -> str:
        """String representation of renderer manager."""
        return (f"RendererManager(frame={self._frame_counter}, "
                f"debug={self.render_context.debug_mode_enabled})")