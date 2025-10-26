"""
Block Manager - Handles all block-related operations with standardized naming.
Manages block creation, manipulation, rotation, and shape definitions.
"""

import random
from typing import List, Tuple, Optional
from dataclasses import dataclass

from ..config import (
    ColorPalette,
    BlockShapesConfig,
    get_block_colors,
)


@dataclass
@dataclass(frozen=True)
class BlockPosition:
    """Standardized position representation for blocks."""
    x: int
    y: int
    
    def __add__(self, other: 'BlockPosition') -> 'BlockPosition':
        return BlockPosition(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'BlockPosition') -> 'BlockPosition':
        return BlockPosition(self.x - other.x, self.y - other.y)


class BlockData:
    """
    Standardized block data structure with enhanced functionality.
    Represents a single game block with shape, color, and state.
    """
    
    def __init__(self, 
                 shape: List[List[int]] = None, 
                 color: Tuple[int, int, int] = None,
                 block_id: Optional[str] = None):
        """Initialize block with shape and color."""
        self._shape_matrix = shape if shape is not None else self._get_random_shape()
        self._color_rgb = color if color is not None else random.choice(get_block_colors())
        self._is_used = False
        self._rotation_angle = 0
        self._block_id = block_id or self._generate_block_id()
        
        # Validate shape
        self._validate_shape()
    
    @property
    def shape_matrix(self) -> List[List[int]]:
        """Get the current shape matrix."""
        return self._shape_matrix
    
    @property 
    def color_rgb(self) -> Tuple[int, int, int]:
        """Get the block color as RGB tuple."""
        return self._color_rgb
    
    @property
    def is_used(self) -> bool:
        """Check if block has been placed."""
        return self._is_used
    
    @property
    def rotation_angle(self) -> int:
        """Get current rotation angle in degrees."""
        return self._rotation_angle
    
    @property
    def block_id(self) -> str:
        """Get unique block identifier."""
        return self._block_id
    
    @property
    def width_cells(self) -> int:
        """Get block width in cells."""
        return len(self._shape_matrix[0]) if self._shape_matrix else 0
    
    @property
    def height_cells(self) -> int:
        """Get block height in cells."""
        return len(self._shape_matrix) if self._shape_matrix else 0
    
    def mark_as_used(self) -> None:
        """Mark this block as used/placed."""
        self._is_used = True
    
    def mark_as_unused(self) -> None:
        """Mark this block as unused (for testing/undo)."""
        self._is_used = False
    
    def get_filled_positions(self) -> List[BlockPosition]:
        """Get all filled cell positions relative to block origin."""
        filled_positions = []
        for row_index, row_data in enumerate(self._shape_matrix):
            for col_index, cell_value in enumerate(row_data):
                if cell_value == 1:
                    filled_positions.append(BlockPosition(col_index, row_index))
        return filled_positions
    
    def rotate_clockwise(self) -> None:
        """Rotate block 90 degrees clockwise."""
        if not self._shape_matrix:
            return
        
        rows_count = len(self._shape_matrix)
        cols_count = len(self._shape_matrix[0])
        
        # Create rotated matrix
        rotated_matrix = [[0 for _ in range(rows_count)] for _ in range(cols_count)]
        
        for row_idx in range(rows_count):
            for col_idx in range(cols_count):
                rotated_matrix[col_idx][rows_count - 1 - row_idx] = self._shape_matrix[row_idx][col_idx]
        
        self._shape_matrix = rotated_matrix
        self._rotation_angle = (self._rotation_angle + 90) % 360
    
    def rotate_counterclockwise(self) -> None:
        """Rotate block 90 degrees counterclockwise."""
        # Rotate clockwise 3 times = counterclockwise once
        for _ in range(3):
            self.rotate_clockwise()
    
    def create_copy(self) -> 'BlockData':
        """Create a deep copy of this block."""
        new_block = BlockData()
        new_block._shape_matrix = [row[:] for row in self._shape_matrix]  # Deep copy
        new_block._color_rgb = self._color_rgb
        new_block._is_used = self._is_used
        new_block._rotation_angle = self._rotation_angle
        new_block._block_id = f"{self._block_id}_copy"
        return new_block
    
    def reset_rotation(self) -> None:
        """Reset block to original rotation."""
        current_angle = self._rotation_angle
        rotations_needed = (360 - current_angle) // 90
        for _ in range(rotations_needed % 4):
            self.rotate_clockwise()
    
    def get_bounding_box(self) -> Tuple[int, int, int, int]:
        """Get bounding box as (min_x, min_y, max_x, max_y)."""
        filled_positions = self.get_filled_positions()
        if not filled_positions:
            return (0, 0, 0, 0)
        
        min_x = min(pos.x for pos in filled_positions)
        min_y = min(pos.y for pos in filled_positions)
        max_x = max(pos.x for pos in filled_positions)
        max_y = max(pos.y for pos in filled_positions)
        
        return (min_x, min_y, max_x, max_y)
    
    def _get_random_shape(self) -> List[List[int]]:
        """Get a random block shape from configuration."""
        all_shapes = BlockShapesConfig.get_all_shapes()
        return random.choice(all_shapes)
    
    def _generate_block_id(self) -> str:
        """Generate unique block identifier."""
        import time
        timestamp = int(time.time() * 1000)
        random_suffix = random.randint(1000, 9999)
        return f"block_{timestamp}_{random_suffix}"
    
    def _validate_shape(self) -> None:
        """Validate that the shape matrix is valid."""
        if not self._shape_matrix:
            raise ValueError("Block shape cannot be empty")
        
        if not all(isinstance(row, list) for row in self._shape_matrix):
            raise ValueError("Block shape must be a 2D list")
        
        row_length = len(self._shape_matrix[0])
        if not all(len(row) == row_length for row in self._shape_matrix):
            raise ValueError("All rows in block shape must have same length")
        
        # Check if block has at least one filled cell
        has_filled_cell = any(cell == 1 for row in self._shape_matrix for cell in row)
        if not has_filled_cell:
            raise ValueError("Block must have at least one filled cell")
    
    def __str__(self) -> str:
        """String representation of the block."""
        result = []
        for row in self._shape_matrix:
            result.append(''.join(['█' if cell else '·' for cell in row]))
        return '\n'.join(result)
    
    def __repr__(self) -> str:
        """Detailed representation of the block."""
        return (f"BlockData(id={self._block_id}, "
                f"size={self.width_cells}x{self.height_cells}, "
                f"rotation={self._rotation_angle}°, "
                f"used={self._is_used})")


