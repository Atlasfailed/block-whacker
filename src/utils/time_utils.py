"""
Time Utils - Time-related utility functions with standardized time handling.
Provides time management and formatting functions for the game.
"""

import time
import datetime
from typing import Optional, Tuple, Dict, Any


class TimeUtils:
    """
    Time utility functions for game timing and formatting.
    Provides standardized time management operations.
    """
    
    @staticmethod
    def get_current_timestamp() -> float:
        """Get current timestamp in seconds since epoch."""
        return time.time()
    
    @staticmethod
    def get_current_datetime() -> datetime.datetime:
        """Get current datetime object."""
        return datetime.datetime.now()
    
    @staticmethod
    def format_duration(seconds: float, include_hours: bool = True, 
                       include_milliseconds: bool = False) -> str:
        """Format duration in seconds to human-readable string."""
        if seconds < 0:
            return "00:00"
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        remaining_seconds = seconds % 60
        
        if include_milliseconds:
            seconds_int = int(remaining_seconds)
            milliseconds = int((remaining_seconds - seconds_int) * 1000)
            
            if include_hours and hours > 0:
                return f"{hours:02d}:{minutes:02d}:{seconds_int:02d}.{milliseconds:03d}"
            else:
                return f"{minutes:02d}:{seconds_int:02d}.{milliseconds:03d}"
        else:
            seconds_int = int(remaining_seconds)
            
            if include_hours and hours > 0:
                return f"{hours:02d}:{minutes:02d}:{seconds_int:02d}"
            else:
                return f"{minutes:02d}:{seconds_int:02d}"
    
    @staticmethod
    def format_compact_duration(seconds: float) -> str:
        """Format duration in compact format (e.g., '1h 23m', '45s')."""
        if seconds < 0:
            return "0s"
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        remaining_seconds = int(seconds % 60)
        
        parts = []
        
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if remaining_seconds > 0 or not parts:
            parts.append(f"{remaining_seconds}s")
        
        return " ".join(parts)
    
    @staticmethod
    def parse_duration_string(duration_str: str) -> Optional[float]:
        """Parse duration string back to seconds."""
        try:
            # Handle formats like "12:34", "1:23:45", "1h 23m 45s"
            duration_str = duration_str.strip().lower()
            
            # Compact format (1h 23m 45s)
            if any(unit in duration_str for unit in ['h', 'm', 's']):
                total_seconds = 0.0
                
                # Extract hours
                if 'h' in duration_str:
                    h_parts = duration_str.split('h')
                    if h_parts[0].strip().isdigit():
                        total_seconds += int(h_parts[0].strip()) * 3600
                    duration_str = h_parts[1] if len(h_parts) > 1 else ""
                
                # Extract minutes
                if 'm' in duration_str:
                    m_parts = duration_str.split('m')
                    if m_parts[0].strip().isdigit():
                        total_seconds += int(m_parts[0].strip()) * 60
                    duration_str = m_parts[1] if len(m_parts) > 1 else ""
                
                # Extract seconds
                if 's' in duration_str:
                    s_parts = duration_str.split('s')[0].strip()
                    if s_parts.replace('.', '').isdigit():
                        total_seconds += float(s_parts)
                
                return total_seconds
            
            # Colon format (MM:SS or HH:MM:SS)
            elif ':' in duration_str:
                parts = duration_str.split(':')
                if len(parts) == 2:  # MM:SS
                    minutes, seconds = parts
                    return int(minutes) * 60 + float(seconds)
                elif len(parts) == 3:  # HH:MM:SS
                    hours, minutes, seconds = parts
                    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
            
            # Just a number (assume seconds)
            else:
                return float(duration_str)
                
        except Exception:
            return None
    
    @staticmethod
    def calculate_fps(frame_times: list) -> float:
        """Calculate FPS from list of frame times."""
        if not frame_times or len(frame_times) < 2:
            return 0.0
        
        total_time = frame_times[-1] - frame_times[0]
        frame_count = len(frame_times) - 1
        
        if total_time <= 0:
            return 0.0
        
        return frame_count / total_time
    
    @staticmethod
    def calculate_average_frame_time(frame_times: list) -> float:
        """Calculate average frame time from list of frame times."""
        if not frame_times or len(frame_times) < 2:
            return 0.0
        
        deltas = [frame_times[i] - frame_times[i-1] for i in range(1, len(frame_times))]
        return sum(deltas) / len(deltas)
    
    @staticmethod
    def get_time_since(start_time: float) -> float:
        """Get time elapsed since start time."""
        return time.time() - start_time
    
    @staticmethod
    def is_timeout(start_time: float, timeout_duration: float) -> bool:
        """Check if timeout duration has elapsed since start time."""
        return TimeUtils.get_time_since(start_time) >= timeout_duration
    
    @staticmethod
    def sleep_precise(duration: float) -> None:
        """Sleep for precise duration using high-resolution timing."""
        if duration <= 0:
            return
        
        end_time = time.perf_counter() + duration
        
        # Use time.sleep for most of the duration
        if duration > 0.001:  # 1ms
            time.sleep(duration - 0.001)
        
        # Busy wait for the remaining time for precision
        while time.perf_counter() < end_time:
            pass
    
    @staticmethod
    def create_timer() -> Dict[str, Any]:
        """Create a new timer object."""
        return {
            'start_time': time.perf_counter(),
            'last_lap': time.perf_counter(),
            'laps': [],
            'running': True
        }
    
    @staticmethod
    def lap_timer(timer: Dict[str, Any]) -> float:
        """Record a lap time and return lap duration."""
        if not timer.get('running', False):
            return 0.0
        
        current_time = time.perf_counter()
        lap_duration = current_time - timer['last_lap']
        
        timer['laps'].append({
            'lap_number': len(timer['laps']) + 1,
            'lap_duration': lap_duration,
            'total_duration': current_time - timer['start_time'],
            'timestamp': current_time
        })
        
        timer['last_lap'] = current_time
        return lap_duration
    
    @staticmethod
    def stop_timer(timer: Dict[str, Any]) -> float:
        """Stop timer and return total duration."""
        if not timer.get('running', False):
            return 0.0
        
        current_time = time.perf_counter()
        total_duration = current_time - timer['start_time']
        
        timer['running'] = False
        timer['end_time'] = current_time
        timer['total_duration'] = total_duration
        
        return total_duration
    
    @staticmethod
    def get_timer_duration(timer: Dict[str, Any]) -> float:
        """Get current timer duration without stopping it."""
        if not timer.get('running', False):
            return timer.get('total_duration', 0.0)
        
        return time.perf_counter() - timer['start_time']
    
    @staticmethod
    def format_timestamp(timestamp: Optional[float] = None, 
                        format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Format timestamp to human-readable string."""
        if timestamp is None:
            timestamp = time.time()
        
        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.strftime(format_string)
    
    @staticmethod
    def get_day_of_year(timestamp: Optional[float] = None) -> int:
        """Get day of year (1-366) for timestamp."""
        if timestamp is None:
            timestamp = time.time()
        
        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.timetuple().tm_yday
    
    @staticmethod
    def get_week_of_year(timestamp: Optional[float] = None) -> int:
        """Get week of year (1-53) for timestamp."""
        if timestamp is None:
            timestamp = time.time()
        
        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.isocalendar()[1]
    
    @staticmethod
    def is_same_day(timestamp_1: float, timestamp_2: float) -> bool:
        """Check if two timestamps are on the same day."""
        dt1 = datetime.datetime.fromtimestamp(timestamp_1)
        dt2 = datetime.datetime.fromtimestamp(timestamp_2)
        
        return dt1.date() == dt2.date()
    
    @staticmethod
    def get_time_until_midnight() -> float:
        """Get seconds until next midnight."""
        now = datetime.datetime.now()
        tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
        
        return (tomorrow - now).total_seconds()
    
    @staticmethod
    def create_countdown_timer(duration: float) -> Dict[str, Any]:
        """Create a countdown timer."""
        return {
            'start_time': time.perf_counter(),
            'duration': duration,
            'running': True
        }
    
    @staticmethod
    def get_countdown_remaining(countdown: Dict[str, Any]) -> float:
        """Get remaining time on countdown timer."""
        if not countdown.get('running', False):
            return 0.0
        
        elapsed = time.perf_counter() - countdown['start_time']
        remaining = countdown['duration'] - elapsed
        
        return max(0.0, remaining)
    
    @staticmethod
    def is_countdown_expired(countdown: Dict[str, Any]) -> bool:
        """Check if countdown timer has expired."""
        return TimeUtils.get_countdown_remaining(countdown) <= 0.0
    
    @staticmethod
    def get_performance_timestamp() -> float:
        """Get high-precision timestamp for performance measurements."""
        return time.perf_counter()
    
    @staticmethod
    def benchmark_function(func, *args, **kwargs) -> Tuple[Any, float]:
        """Benchmark function execution time."""
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        
        execution_time = end_time - start_time
        return result, execution_time