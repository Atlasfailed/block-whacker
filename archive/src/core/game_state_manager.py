"""
Game State Manager - Handles all game state operations with standardized naming.
Manages game modes, scoring, statistics, save/load functionality, and game flow.
"""

import time
import json
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path

from ..config import (
    GameMode, 
    GameRules, 
    FileConfig,
    DisplayConfig,
)
from .block_manager import BlockManager, BlockData
from .grid_manager import GridManager, LineClearResult


@dataclass
class GameStatistics:
    """Comprehensive game statistics tracking."""
    total_score: int = 0
    highest_score: int = 0
    current_level: int = 1
    lines_cleared_total: int = 0
    blocks_placed_total: int = 0
    games_played_total: int = 0
    time_played_seconds: float = 0.0
    perfect_clears_count: int = 0
    max_combo_achieved: int = 0
    
    # Performance metrics
    blocks_per_minute: float = 0.0
    average_score_per_game: float = 0.0
    best_time_to_target: float = 0.0
    
    # Current session
    session_start_time: float = field(default_factory=time.time)
    current_combo_count: int = 0
    
    def update_performance_metrics(self, time_played: float) -> None:
        """Update calculated performance metrics."""
        if time_played > 0:
            self.blocks_per_minute = (self.blocks_placed_total / time_played) * 60
        
        if self.games_played_total > 0:
            self.average_score_per_game = self.total_score / self.games_played_total


@dataclass
class GameSession:
    """Represents a single game session."""
    session_id: str
    game_mode: GameMode
    start_time: float
    end_time: Optional[float] = None
    final_score: int = 0
    lines_cleared: int = 0
    blocks_placed: int = 0
    duration_seconds: float = 0.0
    completed_successfully: bool = False


