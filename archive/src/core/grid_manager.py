"""
Grid Manager - Handles all grid-related operations with standardized naming.
Manages grid state, collision detection, line clearing, and spatial operations.
"""

from typing import List, Tuple, Optional, Set, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

from ..config import DisplayConfig, ColorPalette
from .block_manager import BlockData, BlockPosition


class CellState(Enum):
    """Standardized cell state enumeration."""
    EMPTY = 0
    FILLED = 1


@dataclass
class GridCell:
    """Represents a single cell in the game grid."""
    state: CellState = CellState.EMPTY
    color_rgb: Tuple[int, int, int] = field(default_factory=lambda: ColorPalette.BACKGROUND_PRIMARY)
    occupied_by_block_id: Optional[str] = None
    
    @property
    def is_empty(self) -> bool:
        """Check if cell is empty."""
        return self.state == CellState.EMPTY
    
    @property
    def is_filled(self) -> bool:
        """Check if cell is filled."""
        return self.state == CellState.FILLED
    
    def fill_with_color(self, color: Tuple[int, int, int], block_id: str = None) -> None:
        """Fill cell with specified color."""
        self.state = CellState.FILLED
        self.color_rgb = color
        self.occupied_by_block_id = block_id
    
    def clear_cell(self) -> None:
        """Clear the cell."""
        self.state = CellState.EMPTY
        self.color_rgb = ColorPalette.BACKGROUND_PRIMARY
        self.occupied_by_block_id = None


@dataclass
class LineClearResult:
    """Result of line clearing operation."""
    lines_cleared_count: int = 0
    cleared_positions: List[BlockPosition] = field(default_factory=list)
    cleared_rows: List[int] = field(default_factory=list)
    cleared_columns: List[int] = field(default_factory=list)
    combo_multiplier: int = 1


