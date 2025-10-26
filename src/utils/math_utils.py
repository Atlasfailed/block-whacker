"""
Math Utils - Mathematical utility functions with standardized calculations.
Provides common mathematical operations used throughout the game.
"""

import math
import random
from typing import Tuple, List, Union, Optional
from ..core.block_manager import BlockPosition


class MathUtils:
    """
    Mathematical utility functions for game calculations.
    Provides standardized mathematical operations and algorithms.
    """
    
    @staticmethod
    def clamp_value(value: float, min_value: float, max_value: float) -> float:
        """Clamp a value between minimum and maximum bounds."""
        return max(min_value, min(max_value, value))
    
    @staticmethod
    def linear_interpolate(start_value: float, end_value: float, t: float) -> float:
        """Linear interpolation between two values."""
        t = MathUtils.clamp_value(t, 0.0, 1.0)
        return start_value + (end_value - start_value) * t
    
    @staticmethod
    def smooth_step(edge_0: float, edge_1: float, x: float) -> float:
        """Smooth step function for smooth transitions."""
        t = MathUtils.clamp_value((x - edge_0) / (edge_1 - edge_0), 0.0, 1.0)
        return t * t * (3.0 - 2.0 * t)
    
    @staticmethod
    def ease_in_out(t: float) -> float:
        """Ease in-out function for smooth animations."""
        t = MathUtils.clamp_value(t, 0.0, 1.0)
        return t * t * (3.0 - 2.0 * t)
    
    @staticmethod
    def ease_in_cubic(t: float) -> float:
        """Cubic ease-in function."""
        t = MathUtils.clamp_value(t, 0.0, 1.0)
        return t * t * t
    
    @staticmethod
    def ease_out_cubic(t: float) -> float:
        """Cubic ease-out function."""
        t = MathUtils.clamp_value(t, 0.0, 1.0)
        return 1.0 - (1.0 - t) ** 3
    
    @staticmethod
    def calculate_distance(point_1: Tuple[float, float], 
                          point_2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two points."""
        dx = point_2[0] - point_1[0]
        dy = point_2[1] - point_1[1]
        return math.sqrt(dx * dx + dy * dy)
    
    @staticmethod
    def calculate_manhattan_distance(point_1: Tuple[int, int], 
                                   point_2: Tuple[int, int]) -> int:
        """Calculate Manhattan distance between two points."""
        return abs(point_2[0] - point_1[0]) + abs(point_2[1] - point_1[1])
    
    @staticmethod
    def normalize_vector(vector: Tuple[float, float]) -> Tuple[float, float]:
        """Normalize a 2D vector to unit length."""
        x, y = vector
        length = math.sqrt(x * x + y * y)
        
        if length == 0:
            return (0.0, 0.0)
        
        return (x / length, y / length)
    
    @staticmethod
    def rotate_point(point: Tuple[float, float], angle_radians: float, 
                    origin: Tuple[float, float] = (0.0, 0.0)) -> Tuple[float, float]:
        """Rotate a point around an origin by specified angle."""
        cos_angle = math.cos(angle_radians)
        sin_angle = math.sin(angle_radians)
        
        # Translate to origin
        x = point[0] - origin[0]
        y = point[1] - origin[1]
        
        # Rotate
        rotated_x = x * cos_angle - y * sin_angle
        rotated_y = x * sin_angle + y * cos_angle
        
        # Translate back
        return (rotated_x + origin[0], rotated_y + origin[1])
    
    @staticmethod
    def degrees_to_radians(degrees: float) -> float:
        """Convert degrees to radians."""
        return degrees * math.pi / 180.0
    
    @staticmethod
    def radians_to_degrees(radians: float) -> float:
        """Convert radians to degrees."""
        return radians * 180.0 / math.pi
    
    @staticmethod
    def random_float_range(min_value: float, max_value: float) -> float:
        """Generate random float within range."""
        return random.uniform(min_value, max_value)
    
    @staticmethod
    def random_int_range(min_value: int, max_value: int) -> int:
        """Generate random integer within range (inclusive)."""
        return random.randint(min_value, max_value)
    
    @staticmethod
    def random_choice_weighted(choices: List[Tuple[any, float]]) -> any:
        """Choose random item from weighted list."""
        if not choices:
            return None
        
        total_weight = sum(weight for _, weight in choices)
        if total_weight <= 0:
            return random.choice([item for item, _ in choices])
        
        random_value = random.uniform(0, total_weight)
        cumulative_weight = 0
        
        for item, weight in choices:
            cumulative_weight += weight
            if random_value <= cumulative_weight:
                return item
        
        # Fallback to last item
        return choices[-1][0]
    
    @staticmethod
    def calculate_grid_bounds(positions: List[BlockPosition]) -> Tuple[int, int, int, int]:
        """Calculate bounding box for a list of grid positions."""
        if not positions:
            return (0, 0, 0, 0)
        
        min_x = min(pos.x for pos in positions)
        max_x = max(pos.x for pos in positions)
        min_y = min(pos.y for pos in positions)
        max_y = max(pos.y for pos in positions)
        
        return (min_x, min_y, max_x, max_y)
    
    @staticmethod
    def calculate_center_point(positions: List[BlockPosition]) -> Tuple[float, float]:
        """Calculate center point of a list of grid positions."""
        if not positions:
            return (0.0, 0.0)
        
        avg_x = sum(pos.x for pos in positions) / len(positions)
        avg_y = sum(pos.y for pos in positions) / len(positions)
        
        return (avg_x, avg_y)
    
    @staticmethod
    def is_point_in_rectangle(point: Tuple[float, float], 
                             rectangle: Tuple[float, float, float, float]) -> bool:
        """Check if point is inside rectangle (x, y, width, height)."""
        x, y = point
        rect_x, rect_y, rect_width, rect_height = rectangle
        
        return (rect_x <= x <= rect_x + rect_width and 
                rect_y <= y <= rect_y + rect_height)
    
    @staticmethod
    def is_point_in_circle(point: Tuple[float, float], 
                          center: Tuple[float, float], radius: float) -> bool:
        """Check if point is inside circle."""
        distance = MathUtils.calculate_distance(point, center)
        return distance <= radius
    
    @staticmethod
    def calculate_angle_between_points(point_1: Tuple[float, float], 
                                     point_2: Tuple[float, float]) -> float:
        """Calculate angle between two points in radians."""
        dx = point_2[0] - point_1[0]
        dy = point_2[1] - point_1[1]
        return math.atan2(dy, dx)
    
    @staticmethod
    def wrap_angle(angle_radians: float) -> float:
        """Wrap angle to range [-π, π]."""
        while angle_radians > math.pi:
            angle_radians -= 2 * math.pi
        while angle_radians < -math.pi:
            angle_radians += 2 * math.pi
        return angle_radians
    
    @staticmethod
    def calculate_score_multiplier(combo_count: int, level: int) -> float:
        """Calculate score multiplier based on combo and level."""
        # Base multiplier from combo
        combo_multiplier = 1.0 + (combo_count - 1) * 0.5
        
        # Level multiplier
        level_multiplier = 1.0 + (level - 1) * 0.1
        
        # Combined multiplier with diminishing returns
        combined = combo_multiplier * level_multiplier
        
        # Apply logarithmic scaling to prevent explosive growth
        if combined > 5.0:
            combined = 5.0 + math.log(combined - 4.0)
        
        return combined
    
    @staticmethod
    def calculate_level_from_score(score: int) -> int:
        """Calculate level based on current score."""
        if score <= 0:
            return 1
        
        # Level increases every 10,000 points with slight acceleration
        base_level = score // 10000
        bonus_level = int(math.sqrt(score / 50000))  # Bonus from high scores
        
        return max(1, base_level + bonus_level + 1)
    
    @staticmethod
    def calculate_drop_speed(level: int) -> float:
        """Calculate block drop speed based on level."""
        # Base speed increases with level, with diminishing returns
        base_speed = 1.0 + (level - 1) * 0.3
        
        # Apply logarithmic scaling to prevent excessive speed
        if base_speed > 10.0:
            base_speed = 10.0 + math.log(base_speed - 9.0)
        
        return base_speed
    
    @staticmethod
    def calculate_time_bonus(time_remaining: float, max_time: float) -> int:
        """Calculate time bonus for timed game modes."""
        if max_time <= 0 or time_remaining <= 0:
            return 0
        
        time_ratio = time_remaining / max_time
        
        # Exponential bonus for finishing quickly
        bonus = int(1000 * time_ratio * time_ratio)
        
        return max(0, bonus)
    
    @staticmethod
    def calculate_fibonacci_sequence(n: int) -> List[int]:
        """Calculate Fibonacci sequence up to n terms."""
        if n <= 0:
            return []
        elif n == 1:
            return [0]
        elif n == 2:
            return [0, 1]
        
        sequence = [0, 1]
        for i in range(2, n):
            sequence.append(sequence[i-1] + sequence[i-2])
        
        return sequence
    
    @staticmethod
    def is_prime(number: int) -> bool:
        """Check if a number is prime."""
        if number < 2:
            return False
        if number == 2:
            return True
        if number % 2 == 0:
            return False
        
        for i in range(3, int(math.sqrt(number)) + 1, 2):
            if number % i == 0:
                return False
        
        return True
    
    @staticmethod
    def gcd(a: int, b: int) -> int:
        """Calculate Greatest Common Divisor."""
        while b:
            a, b = b, a % b
        return abs(a)
    
    @staticmethod
    def lcm(a: int, b: int) -> int:
        """Calculate Least Common Multiple."""
        return abs(a * b) // MathUtils.gcd(a, b) if a and b else 0
    
    @staticmethod
    def calculate_percentage(value: float, total: float) -> float:
        """Calculate percentage with safe division."""
        if total == 0:
            return 0.0
        return (value / total) * 100.0
    
    @staticmethod
    def round_to_nearest(value: float, nearest: float) -> float:
        """Round value to nearest specified increment."""
        if nearest == 0:
            return value
        return round(value / nearest) * nearest
    
    @staticmethod
    def sign(value: float) -> int:
        """Get sign of a number (-1, 0, or 1)."""
        if value > 0:
            return 1
        elif value < 0:
            return -1
        else:
            return 0