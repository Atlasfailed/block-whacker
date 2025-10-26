"""
File Manager - Handles file operations with standardized file management.
Provides safe file I/O operations for game data persistence.
"""

import os
import json
import pickle
import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import asdict, is_dataclass

from ..config import FileConfig


class FileManager:
    """
    Manages file operations with standardized error handling and validation.
    Provides safe methods for saving and loading game data.
    """
    
    def __init__(self):
        """Initialize file manager."""
        self.base_save_directory = Path(FileConfig.SAVES_DIR)
        self.backup_directory = Path(FileConfig.BACKUP_DIR)
        
        # Ensure directories exist
        self._ensure_directories_exist()
        
        # File operation statistics
        self.files_saved_total = 0
        self.files_loaded_total = 0
        self.save_errors_total = 0
        self.load_errors_total = 0
    
    def _ensure_directories_exist(self) -> None:
        """Ensure all required directories exist."""
        directories = [
            self.base_save_directory,
            self.backup_directory,
            self.base_save_directory / 'game_data',
            self.base_save_directory / 'settings',
            self.base_save_directory / 'statistics'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def save_json_data(self, data: Any, file_path: Union[str, Path], 
                      create_backup: bool = True) -> bool:
        """Save data as JSON file with optional backup."""
        try:
            file_path = Path(file_path)
            
            # Create backup if requested and file exists
            if create_backup and file_path.exists():
                self._create_backup(file_path)
            
            # Convert dataclasses to dictionaries
            serializable_data = self._make_serializable(data)
            
            # Write to temporary file first
            temp_path = file_path.with_suffix('.tmp')
            with open(temp_path, 'w', encoding='utf-8') as file:
                json.dump(serializable_data, file, indent=2, ensure_ascii=False)
            
            # Atomic move to final location
            temp_path.replace(file_path)
            
            self.files_saved_total += 1
            return True
            
        except Exception as e:
            self.save_errors_total += 1
            print(f"Error saving JSON file {file_path}: {e}")
            return False
    
    def load_json_data(self, file_path: Union[str, Path], 
                      default_value: Any = None) -> Any:
        """Load data from JSON file with fallback to default."""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return default_value
            
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            self.files_loaded_total += 1
            return data
            
        except Exception as e:
            self.load_errors_total += 1
            print(f"Error loading JSON file {file_path}: {e}")
            return default_value
    
    def save_binary_data(self, data: Any, file_path: Union[str, Path], 
                        create_backup: bool = True) -> bool:
        """Save data as binary pickle file with optional backup."""
        try:
            file_path = Path(file_path)
            
            # Create backup if requested and file exists
            if create_backup and file_path.exists():
                self._create_backup(file_path)
            
            # Write to temporary file first
            temp_path = file_path.with_suffix('.tmp')
            with open(temp_path, 'wb') as file:
                pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)
            
            # Atomic move to final location
            temp_path.replace(file_path)
            
            self.files_saved_total += 1
            return True
            
        except Exception as e:
            self.save_errors_total += 1
            print(f"Error saving binary file {file_path}: {e}")
            return False
    
    def load_binary_data(self, file_path: Union[str, Path], 
                        default_value: Any = None) -> Any:
        """Load data from binary pickle file with fallback to default."""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return default_value
            
            with open(file_path, 'rb') as file:
                data = pickle.load(file)
            
            self.files_loaded_total += 1
            return data
            
        except Exception as e:
            self.load_errors_total += 1
            print(f"Error loading binary file {file_path}: {e}")
            return default_value
    
    def _create_backup(self, file_path: Path) -> bool:
        """Create a backup of the specified file."""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
            backup_path = self.backup_directory / backup_name
            
            # Copy file to backup location
            import shutil
            shutil.copy2(file_path, backup_path)
            
            # Clean up old backups (keep only recent ones)
            self._cleanup_old_backups(file_path.stem)
            
            return True
            
        except Exception as e:
            print(f"Error creating backup for {file_path}: {e}")
            return False
    
    def _cleanup_old_backups(self, file_stem: str, max_backups: int = 10) -> None:
        """Clean up old backup files, keeping only the most recent ones."""
        try:
            # Find all backup files for this file
            backup_pattern = f"{file_stem}_*"
            backup_files = list(self.backup_directory.glob(backup_pattern))
            
            if len(backup_files) > max_backups:
                # Sort by modification time (oldest first)
                backup_files.sort(key=lambda p: p.stat().st_mtime)
                
                # Remove oldest files
                files_to_remove = backup_files[:-max_backups]
                for file_path in files_to_remove:
                    file_path.unlink()
                    
        except Exception as e:
            print(f"Error cleaning up backups for {file_stem}: {e}")
    
    def _make_serializable(self, data: Any) -> Any:
        """Convert complex data types to JSON-serializable format."""
        if isinstance(data, dict):
            return {key: self._make_serializable(value) for key, value in data.items()}
        elif isinstance(data, (list, tuple)):
            return [self._make_serializable(item) for item in data]
        elif is_dataclass(data):
            return self._make_serializable(asdict(data))
        elif hasattr(data, '__dict__'):
            # Convert objects with __dict__ to dictionaries
            return self._make_serializable(data.__dict__)
        elif isinstance(data, (int, float, str, bool)) or data is None:
            return data
        else:
            # Convert other types to string representation
            return str(data)
    
    def file_exists(self, file_path: Union[str, Path]) -> bool:
        """Check if a file exists."""
        return Path(file_path).exists()
    
    def delete_file(self, file_path: Union[str, Path], 
                   create_backup: bool = True) -> bool:
        """Delete a file with optional backup."""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return True  # File doesn't exist, consider it "deleted"
            
            # Create backup if requested
            if create_backup:
                self._create_backup(file_path)
            
            file_path.unlink()
            return True
            
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
            return False
    
    def get_file_size(self, file_path: Union[str, Path]) -> Optional[int]:
        """Get file size in bytes."""
        try:
            return Path(file_path).stat().st_size
        except Exception:
            return None
    
    def get_file_modified_time(self, file_path: Union[str, Path]) -> Optional[datetime.datetime]:
        """Get file modification time."""
        try:
            timestamp = Path(file_path).stat().st_mtime
            return datetime.datetime.fromtimestamp(timestamp)
        except Exception:
            return None
    
    def list_save_files(self, file_pattern: str = "*") -> List[Path]:
        """List all save files matching the pattern."""
        try:
            return list(self.base_save_directory.glob(f"**/{file_pattern}"))
        except Exception:
            return []
    
    def list_backup_files(self, file_pattern: str = "*") -> List[Path]:
        """List all backup files matching the pattern."""
        try:
            return list(self.backup_directory.glob(file_pattern))
        except Exception:
            return []
    
    def get_save_directory_info(self) -> Dict[str, Any]:
        """Get information about the save directory."""
        try:
            save_files = self.list_save_files()
            backup_files = self.list_backup_files()
            
            total_save_size = sum(f.stat().st_size for f in save_files if f.is_file())
            total_backup_size = sum(f.stat().st_size for f in backup_files if f.is_file())
            
            return {
                'save_directory': str(self.base_save_directory),
                'backup_directory': str(self.backup_directory),
                'save_files_count': len(save_files),
                'backup_files_count': len(backup_files),
                'total_save_size_bytes': total_save_size,
                'total_backup_size_bytes': total_backup_size,
                'directories_exist': self.base_save_directory.exists()
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_file_statistics(self) -> Dict[str, Any]:
        """Get file operation statistics."""
        return {
            'files_saved_total': self.files_saved_total,
            'files_loaded_total': self.files_loaded_total,
            'save_errors_total': self.save_errors_total,
            'load_errors_total': self.load_errors_total,
            'save_success_rate': (
                self.files_saved_total / max(1, self.files_saved_total + self.save_errors_total)
            ),
            'load_success_rate': (
                self.files_loaded_total / max(1, self.files_loaded_total + self.load_errors_total)
            )
        }
    
    def reset_statistics(self) -> None:
        """Reset file operation statistics."""
        self.files_saved_total = 0
        self.files_loaded_total = 0
        self.save_errors_total = 0
        self.load_errors_total = 0
    
    def __repr__(self) -> str:
        """String representation of file manager."""
        return (f"FileManager(saves={self.files_saved_total}, "
                f"loads={self.files_loaded_total}, "
                f"directory={self.base_save_directory})")