class GridManager:
    """
    Manages the game grid with standardized operations.
    Handles block placement, line clearing, and spatial queries.
    """
    
    def __init__(self, grid_size: int = None):
        """Initialize grid manager with specified size."""
        self._grid_size = grid_size or DisplayConfig.GRID_SIZE
        self._grid_cells: List[List[GridCell]] = self._initialize_empty_grid()
        self._combo_counter = 0
        self._total_lines_cleared = 0
        
        # Performance optimization: cache frequently used calculations
        self._cached_filled_positions: Optional[Set[BlockPosition]] = None
        self._cache_dirty = True
    
    @property
    def grid_size(self) -> int:
        """Get the grid size (assuming square grid)."""
        return self._grid_size
    
    @property
    def grid_dimensions(self) -> Tuple[int, int]:
        """Get grid dimensions as (width, height)."""
        return (self._grid_size, self._grid_size)
    
    @property
    def combo_counter(self) -> int:
        """Get current combo counter."""
        return self._combo_counter
    
    @property
    def total_lines_cleared(self) -> int:
        """Get total number of lines cleared."""
        return self._total_lines_cleared
    
    def is_position_valid(self, position: BlockPosition) -> bool:
        """Check if position is within grid bounds."""
        return (0 <= position.x < self._grid_size and 
                0 <= position.y < self._grid_size)
    
    def is_position_empty(self, position: BlockPosition) -> bool:
        """Check if position is empty and valid."""
        if not self.is_position_valid(position):
            return False
        return self._grid_cells[position.y][position.x].is_empty
    
    def is_position_filled(self, position: BlockPosition) -> bool:
        """Check if position is filled."""
        if not self.is_position_valid(position):
            return False
        return self._grid_cells[position.y][position.x].is_filled
    
    def get_cell_at_position(self, position: BlockPosition) -> Optional[GridCell]:
        """Get cell at specified position."""
        if not self.is_position_valid(position):
            return None
        return self._grid_cells[position.y][position.x]
    
    def get_cell_color(self, position: BlockPosition) -> Tuple[int, int, int]:
        """Get color of cell at position."""
        cell = self.get_cell_at_position(position)
        return cell.color_rgb if cell else ColorPalette.BACKGROUND_PRIMARY
    
    def can_place_block(self, block: BlockData, target_position: BlockPosition) -> bool:
        """Check if block can be placed at target position."""
        for relative_pos in block.get_filled_positions():
            absolute_pos = target_position + relative_pos
            
            if not self.is_position_valid(absolute_pos):
                return False
            
            if not self.is_position_empty(absolute_pos):
                return False
        
        return True
    
    def place_block(self, block: BlockData, target_position: BlockPosition) -> bool:
        """
        Place block on grid at target position.
        
        Returns:
            True if placement successful, False otherwise
        """
        if not self.can_place_block(block, target_position):
            return False
        
        # Place the block
        for relative_pos in block.get_filled_positions():
            absolute_pos = target_position + relative_pos
            cell = self._grid_cells[absolute_pos.y][absolute_pos.x]
            cell.fill_with_color(block.color_rgb, block.block_id)
        
        # Mark block as used
        block.mark_as_used()
        
        # Invalidate cache
        self._cache_dirty = True
        
        return True
    
    def get_completed_lines(self) -> Tuple[List[int], List[int]]:
        """Get lists of completed rows and columns."""
        completed_rows = []
        completed_columns = []
        
        # Check rows
        for row_idx in range(self._grid_size):
            if all(self._grid_cells[row_idx][col_idx].is_filled 
                   for col_idx in range(self._grid_size)):
                completed_rows.append(row_idx)
        
        # Check columns
        for col_idx in range(self._grid_size):
            if all(self._grid_cells[row_idx][col_idx].is_filled 
                   for row_idx in range(self._grid_size)):
                completed_columns.append(col_idx)
        
        return completed_rows, completed_columns
    
    def clear_completed_lines(self) -> LineClearResult:
        """Clear completed lines and return result."""
        completed_rows, completed_columns = self.get_completed_lines()
        cleared_positions = []
        
        # Clear rows
        for row_idx in completed_rows:
            for col_idx in range(self._grid_size):
                position = BlockPosition(col_idx, row_idx)
                if self.is_position_filled(position):
                    cleared_positions.append(position)
                self._grid_cells[row_idx][col_idx].clear_cell()
        
        # Clear columns
        for col_idx in completed_columns:
            for row_idx in range(self._grid_size):
                position = BlockPosition(col_idx, row_idx)
                if self.is_position_filled(position):
                    # Avoid duplicates from row+column intersections
                    if position not in cleared_positions:
                        cleared_positions.append(position)
                self._grid_cells[row_idx][col_idx].clear_cell()
        
        lines_cleared_count = len(completed_rows) + len(completed_columns)
        
        # Update combo counter
        if lines_cleared_count > 0:
            self._combo_counter += 1
            self._total_lines_cleared += lines_cleared_count
        else:
            self._combo_counter = 0
        
        # Invalidate cache
        self._cache_dirty = True
        
        return LineClearResult(
            lines_cleared_count=lines_cleared_count,
            cleared_positions=cleared_positions,
            cleared_rows=completed_rows,
            cleared_columns=completed_columns,
            combo_multiplier=self._combo_counter
        )
    
    def is_grid_empty(self) -> bool:
        """Check if grid is completely empty."""
        for row in self._grid_cells:
            for cell in row:
                if cell.is_filled:
                    return False
        return True
    
    def is_grid_full(self) -> bool:
        """Check if grid is completely full."""
        for row in self._grid_cells:
            for cell in row:
                if cell.is_empty:
                    return False
        return True
    
    def get_filled_positions_count(self) -> int:
        """Get number of filled positions."""
        count = 0
        for row in self._grid_cells:
            for cell in row:
                if cell.is_filled:
                    count += 1
        return count
    
    def get_empty_positions(self) -> List[BlockPosition]:
        """Get all empty positions."""
        empty_positions = []
        for row_idx in range(self._grid_size):
            for col_idx in range(self._grid_size):
                position = BlockPosition(col_idx, row_idx)
                if self.is_position_empty(position):
                    empty_positions.append(position)
        return empty_positions
    
    def get_filled_positions(self) -> Set[BlockPosition]:
        """Get all filled positions (cached for performance)."""
        if self._cache_dirty or self._cached_filled_positions is None:
            filled_positions = set()
            for row_idx in range(self._grid_size):
                for col_idx in range(self._grid_size):
                    position = BlockPosition(col_idx, row_idx)
                    if self.is_position_filled(position):
                        filled_positions.add(position)
            
            self._cached_filled_positions = filled_positions
            self._cache_dirty = False
        
        return self._cached_filled_positions.copy()
    
    def get_possible_block_placements(self, block: BlockData) -> List[BlockPosition]:
        """Get all possible placement positions for a block."""
        valid_positions = []
        for row_idx in range(self._grid_size):
            for col_idx in range(self._grid_size):
                test_position = BlockPosition(col_idx, row_idx)
                if self.can_place_block(block, test_position):
                    valid_positions.append(test_position)
        return valid_positions
    
    def clear_all_cells(self) -> None:
        """Clear the entire grid."""
        for row in self._grid_cells:
            for cell in row:
                cell.clear_cell()
        
        self._combo_counter = 0
        self._cache_dirty = True
    
    def reset_grid(self) -> None:
        """Reset grid to initial state."""
        self.clear_all_cells()
        self._total_lines_cleared = 0
    
    def create_grid_copy(self) -> 'GridManager':
        """Create a deep copy of the grid."""
        new_grid = GridManager(self._grid_size)
        
        # Copy all cells
        for row_idx in range(self._grid_size):
            for col_idx in range(self._grid_size):
                original_cell = self._grid_cells[row_idx][col_idx]
                new_cell = new_grid._grid_cells[row_idx][col_idx]
                
                new_cell.state = original_cell.state
                new_cell.color_rgb = original_cell.color_rgb
                new_cell.occupied_by_block_id = original_cell.occupied_by_block_id
        
        new_grid._combo_counter = self._combo_counter
        new_grid._total_lines_cleared = self._total_lines_cleared
        
        return new_grid
    
    def get_grid_statistics(self) -> Dict[str, Any]:
        """Get comprehensive grid statistics."""
        filled_count = self.get_filled_positions_count()
        total_cells = self._grid_size * self._grid_size
        
        # Count cells by color
        color_counts = {}
        for row in self._grid_cells:
            for cell in row:
                if cell.is_filled:
                    color_key = str(cell.color_rgb)
                    color_counts[color_key] = color_counts.get(color_key, 0) + 1
        
        return {
            'grid_size': self._grid_size,
            'total_cells': total_cells,
            'filled_cells': filled_count,
            'empty_cells': total_cells - filled_count,
            'fill_percentage': (filled_count / total_cells) * 100,
            'combo_counter': self._combo_counter,
            'total_lines_cleared': self._total_lines_cleared,
            'is_empty': self.is_grid_empty(),
            'is_full': self.is_grid_full(),
            'color_distribution': color_counts,
        }
    
    def _initialize_empty_grid(self) -> List[List[GridCell]]:
        """Initialize empty grid with default cells."""
        return [[GridCell() for _ in range(self._grid_size)] 
                for _ in range(self._grid_size)]
    
    def __str__(self) -> str:
        """String representation of the grid."""
        result = []
        for row in self._grid_cells:
            row_str = ''.join(['█' if cell.is_filled else '·' for cell in row])
            result.append(row_str)
        return '\n'.join(result)
    
    def __repr__(self) -> str:
        """Detailed representation of the grid."""
        stats = self.get_grid_statistics()
        return (f"GridManager(size={self._grid_size}, "
                f"filled={stats['filled_cells']}/{stats['total_cells']}, "
                f"combo={self._combo_counter})")
    
    def __eq__(self, other: 'GridManager') -> bool:
        """Check equality with another grid."""
        if not isinstance(other, GridManager):
            return False
        
        if self._grid_size != other._grid_size:
            return False
        
        for row_idx in range(self._grid_size):
            for col_idx in range(self._grid_size):
                self_cell = self._grid_cells[row_idx][col_idx]
                other_cell = other._grid_cells[row_idx][col_idx]
                
                if (self_cell.state != other_cell.state or
                    self_cell.color_rgb != other_cell.color_rgb):
                    return False
        
        return True