class GameStateManager:
    """
    Manages comprehensive game state including modes, scoring, and persistence.
    Provides high-level interface for all game state operations.
    """
    
    def __init__(self, block_manager: 'BlockManager' = None, 
                 grid_manager: 'GridManager' = None,
                 game_mode: GameMode = GameMode.CLASSIC):
        """Initialize game state manager."""
        self._current_mode = game_mode
        self._game_statistics = GameStatistics()
        self._is_game_over = False
        self._is_paused = False
        self._game_session_active = False
        
        # Store references to passed managers (if provided)
        if block_manager is not None:
            self._external_block_manager = block_manager
        if grid_manager is not None:
            self._external_grid_manager = grid_manager
        
        # Game timing
        self._session_start_time = time.time()
        self._pause_start_time = 0.0
        self._total_pause_time = 0.0
        self._time_remaining = 0.0
        
        # Game components
        self._block_manager = BlockManager()
        self._grid_manager = GridManager()
        self._available_blocks: List[BlockData] = []
        self._next_blocks_preview: List[BlockData] = []
        
        # Score calculation
        self._score_this_session = 0
        self._last_line_clear_score = 0
        self._consecutive_perfect_clears = 0
        
        # Initialize game state
        self._initialize_new_game()
        
        # Load persistent data
        self._load_high_scores()
    
    # ==========================================================================
    # PROPERTIES
    # ==========================================================================
    
    @property
    def current_mode(self) -> GameMode:
        """Get current game mode."""
        return self._current_mode
    
    @property
    def is_game_over(self) -> bool:
        """Check if game is over."""
        return self._is_game_over
    
    @property
    def is_paused(self) -> bool:
        """Check if game is paused."""
        return self._is_paused
    
    @property
    def current_score(self) -> int:
        """Get current session score."""
        return self._score_this_session
    
    @property
    def high_score(self) -> int:
        """Get high score for current mode."""
        return self._game_statistics.highest_score
    
    @property
    def current_level(self) -> int:
        """Get current level."""
        return self._game_statistics.current_level
    
    @property
    def grid_manager(self) -> GridManager:
        """Get grid manager instance."""
        return getattr(self, '_external_grid_manager', self._grid_manager)
    
    @property
    def block_manager(self) -> 'BlockManager':
        """Get block manager instance."""
        return getattr(self, '_external_block_manager', self._block_manager)
    
    @property
    def available_blocks(self) -> List[BlockData]:
        """Get currently available blocks."""
        return self._available_blocks
    
    @property
    def next_blocks_preview(self) -> List[BlockData]:
        """Get preview of next blocks."""
        return self._next_blocks_preview
    
    @property
    def time_remaining(self) -> float:
        """Get time remaining (for timed modes)."""
        return max(0.0, self._time_remaining)
    
    @property
    def session_duration(self) -> float:
        """Get current session duration in seconds."""
        if not self._game_session_active:
            return 0.0
        
        current_time = time.time()
        elapsed_time = current_time - self._session_start_time - self._total_pause_time
        
        if self._is_paused:
            elapsed_time -= (current_time - self._pause_start_time)
        
        return elapsed_time
    
    # ==========================================================================
    # GAME FLOW CONTROL
    # ==========================================================================
    
    def start_new_game(self, game_mode: GameMode = None) -> None:
        """Start a new game with optional mode change."""
        if game_mode and game_mode != self._current_mode:
            self._current_mode = game_mode
        
        self._initialize_new_game()
        self._game_session_active = True
        
        print(f"Started new {self._current_mode.value} game")
    
    def pause_game(self) -> None:
        """Pause the current game."""
        if not self._is_paused and not self._is_game_over:
            self._is_paused = True
            self._pause_start_time = time.time()
    
    def resume_game(self) -> None:
        """Resume the paused game."""
        if self._is_paused:
            self._is_paused = False
            pause_duration = time.time() - self._pause_start_time
            self._total_pause_time += pause_duration
            self._pause_start_time = 0.0
    
    def toggle_pause(self) -> bool:
        """Toggle pause state and return new state."""
        if self._is_paused:
            self.resume_game()
        else:
            self.pause_game()
        return self._is_paused
    
    def end_game(self, completed_successfully: bool = False) -> GameSession:
        """End the current game and return session data."""
        self._is_game_over = True
        self._game_session_active = False
        
        # Create session record
        session = GameSession(
            session_id=f"session_{int(time.time())}",
            game_mode=self._current_mode,
            start_time=self._session_start_time,
            end_time=time.time(),
            final_score=self._score_this_session,
            lines_cleared=self._game_statistics.lines_cleared_total,
            blocks_placed=self._game_statistics.blocks_placed_total,
            duration_seconds=self.session_duration,
            completed_successfully=completed_successfully
        )
        
        # Update statistics
        self._update_final_statistics(session)
        
        # Save high score if achieved
        if self._score_this_session > self._game_statistics.highest_score:
            self._game_statistics.highest_score = self._score_this_session
            self._save_high_scores()
        
        return session
    
    def restart_game(self) -> None:
        """Restart the current game."""
        current_mode = self._current_mode
        self.start_new_game(current_mode)
    
    # ==========================================================================
    # BLOCK AND GRID OPERATIONS
    # ==========================================================================
    
    def place_block(self, block: BlockData, target_position) -> bool:
        """
        Place a block on the grid and handle all associated game logic.
        
        Returns:
            True if placement successful, False otherwise
        """
        if not self.grid_manager.place_block(block, target_position):
            return False
        
        # Mark the block as used
        block.mark_as_used()
        
        # Update statistics
        self._game_statistics.blocks_placed_total += 1
        
        # Clear completed lines and award points only for line clears
        line_clear_result = self.grid_manager.clear_completed_lines()
        if line_clear_result.lines_cleared_count > 0:
            line_score = self._calculate_line_clear_score(line_clear_result)
            self._score_this_session += line_score
            self._last_line_clear_score = line_score
            
            # Update statistics
            self._game_statistics.lines_cleared_total += line_clear_result.lines_cleared_count
            self._game_statistics.current_combo_count = line_clear_result.combo_multiplier
            
            if line_clear_result.combo_multiplier > self._game_statistics.max_combo_achieved:
                self._game_statistics.max_combo_achieved = line_clear_result.combo_multiplier
        else:
            # No lines cleared, reset the last line clear score
            self._last_line_clear_score = 0
        
        # Check for perfect clear
        if self.grid_manager.is_grid_empty():
            perfect_clear_bonus = GameRules.SCORE_PERFECT_CLEAR
            self._score_this_session += perfect_clear_bonus
            self._game_statistics.perfect_clears_count += 1
            self._consecutive_perfect_clears += 1
        else:
            self._consecutive_perfect_clears = 0
        
        # Generate new blocks if all used
        if all(block.is_used for block in self._available_blocks):
            self._generate_new_available_blocks()
            
            # Bonus for using all blocks
            all_blocks_bonus = GameRules.SCORE_ALL_BLOCKS_BONUS
            self._score_this_session += all_blocks_bonus
        
        # Update level
        self._update_level()
        
        # Check for game over
        self._check_game_over_conditions()
        
        return True
    
    def can_place_any_available_block(self) -> bool:
        """Check if any available block can be placed."""
        return self.block_manager.can_place_any_block(
            self._available_blocks,
            list(self.grid_manager.get_filled_positions()),
            self.grid_manager.grid_dimensions
        )
    
    def generate_new_block_set(self) -> None:
        """Generate a new set of available blocks."""
        self._generate_new_available_blocks()
    
    # ==========================================================================
    # SCORING SYSTEM
    # ==========================================================================
    
    def _calculate_line_clear_score(self, result: LineClearResult) -> int:
        """Calculate score for line clearing with progressive bonuses."""
        if result.lines_cleared_count == 0:
            return 0
        
        # Progressive scoring: 1 line = 100, 2 lines = 300, 3 lines = 600, etc.
        if result.lines_cleared_count == 1:
            base_score = GameRules.SCORE_LINE_BASE  # 100
        elif result.lines_cleared_count == 2:
            base_score = GameRules.SCORE_LINE_BASE * 3  # 300
        elif result.lines_cleared_count == 3:
            base_score = GameRules.SCORE_LINE_BASE * 6  # 600
        elif result.lines_cleared_count == 4:
            base_score = GameRules.SCORE_LINE_BASE * 10  # 1000
        else:
            # For 5+ lines (rare), exponential increase
            base_score = GameRules.SCORE_LINE_BASE * (result.lines_cleared_count ** 2)
        
        # Combo bonus
        combo_bonus = result.combo_multiplier * GameRules.SCORE_COMBO_BONUS
        
        # Level bonus
        level_bonus = int(base_score * (self._game_statistics.current_level - 1) * 0.1)
        
        # Perfect clear streak bonus
        streak_bonus = self._consecutive_perfect_clears * 500
        
        total_score = base_score + combo_bonus + level_bonus + streak_bonus
        return max(total_score, 0)
    
    def _update_level(self) -> None:
        """Update current level based on lines cleared."""
        if GameRules.DIFFICULTY_SCALING_ENABLED:
            new_level = 1 + (self._game_statistics.lines_cleared_total // GameRules.LINES_PER_LEVEL)
            self._game_statistics.current_level = min(new_level, GameRules.MAX_LEVEL)
    
    # ==========================================================================
    # GAME STATE PERSISTENCE
    # ==========================================================================
    
    def save_game_state(self) -> bool:
        """Save current game state to file."""
        try:
            save_data = {
                'version': '2.0',
                'mode': self._current_mode.value,
                'score': self._score_this_session,
                'statistics': asdict(self._game_statistics),
                'grid_data': self._serialize_grid(),
                'available_blocks': [self._serialize_block(block) for block in self._available_blocks],
                'next_blocks': [self._serialize_block(block) for block in self._next_blocks_preview],
                'session_data': {
                    'start_time': self._session_start_time,
                    'total_pause_time': self._total_pause_time,
                    'time_remaining': self._time_remaining,
                },
                'metadata': {
                    'save_time': time.time(),
                    'game_over': self._is_game_over,
                    'paused': self._is_paused,
                }
            }
            
            save_path = FileConfig.SAVES_DIR / FileConfig.SAVE_GAME_FILE
            FileConfig.ensure_directories_exist()
            
            with open(save_path, 'w') as file:
                json.dump(save_data, file, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving game state: {e}")
            return False
    
    def load_game_state(self) -> bool:
        """Load game state from file."""
        try:
            save_path = FileConfig.SAVES_DIR / FileConfig.SAVE_GAME_FILE
            
            if not save_path.exists():
                return False
            
            with open(save_path, 'r') as file:
                save_data = json.load(file)
            
            # Validate save data version
            if save_data.get('version') != '2.0':
                print("Save file version mismatch")
                return False
            
            # Restore game state
            self._current_mode = GameMode(save_data['mode'])
            self._score_this_session = save_data['score']
            
            # Restore statistics
            stats_data = save_data['statistics']
            for key, value in stats_data.items():
                if hasattr(self._game_statistics, key):
                    setattr(self._game_statistics, key, value)
            
            # Restore grid
            self._deserialize_grid(save_data['grid_data'])
            
            # Restore blocks
            self._available_blocks = [
                self._deserialize_block(block_data) 
                for block_data in save_data['available_blocks']
            ]
            self._next_blocks_preview = [
                self._deserialize_block(block_data) 
                for block_data in save_data['next_blocks']
            ]
            
            # Restore session data
            session_data = save_data['session_data']
            self._session_start_time = session_data['start_time']
            self._total_pause_time = session_data['total_pause_time']
            self._time_remaining = session_data['time_remaining']
            
            # Restore metadata
            metadata = save_data['metadata']
            self._is_game_over = metadata['game_over']
            self._is_paused = metadata['paused']
            
            return True
            
        except Exception as e:
            print(f"Error loading game state: {e}")
            return False
    
    def _save_high_scores(self) -> None:
        """Save high scores to persistent storage."""
        try:
            scores_path = FileConfig.DATA_DIR / FileConfig.HIGH_SCORES_FILE
            FileConfig.ensure_directories_exist()
            
            # Load existing scores
            high_scores = {}
            if scores_path.exists():
                with open(scores_path, 'r') as file:
                    high_scores = json.load(file)
            
            # Update score for current mode
            mode_key = self._current_mode.value
            current_high = high_scores.get(mode_key, 0)
            high_scores[mode_key] = max(current_high, self._game_statistics.highest_score)
            
            # Save updated scores
            with open(scores_path, 'w') as file:
                json.dump(high_scores, file, indent=2)
                
        except Exception as e:
            print(f"Error saving high scores: {e}")
    
    def _load_high_scores(self) -> None:
        """Load high scores from persistent storage."""
        try:
            scores_path = FileConfig.DATA_DIR / FileConfig.HIGH_SCORES_FILE
            
            if not scores_path.exists():
                return
            
            with open(scores_path, 'r') as file:
                high_scores = json.load(file)
            
            mode_key = self._current_mode.value
            self._game_statistics.highest_score = high_scores.get(mode_key, 0)
            
        except Exception as e:
            print(f"Error loading high scores: {e}")
    
    # ==========================================================================
    # SERIALIZATION HELPERS
    # ==========================================================================
    
    def _serialize_block(self, block: BlockData) -> Dict[str, Any]:
        """Serialize block data for saving."""
        return {
            'shape': block.shape_matrix,
            'color': block.color_rgb,
            'used': block.is_used,
            'rotation': block.rotation_angle,
            'id': block.block_id,
        }
    
    def _deserialize_block(self, block_data: Dict[str, Any]) -> BlockData:
        """Deserialize block data from save file."""
        block = BlockData(block_data['shape'], tuple(block_data['color']))
        if block_data['used']:
            block.mark_as_used()
        
        # Restore rotation
        target_rotation = block_data['rotation']
        while block.rotation_angle != target_rotation:
            block.rotate_clockwise()
        
        return block
    
    def _serialize_grid(self) -> List[List[Dict[str, Any]]]:
        """Serialize grid data for saving."""
        grid_data = []
        for row_idx in range(self.grid_manager.grid_size):
            row_data = []
            for col_idx in range(self.grid_manager.grid_size):
                from .grid_manager import BlockPosition
                position = BlockPosition(col_idx, row_idx)
                cell = self.grid_manager.get_cell_at_position(position)
                
                cell_data = {
                    'filled': cell.is_filled,
                    'color': cell.color_rgb,
                    'block_id': cell.occupied_by_block_id,
                }
                row_data.append(cell_data)
            grid_data.append(row_data)
        
        return grid_data
    
    def _deserialize_grid(self, grid_data: List[List[Dict[str, Any]]]) -> None:
        """Deserialize grid data from save file."""
        self.grid_manager.clear_all_cells()
        
        for row_idx, row_data in enumerate(grid_data):
            for col_idx, cell_data in enumerate(row_data):
                if cell_data['filled']:
                    from .grid_manager import BlockPosition
                    position = BlockPosition(col_idx, row_idx)
                    cell = self.grid_manager.get_cell_at_position(position)
                    cell.fill_with_color(
                        tuple(cell_data['color']), 
                        cell_data.get('block_id')
                    )
    
    # ==========================================================================
    # PRIVATE HELPER METHODS
    # ==========================================================================
    
    def _initialize_new_game(self) -> None:
        """Initialize a new game session."""
        # Reset game state
        self._is_game_over = False
        self._is_paused = False
        self._score_this_session = 0
        self._last_line_clear_score = 0
        self._consecutive_perfect_clears = 0
        
        # Reset timing
        self._session_start_time = time.time()
        self._total_pause_time = 0.0
        self._pause_start_time = 0.0
        
        # Set mode-specific time limits
        if self._current_mode == GameMode.TIMED:
            self._time_remaining = GameRules.TIMED_MODE_DURATION
        else:
            self._time_remaining = 0.0
        
        # Reset game components
        self.grid_manager.reset_grid()
        self._generate_new_available_blocks()
        
        # Reset session statistics (keep persistent stats)
        self._game_statistics.current_level = 1
        self._game_statistics.current_combo_count = 0
        self._game_statistics.session_start_time = time.time()
    
    def _generate_new_available_blocks(self) -> None:
        """Generate new sets of available and preview blocks."""
        # Move preview blocks to available (if any)
        if self._next_blocks_preview:
            self._available_blocks = self._next_blocks_preview[:]
        else:
            self._available_blocks = self.block_manager.create_block_set(
                GameRules.AVAILABLE_BLOCKS_COUNT
            )
        
        # Generate new preview blocks
        self._next_blocks_preview = self.block_manager.create_block_set(
            GameRules.NEXT_BLOCKS_PREVIEW_COUNT
        )
    
    def _check_game_over_conditions(self) -> None:
        """Check if game should end based on current conditions."""
        # Check if no blocks can be placed
        if not self.can_place_any_available_block():
            self.end_game(completed_successfully=False)
            return
        
        # Check mode-specific end conditions
        if self._current_mode == GameMode.TIMED:
            if self.time_remaining <= 0:
                self.end_game(completed_successfully=True)
        elif self._current_mode == GameMode.CHALLENGE:
            if self._score_this_session >= GameRules.CHALLENGE_TARGET_SCORE:
                self.end_game(completed_successfully=True)
    
    def _update_final_statistics(self, session: GameSession) -> None:
        """Update final statistics after game ends."""
        self._game_statistics.games_played_total += 1
        self._game_statistics.time_played_seconds += session.duration_seconds
        self._game_statistics.total_score += session.final_score
        
        # Update performance metrics
        self._game_statistics.update_performance_metrics(
            self._game_statistics.time_played_seconds
        )
    
    def update_game_state(self, delta_time: float) -> None:
        """Update game state with time progression."""
        if self._is_paused or self._is_game_over:
            return
        
        # Update timed mode countdown
        if self._current_mode == GameMode.TIMED:
            self._time_remaining -= delta_time
            if self._time_remaining <= 0:
                self._check_game_over_conditions()
    
    def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """Get all statistics and game state information."""
        base_stats = asdict(self._game_statistics)
        base_stats.update({
            'current_session_score': self._score_this_session,
            'current_mode': self._current_mode.value,
            'session_duration': self.session_duration,
            'time_remaining': self.time_remaining,
            'is_game_over': self._is_game_over,
            'is_paused': self._is_paused,
            'grid_statistics': self.grid_manager.get_grid_statistics(),
            'available_blocks_count': len([b for b in self._available_blocks if not b.is_used]),
            'last_line_clear_score': self._last_line_clear_score,
            'consecutive_perfect_clears': self._consecutive_perfect_clears,
        })
        return base_stats
    
    def __repr__(self) -> str:
        """String representation of game state manager."""
        return (f"GameStateManager(mode={self._current_mode.value}, "
                f"score={self._score_this_session}, "
                f"level={self._game_statistics.current_level}, "
                f"game_over={self._is_game_over})")