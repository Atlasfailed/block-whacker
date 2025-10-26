"""
Validation Utils - Input validation and data verification with standardized validation.
Provides comprehensive validation functions for game data integrity.
"""

import re
from typing import Any, List, Dict, Union, Optional, Callable, Tuple
from pathlib import Path

from ..config import DisplayConfig, AudioConfig
from ..core.block_manager import BlockPosition


class ValidationUtils:
    """
    Validation utility functions for data integrity and input validation.
    Provides standardized validation operations across the game.
    """
    
    @staticmethod
    def is_valid_rgb_color(color: Any) -> bool:
        """Validate RGB color tuple."""
        if not isinstance(color, (tuple, list)):
            return False
        
        if len(color) != 3:
            return False
        
        return all(isinstance(c, int) and 0 <= c <= 255 for c in color)
    
    @staticmethod
    def is_valid_rgba_color(color: Any) -> bool:
        """Validate RGBA color tuple."""
        if not isinstance(color, (tuple, list)):
            return False
        
        if len(color) != 4:
            return False
        
        # RGB values: 0-255, Alpha: 0-255
        return all(isinstance(c, int) and 0 <= c <= 255 for c in color)
    
    @staticmethod
    def is_valid_position(position: Any) -> bool:
        """Validate position tuple or BlockPosition."""
        if isinstance(position, BlockPosition):
            return isinstance(position.x, int) and isinstance(position.y, int)
        
        if not isinstance(position, (tuple, list)):
            return False
        
        if len(position) != 2:
            return False
        
        return all(isinstance(coord, int) for coord in position)
    
    @staticmethod
    def is_valid_grid_position(position: Any, grid_size: int = DisplayConfig.GRID_SIZE) -> bool:
        """Validate grid position is within bounds."""
        if not ValidationUtils.is_valid_position(position):
            return False
        
        if isinstance(position, BlockPosition):
            x, y = position.x, position.y
        else:
            x, y = position
        
        return 0 <= x < grid_size and 0 <= y < grid_size
    
    @staticmethod
    def is_valid_block_shape(shape: Any) -> bool:
        """Validate block shape matrix."""
        if not isinstance(shape, list):
            return False
        
        if not shape:  # Empty list
            return False
        
        # Check all rows are lists and same length
        row_length = len(shape[0]) if shape else 0
        for row in shape:
            if not isinstance(row, list):
                return False
            if len(row) != row_length:
                return False
            
            # Check all values are 0 or 1
            if not all(cell in [0, 1] for cell in row):
                return False
        
        # Shape must contain at least one filled cell
        return any(cell == 1 for row in shape for cell in row)
    
    @staticmethod
    def is_valid_score(score: Any) -> bool:
        """Validate score value."""
        return isinstance(score, int) and score >= 0
    
    @staticmethod
    def is_valid_level(level: Any) -> bool:
        """Validate level value."""
        return isinstance(level, int) and level >= 1
    
    @staticmethod
    def is_valid_volume(volume: Any) -> bool:
        """Validate volume value (0.0 to 1.0)."""
        return isinstance(volume, (int, float)) and 0.0 <= volume <= 1.0
    
    @staticmethod
    def is_valid_duration(duration: Any) -> bool:
        """Validate duration value (positive number)."""
        return isinstance(duration, (int, float)) and duration >= 0.0
    
    @staticmethod
    def is_valid_percentage(percentage: Any) -> bool:
        """Validate percentage value (0.0 to 100.0)."""
        return isinstance(percentage, (int, float)) and 0.0 <= percentage <= 100.0
    
    @staticmethod
    def is_valid_probability(probability: Any) -> bool:
        """Validate probability value (0.0 to 1.0)."""
        return isinstance(probability, (int, float)) and 0.0 <= probability <= 1.0
    
    @staticmethod
    def is_valid_file_path(file_path: Any) -> bool:
        """Validate file path string."""
        if not isinstance(file_path, (str, Path)):
            return False
        
        try:
            path = Path(file_path)
            # Check if path is valid (doesn't contain invalid characters)
            str(path.resolve())
            return True
        except (ValueError, OSError):
            return False
    
    @staticmethod
    def is_valid_save_file_name(filename: str) -> bool:
        """Validate save file name."""
        if not isinstance(filename, str):
            return False
        
        # Check length
        if not (1 <= len(filename) <= 255):
            return False
        
        # Check for invalid characters
        invalid_chars = r'[<>:"/\\|?*]'
        if re.search(invalid_chars, filename):
            return False
        
        # Check for reserved names on Windows
        reserved_names = {
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        }
        
        if filename.upper().split('.')[0] in reserved_names:
            return False
        
        return True
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email address format."""
        if not isinstance(email, str):
            return False
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None
    
    @staticmethod
    def is_valid_username(username: str) -> bool:
        """Validate username format."""
        if not isinstance(username, str):
            return False
        
        # Length check
        if not (3 <= len(username) <= 20):
            return False
        
        # Character check (alphanumeric and underscore only)
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False
        
        # Must start with letter
        if not username[0].isalpha():
            return False
        
        return True
    
    @staticmethod
    def is_valid_configuration_data(config_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate configuration data structure."""
        errors = []
        
        if not isinstance(config_data, dict):
            errors.append("Configuration must be a dictionary")
            return False, errors
        
        # Check required configuration sections
        required_sections = ['display', 'audio', 'game', 'controls']
        for section in required_sections:
            if section not in config_data:
                errors.append(f"Missing required section: {section}")
        
        # Validate display settings
        if 'display' in config_data:
            display_config = config_data['display']
            
            if 'resolution' in display_config:
                resolution = display_config['resolution']
                if not (isinstance(resolution, (list, tuple)) and len(resolution) == 2):
                    errors.append("Display resolution must be [width, height]")
                elif not all(isinstance(dim, int) and dim > 0 for dim in resolution):
                    errors.append("Display resolution dimensions must be positive integers")
            
            if 'fullscreen' in display_config:
                if not isinstance(display_config['fullscreen'], bool):
                    errors.append("Fullscreen setting must be boolean")
        
        # Validate audio settings
        if 'audio' in config_data:
            audio_config = config_data['audio']
            
            for volume_key in ['master_volume', 'music_volume', 'effects_volume']:
                if volume_key in audio_config:
                    if not ValidationUtils.is_valid_volume(audio_config[volume_key]):
                        errors.append(f"Audio {volume_key} must be between 0.0 and 1.0")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def is_valid_save_data(save_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate save game data structure."""
        errors = []
        
        if not isinstance(save_data, dict):
            errors.append("Save data must be a dictionary")
            return False, errors
        
        # Check required save data fields
        required_fields = ['version', 'timestamp', 'game_state', 'statistics']
        for field in required_fields:
            if field not in save_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate game state
        if 'game_state' in save_data:
            game_state = save_data['game_state']
            
            if 'score' in game_state:
                if not ValidationUtils.is_valid_score(game_state['score']):
                    errors.append("Invalid score in save data")
            
            if 'level' in game_state:
                if not ValidationUtils.is_valid_level(game_state['level']):
                    errors.append("Invalid level in save data")
            
            if 'grid' in game_state:
                grid = game_state['grid']
                if not isinstance(grid, list):
                    errors.append("Grid data must be a list")
                elif grid and not all(isinstance(row, list) for row in grid):
                    errors.append("Grid rows must be lists")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename by removing/replacing invalid characters."""
        if not isinstance(filename, str):
            return "unnamed"
        
        # Replace invalid characters with underscores
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip(' .')
        
        # Ensure not empty
        if not sanitized:
            sanitized = "unnamed"
        
        # Truncate to reasonable length
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        
        return sanitized
    
    @staticmethod
    def sanitize_user_input(user_input: str, max_length: int = 1000) -> str:
        """Sanitize user input for safe processing."""
        if not isinstance(user_input, str):
            return ""
        
        # Remove control characters except newlines and tabs
        sanitized = ''.join(char for char in user_input 
                          if ord(char) >= 32 or char in '\n\t')
        
        # Truncate to max length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        # Strip leading/trailing whitespace
        sanitized = sanitized.strip()
        
        return sanitized
    
    @staticmethod
    def validate_range(value: Any, min_value: Union[int, float], 
                      max_value: Union[int, float]) -> bool:
        """Validate that value is within specified range."""
        if not isinstance(value, (int, float)):
            return False
        
        return min_value <= value <= max_value
    
    @staticmethod
    def validate_list_of_type(data: Any, expected_type: type, 
                             min_length: int = 0, max_length: Optional[int] = None) -> bool:
        """Validate that data is a list of specified type with length constraints."""
        if not isinstance(data, list):
            return False
        
        if len(data) < min_length:
            return False
        
        if max_length is not None and len(data) > max_length:
            return False
        
        return all(isinstance(item, expected_type) for item in data)
    
    @staticmethod
    def validate_dict_structure(data: Dict[str, Any], required_keys: List[str], 
                               optional_keys: Optional[List[str]] = None) -> Tuple[bool, List[str]]:
        """Validate dictionary has required keys and no unexpected keys."""
        errors = []
        
        if not isinstance(data, dict):
            errors.append("Data must be a dictionary")
            return False, errors
        
        # Check required keys
        for key in required_keys:
            if key not in data:
                errors.append(f"Missing required key: {key}")
        
        # Check for unexpected keys
        allowed_keys = set(required_keys)
        if optional_keys:
            allowed_keys.update(optional_keys)
        
        unexpected_keys = set(data.keys()) - allowed_keys
        if unexpected_keys:
            errors.append(f"Unexpected keys: {', '.join(unexpected_keys)}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_with_callback(value: Any, validator_function: Callable[[Any], bool]) -> bool:
        """Validate value using custom validator function."""
        try:
            return validator_function(value)
        except Exception:
            return False
    
    @staticmethod
    def is_valid_json_serializable(data: Any) -> bool:
        """Check if data can be serialized to JSON."""
        import json
        try:
            json.dumps(data)
            return True
        except (TypeError, ValueError):
            return False
    
    @staticmethod
    def validate_network_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate network communication data."""
        errors = []
        
        if not isinstance(data, dict):
            errors.append("Network data must be a dictionary")
            return False, errors
        
        # Check required fields
        required_fields = ['type', 'payload']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Validate message type
        if 'type' in data:
            if not isinstance(data['type'], str):
                errors.append("Message type must be a string")
            elif not data['type'].strip():
                errors.append("Message type cannot be empty")
        
        # Check JSON serializable
        if not ValidationUtils.is_valid_json_serializable(data):
            errors.append("Data must be JSON serializable")
        
        return len(errors) == 0, errors