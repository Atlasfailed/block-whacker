"""
Color Utils - Color manipulation and utility functions with standardized color handling.
Provides comprehensive color operations for the game's visual elements.
"""

import colorsys
import random
from typing import Tuple, List, Optional, Union


class ColorUtils:
    """
    Color utility functions for color manipulation and generation.
    Provides standardized color operations and conversions.
    """
    
    # Standard color constants
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    
    @staticmethod
    def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hexadecimal string."""
        r, g, b = rgb
        return f"#{r:02x}{g:02x}{b:02x}"
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Convert hexadecimal string to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        
        if len(hex_color) == 3:
            # Short format (e.g., "abc" -> "aabbcc")
            hex_color = ''.join([c*2 for c in hex_color])
        
        if len(hex_color) != 6:
            raise ValueError(f"Invalid hex color format: {hex_color}")
        
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def rgb_to_hsv(rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
        """Convert RGB to HSV color space."""
        r, g, b = [c / 255.0 for c in rgb]
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        return (h * 360.0, s * 100.0, v * 100.0)  # Convert to degrees and percentages
    
    @staticmethod
    def hsv_to_rgb(hsv: Tuple[float, float, float]) -> Tuple[int, int, int]:
        """Convert HSV to RGB color space."""
        h, s, v = hsv[0] / 360.0, hsv[1] / 100.0, hsv[2] / 100.0  # Normalize
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return (int(r * 255), int(g * 255), int(b * 255))
    
    @staticmethod
    def rgb_to_hsl(rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
        """Convert RGB to HSL color space."""
        r, g, b = [c / 255.0 for c in rgb]
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        return (h * 360.0, s * 100.0, l * 100.0)  # Convert to degrees and percentages
    
    @staticmethod
    def hsl_to_rgb(hsl: Tuple[float, float, float]) -> Tuple[int, int, int]:
        """Convert HSL to RGB color space."""
        h, s, l = hsl[0] / 360.0, hsl[1] / 100.0, hsl[2] / 100.0  # Normalize
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return (int(r * 255), int(g * 255), int(b * 255))
    
    @staticmethod
    def lighten_color(rgb: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
        """Lighten a color by specified factor (0.0 to 1.0)."""
        factor = max(0.0, min(1.0, factor))
        
        # Convert to HSL, increase lightness, convert back
        h, s, l = ColorUtils.rgb_to_hsl(rgb)
        l = min(100.0, l + (100.0 - l) * factor)
        
        return ColorUtils.hsl_to_rgb((h, s, l))
    
    @staticmethod
    def darken_color(rgb: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
        """Darken a color by specified factor (0.0 to 1.0)."""
        factor = max(0.0, min(1.0, factor))
        
        # Convert to HSL, decrease lightness, convert back
        h, s, l = ColorUtils.rgb_to_hsl(rgb)
        l = max(0.0, l - l * factor)
        
        return ColorUtils.hsl_to_rgb((h, s, l))
    
    @staticmethod
    def saturate_color(rgb: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
        """Increase color saturation by specified factor (0.0 to 1.0)."""
        factor = max(0.0, min(1.0, factor))
        
        # Convert to HSL, increase saturation, convert back
        h, s, l = ColorUtils.rgb_to_hsl(rgb)
        s = min(100.0, s + (100.0 - s) * factor)
        
        return ColorUtils.hsl_to_rgb((h, s, l))
    
    @staticmethod
    def desaturate_color(rgb: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
        """Decrease color saturation by specified factor (0.0 to 1.0)."""
        factor = max(0.0, min(1.0, factor))
        
        # Convert to HSL, decrease saturation, convert back
        h, s, l = ColorUtils.rgb_to_hsl(rgb)
        s = max(0.0, s - s * factor)
        
        return ColorUtils.hsl_to_rgb((h, s, l))
    
    @staticmethod
    def blend_colors(color_1: Tuple[int, int, int], color_2: Tuple[int, int, int], 
                    factor: float) -> Tuple[int, int, int]:
        """Blend two colors with specified factor (0.0 = color1, 1.0 = color2)."""
        factor = max(0.0, min(1.0, factor))
        
        r = int(color_1[0] + (color_2[0] - color_1[0]) * factor)
        g = int(color_1[1] + (color_2[1] - color_1[1]) * factor)
        b = int(color_1[2] + (color_2[2] - color_1[2]) * factor)
        
        return (r, g, b)
    
    @staticmethod
    def get_complementary_color(rgb: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Get complementary color (opposite on color wheel)."""
        h, s, l = ColorUtils.rgb_to_hsl(rgb)
        h = (h + 180.0) % 360.0  # Rotate 180 degrees
        
        return ColorUtils.hsl_to_rgb((h, s, l))
    
    @staticmethod
    def get_analogous_colors(rgb: Tuple[int, int, int], 
                           angle: float = 30.0) -> List[Tuple[int, int, int]]:
        """Get analogous colors (adjacent on color wheel)."""
        h, s, l = ColorUtils.rgb_to_hsl(rgb)
        
        # Generate colors at ±angle degrees
        h1 = (h - angle) % 360.0
        h2 = (h + angle) % 360.0
        
        return [
            ColorUtils.hsl_to_rgb((h1, s, l)),
            rgb,  # Original color
            ColorUtils.hsl_to_rgb((h2, s, l))
        ]
    
    @staticmethod
    def get_triadic_colors(rgb: Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
        """Get triadic colors (120 degrees apart on color wheel)."""
        h, s, l = ColorUtils.rgb_to_hsl(rgb)
        
        h1 = (h + 120.0) % 360.0
        h2 = (h + 240.0) % 360.0
        
        return [
            rgb,  # Original color
            ColorUtils.hsl_to_rgb((h1, s, l)),
            ColorUtils.hsl_to_rgb((h2, s, l))
        ]
    
    @staticmethod
    def get_color_palette(base_color: Tuple[int, int, int], 
                         count: int = 5) -> List[Tuple[int, int, int]]:
        """Generate a color palette based on a base color."""
        if count <= 1:
            return [base_color]
        
        h, s, l = ColorUtils.rgb_to_hsl(base_color)
        palette = []
        
        # Generate colors by varying hue
        hue_step = 360.0 / count
        
        for i in range(count):
            new_h = (h + i * hue_step) % 360.0
            palette.append(ColorUtils.hsl_to_rgb((new_h, s, l)))
        
        return palette
    
    @staticmethod
    def generate_random_color(saturation_range: Tuple[float, float] = (50.0, 100.0),
                            lightness_range: Tuple[float, float] = (30.0, 80.0)) -> Tuple[int, int, int]:
        """Generate a random color with specified saturation and lightness ranges."""
        h = random.uniform(0.0, 360.0)
        s = random.uniform(saturation_range[0], saturation_range[1])
        l = random.uniform(lightness_range[0], lightness_range[1])
        
        return ColorUtils.hsl_to_rgb((h, s, l))
    
    @staticmethod
    def generate_gradient(color_1: Tuple[int, int, int], color_2: Tuple[int, int, int], 
                         steps: int) -> List[Tuple[int, int, int]]:
        """Generate a gradient between two colors with specified steps."""
        if steps <= 1:
            return [color_1]
        
        gradient = []
        
        for i in range(steps):
            factor = i / (steps - 1)
            blended_color = ColorUtils.blend_colors(color_1, color_2, factor)
            gradient.append(blended_color)
        
        return gradient
    
    @staticmethod
    def get_luminance(rgb: Tuple[int, int, int]) -> float:
        """Calculate relative luminance of a color (0.0 to 1.0)."""
        # Convert to linear RGB
        def linear_component(c):
            c = c / 255.0
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        
        r, g, b = [linear_component(c) for c in rgb]
        
        # Calculate luminance using ITU-R BT.709 coefficients
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    @staticmethod
    def get_contrast_ratio(color_1: Tuple[int, int, int], 
                          color_2: Tuple[int, int, int]) -> float:
        """Calculate contrast ratio between two colors."""
        l1 = ColorUtils.get_luminance(color_1)
        l2 = ColorUtils.get_luminance(color_2)
        
        # Ensure lighter color is in numerator
        if l1 < l2:
            l1, l2 = l2, l1
        
        return (l1 + 0.05) / (l2 + 0.05)
    
    @staticmethod
    def is_accessible_contrast(color_1: Tuple[int, int, int], 
                              color_2: Tuple[int, int, int],
                              level: str = 'AA') -> bool:
        """Check if color combination meets accessibility contrast requirements."""
        contrast_ratio = ColorUtils.get_contrast_ratio(color_1, color_2)
        
        if level.upper() == 'AAA':
            return contrast_ratio >= 7.0
        else:  # AA level
            return contrast_ratio >= 4.5
    
    @staticmethod
    def get_readable_text_color(background_color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Get black or white text color that's most readable on given background."""
        luminance = ColorUtils.get_luminance(background_color)
        
        # Use white text on dark backgrounds, black text on light backgrounds
        return ColorUtils.WHITE if luminance < 0.5 else ColorUtils.BLACK
    
    @staticmethod
    def clamp_rgb(rgb: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Clamp RGB values to valid range (0-255)."""
        return tuple(max(0, min(255, c)) for c in rgb)
    
    @staticmethod
    def rgb_to_grayscale(rgb: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Convert RGB color to grayscale using luminance weights."""
        r, g, b = rgb
        gray_value = int(0.299 * r + 0.587 * g + 0.114 * b)
        return (gray_value, gray_value, gray_value)
    
    @staticmethod
    def apply_gamma_correction(rgb: Tuple[int, int, int], gamma: float) -> Tuple[int, int, int]:
        """Apply gamma correction to RGB color."""
        corrected = tuple(int(255 * ((c / 255.0) ** gamma)) for c in rgb)
        return ColorUtils.clamp_rgb(corrected)
    
    @staticmethod
    def color_distance(color_1: Tuple[int, int, int], 
                      color_2: Tuple[int, int, int]) -> float:
        """Calculate Euclidean distance between two colors in RGB space."""
        r_diff = color_2[0] - color_1[0]
        g_diff = color_2[1] - color_1[1]
        b_diff = color_2[2] - color_1[2]
        
        return (r_diff ** 2 + g_diff ** 2 + b_diff ** 2) ** 0.5
    
    @staticmethod
    def find_closest_color(target_color: Tuple[int, int, int], 
                          color_palette: List[Tuple[int, int, int]]) -> Tuple[int, int, int]:
        """Find the closest color in a palette to the target color."""
        if not color_palette:
            return target_color
        
        closest_color = color_palette[0]
        closest_distance = ColorUtils.color_distance(target_color, closest_color)
        
        for color in color_palette[1:]:
            distance = ColorUtils.color_distance(target_color, color)
            if distance < closest_distance:
                closest_distance = distance
                closest_color = color
        
        return closest_color