class BlockManager:
    """
    Manages block generation, validation, and operations.
    Provides high-level interface for all block-related functionality.
    """
    
    def __init__(self):
        """Initialize the block manager."""
        self._available_shapes = BlockShapesConfig.get_all_shapes()
        self._available_colors = get_block_colors()
        self._generation_seed = None
        
    def create_random_block(self) -> BlockData:
        """Create a new random block."""
        return BlockData()
    
    def create_block_from_shape(self, 
                               shape: List[List[int]], 
                               color: Tuple[int, int, int] = None) -> BlockData:
        """Create a block from specific shape and optional color."""
        return BlockData(shape, color)
    
    def create_block_set(self, count: int = 3) -> List[BlockData]:
        """Create a set of random blocks."""
        return [self.create_random_block() for _ in range(count)]
    
    def validate_block_placement(self, 
                                block: BlockData, 
                                target_position: BlockPosition,
                                occupied_positions: List[BlockPosition],
                                grid_bounds: Tuple[int, int]) -> bool:
        """
        Validate if a block can be placed at target position.
        
        Args:
            block: The block to validate
            target_position: Position where block would be placed
            occupied_positions: List of already occupied grid positions
            grid_bounds: (width, height) of the grid
            
        Returns:
            True if placement is valid, False otherwise
        """
        grid_width, grid_height = grid_bounds
        
        for relative_pos in block.get_filled_positions():
            absolute_pos = target_position + relative_pos
            
            # Check grid bounds
            if (absolute_pos.x < 0 or absolute_pos.x >= grid_width or
                absolute_pos.y < 0 or absolute_pos.y >= grid_height):
                return False
            
            # Check collision with occupied positions
            if absolute_pos in occupied_positions:
                return False
        
        return True
    
    def get_valid_placements(self, 
                           block: BlockData,
                           occupied_positions: List[BlockPosition],
                           grid_bounds: Tuple[int, int]) -> List[BlockPosition]:
        """
        Get all valid placement positions for a block.
        
        Returns:
            List of valid BlockPosition objects where block can be placed
        """
        valid_positions = []
        grid_width, grid_height = grid_bounds
        
        for y in range(grid_height):
            for x in range(grid_width):
                test_position = BlockPosition(x, y)
                if self.validate_block_placement(block, test_position, occupied_positions, grid_bounds):
                    valid_positions.append(test_position)
        
        return valid_positions
    
    def can_place_any_block(self, 
                           blocks: List[BlockData],
                           occupied_positions: List[BlockPosition],
                           grid_bounds: Tuple[int, int]) -> bool:
        """Check if any of the given blocks can be placed somewhere on the grid."""
        for block in blocks:
            if block.is_used:
                continue
            
            if self.get_valid_placements(block, occupied_positions, grid_bounds):
                return True
        
        return False
    
    def set_generation_seed(self, seed: int) -> None:
        """Set random seed for deterministic block generation (useful for testing)."""
        self._generation_seed = seed
        random.seed(seed)
    
    def get_shape_statistics(self) -> dict:
        """Get statistics about available shapes."""
        stats = {
            'total_shapes': len(self._available_shapes),
            'shape_categories': {
                'basic': len(BlockShapesConfig.SHAPES_BASIC),
                'l_pieces': len(BlockShapesConfig.SHAPES_L_PIECES),
                'squares': len(BlockShapesConfig.SHAPES_SQUARES),
                't_pieces': len(BlockShapesConfig.SHAPES_T_PIECES),
                'z_pieces': len(BlockShapesConfig.SHAPES_Z_PIECES),
                'special': len(BlockShapesConfig.SHAPES_SPECIAL),
            },
            'available_colors': len(self._available_colors),
        }
        return stats
    
    def __repr__(self) -> str:
        """String representation of the block manager."""
        stats = self.get_shape_statistics()
        return f"BlockManager(shapes={stats['total_shapes']}, colors={stats['available_colors']})"